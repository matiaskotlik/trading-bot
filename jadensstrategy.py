from datetime import timedelta
from main import run_strategy
from trader import Side, Trader
from downloader import Downloader
from strategy import Parameter, Strategy
from decimal import Decimal


class JadensStategy(Strategy):
    def download_data(self, downloader: Downloader):
        pass

    def trade(self, trader: Trader):
        trader.place_market_order("ETH-USD", Side.BUY, Decimal(0.1))
        intial_price = trader.get_product_price("ETH-USD")
        while True:
            trader.wait(timedelta(hours=1))
            new_price = trader.get_product_price("ETH-USD")
            if new_price >= intial_price:
                trader.place_market_order("ETH-USD", Side.SELL, Decimal(1))
                break


if __name__ == '__main__':
    run_strategy(JadensStategy)