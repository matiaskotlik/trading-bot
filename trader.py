from asyncio import LimitOverrunError
from datetime import datetime
from fileinput import close
from utils import sign
from colorama import Fore, Back, Style
import colorama
from typing import Literal, Optional
from enum import Enum

from cbpro import AuthenticatedClient as CBProClient


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
    CANCELLED = 3


class Trader:
    def __init__(self, client: CBProClient, log=True):
        self.client = client

    def log_order(self,
                  product: str,
                  side: Side,
                  order_type: OrderType,
                  order_status: OrderStatus,
                  price: float,
                  size: float,
                  unit_price: float,
                  order_time: Optional[datetime] = None):
        # format:
        # [TIME] [TYPE ORDER PLACED|FILLED|CANCELLED] +- 12.34 COIN +- $12.3456 USD @ $12.3456 USD / COIN
        coin, curr = product.split('-')

        if order_time:
            time = Fore.WHITE + order_time.strftime('%m-%d-%y %H:%M:%S')
        else:
            time = Fore.RED + 'REALTIME'

        order = {
            OrderStatus.PLACED: Fore.YELLOW,
            OrderStatus.FILLED: Fore.GREEN,
            OrderStatus.CANCELLED: Fore.RED
        }[order_status]
        order += f'{order_type.name} ORDER {order_status.name}'

        lhs = f'{Fore.GREEN}+ ' if side == Side.BUY else f'{Fore.RED}- '
        lhs += f'{size} {coin}'

        rhs = f'{Fore.RED}- ' if side == Side.BUY else f'{Fore.GREEN}+ '
        rhs += f'${price} {curr}'

        unit = f'{Fore.WHITE}@ ${unit_price} {curr} / {coin}'

        l = Fore.WHITE + '['
        r = Fore.WHITE + ']'
        print(f'{l}{time}{r} {l}{order}{r} {lhs} {rhs} {unit}')

    def place_order(self,
                    product_id: str,
                    side: Side,
                    order_type: OrderType,
                    price: Optional[float] = None,
                    size: Optional[float] = None,
                    time=Optional[datetime]):
        product_info = self.client.get_product_ticker(product_id)
        unit_price = float(product_info['price'])
        if order_type == OrderType.MARKET:
            if size and not price:
                price = size * unit_price
            if price and not size:
                size = price / unit_price
        self.log_order(product=product_id,
                       side=side,
                       order_type=order_type,
                       order_status=OrderStatus.PLACED,
                       price=price,
                       size=size,
                       unit_price=unit_price,
                       order_time=time)
        pass


class TestTrader(Trader):
    pass


class CoinbaseTrader(Trader):
    pass