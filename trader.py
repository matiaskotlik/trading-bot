from asyncio import LimitOverrunError
import math
from tabulate import tabulate
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from fileinput import close
from typing import Literal, Optional
from xmlrpc.client import Boolean

import colorama
from cbpro import AuthenticatedClient as CBProClient
from colorama import Back, Fore, Style

from utils import sign


class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'


class OrderType(Enum):
    LIMIT = 'limit'
    MARKET = 'market'
    STOP = 'stop'


class OrderStatus(Enum):
    PLACED = 1
    FILLED = 2
    CANCEL = 3


class Trader:
    def __init__(self, client: CBProClient, usd: float, log=True):
        self.client = client
        self.balance = {'USD': Decimal(usd)}
        self.log = log

    def log_order(self, coin_name: str, currency_name: str, side: Side,
                  order_type: OrderType, order_status: OrderStatus,
                  price: float, size: float, unit_price: float,
                  fee_amount: float, order_time: datetime, is_real: Boolean):
        if not self.log:
            return

        # format:
        # [TIME] [TYPE ORDER PLACED|FILLED|CANCELLED] +- 12.34 COIN +- $12.3456 USD @ $12.3456 USD / COIN
        l = Fore.WHITE + '['
        r = Fore.WHITE + ']'

        time = Fore.RED if is_real else Fore.WHITE
        time += order_time.strftime('%m-%d-%y %H:%M:%S')

        order = {
            OrderStatus.PLACED: Fore.YELLOW,
            OrderStatus.FILLED: Fore.GREEN,
            OrderStatus.CANCEL: Fore.RED
        }[order_status]
        order += f'{order_type.name} ORDER {order_status.name}'
        order = l + order + r

        coin = f'{Fore.GREEN}+ ' if side == Side.BUY else f'{Fore.RED}- '
        coin += f'{size!s:18.18} {coin_name:5.5}'

        currency = f'{Fore.RED}- ' if side == Side.BUY else f'{Fore.GREEN}+ '
        currency += f'${price!s:18.18} {currency_name:5.5}'

        fee = Fore.RED if (fee_amount) else Fore.WHITE
        fee += f'F${fee_amount:2.2f}'

        unit = f'{Fore.WHITE}@ ${unit_price:.7f} {currency_name} / {coin_name}'

        print(f'{l}{time}{r} {order} {fee} {coin} {currency} {unit}')

    def log_portfolio(self):
        raise NotImplementedError

    def place_market_order(self, product_id: str, side: Side,
                           percentage: float):
        raise NotImplementedError

    def wait(self, delta: timedelta):
        raise NotImplementedError


class TestTrader(Trader):
    def get_product_price(self, product_id) -> Decimal:
        now = datetime.now()
        if now < self.time:
            raise ValueError("self.time is in the future")
        min_difference = timedelta(minutes=1, seconds=1)
        if self.time and min_difference < now - self.time:
            historical_data = self.client.get_product_historic_rates(
                product_id, start=self.time, end=self.time, granularity=60)[0]
            unit_price = Decimal(historical_data[4])  # close price
        else:
            product_info = self.client.get_product_ticker(product_id)
            unit_price = Decimal(product_info['price'])
        return unit_price
    COINBASE_FEE = Decimal(0.005)

    def __init__(self,
                 client: CBProClient,
                 usd: float,
                 time: Optional[datetime] = None,
                 log=True):
        self.client = client
        self.time = time
        self.balance = defaultdict(Decimal)
        self.balance['USD'] = Decimal(usd)
        self.log = log

    def get_asset_price(self, asset):
        if asset == 'USD':
            return Decimal(1)
        product = f'{asset}-USD'
        info = self.client.get_product_ticker(product)
        return Decimal(info['price'])

    def portfolio_value(self):
        total = 0
        for (asset, quantity) in self.balance.items():
            unit_price = self.get_asset_price(asset)
            value = unit_price * quantity
            total += value
        return total

    def show_portfolio(self):
        table = []
        total = self.portfolio_value()
        for (asset, quantity) in self.balance.items():
            if quantity == 0:
                continue

            unit_price = self.get_asset_price(asset)
            value = unit_price * quantity
            table.append([
                asset, f'{value / total:.2%}', f'${value:.2f}', quantity,
                f'${unit_price:.2f}'
            ])

        print(f'Total Portfolio Value: ${total:.2f} USD')
        print('Breakdown:')
        headers = ['Asset', 'Holdings', 'Value', 'Quantity', 'Price']
        print(tabulate(table, headers=headers))

    def wait(self, delta: timedelta):
        self.time += delta
        print(f'{Fore.CYAN}-- WAIT SIMULATION: {delta} --')

    def place_market_order(self,
                           product_id: str,
                           side: Side,
                           percentage: Decimal = Decimal(1)):
        """
        Buy or sell an asset at the current market price.
        When buying, percentage is the amount of currency to spend on the asset.
        When selling, percentage is the amount of the asset to sell.
        """
        # get some product info
        now = datetime.now()
        if now < self.time:
            raise ValueError("self.time is in the future")

        min_difference = timedelta(minutes=1, seconds=1)
        if self.time and min_difference < now - self.time:
            historical_data = self.client.get_product_historic_rates(
                product_id, start=self.time, end=self.time, granularity=60)[0]
            unit_price = Decimal(historical_data[4])  # close price
        else:
            product_info = self.client.get_product_ticker(product_id)
            unit_price = Decimal(product_info['price'])

        # format for product_id is 'BTC-USD'
        # figure out which asset we are selling and which we are buying
        coin_name, curr_name = product_id.split('-')
        if side == Side.BUY:
            # buying: curr --> coin
            from_currency, to_currency = curr_name, coin_name
        if side == Side.SELL:
            # selling: coin --> curr
            from_currency, to_currency = coin_name, curr_name

        # calculate how much actual currency we are buying/selling, using percentage.
        from_amount = self.balance[from_currency] * percentage
        if side == Side.BUY:
            # # of coins == $ / unit price
            from_amount -= from_amount * self.COINBASE_FEE
            to_amount = from_amount / unit_price
            price = from_amount
            size = to_amount
        else:
            # $ = # of coins * unit price
            to_amount = from_amount * unit_price
            to_amount -= self.COINBASE_FEE
            price = to_amount
            size = from_amount

        if price <= 0:
            raise ValueError("order price is <= 0")

        if size <= 0:
            raise ValueError("order size is <= 0")

        # simulate purchase
        fee = price * self.COINBASE_FEE
        self.balance[curr_name] -= fee
        self.balance[from_currency] -= from_amount
        self.balance[to_currency] += to_amount

        self.log_order(coin_name=coin_name,
                       currency_name=curr_name,
                       side=side,
                       order_status=OrderStatus.PLACED,
                       order_type=OrderType.MARKET,
                       price=price,
                       size=size,
                       unit_price=unit_price,
                       fee_amount=0,
                       order_time=self.time or datetime.now(),
                       is_real=False)

        self.log_order(coin_name=coin_name,
                       currency_name=curr_name,
                       side=side,
                       order_status=OrderStatus.FILLED,
                       order_type=OrderType.MARKET,
                       price=price,
                       size=size,
                       unit_price=unit_price,
                       fee_amount=fee,
                       order_time=self.time or datetime.now(),
                       is_real=False)
    

class CoinbaseTrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.time:
            raise ValueError(
                "CoinbaseTrader can only operate in realtime mode")


def split(n: int):
    for i in range(n, 0, -1):
        yield 1 / i