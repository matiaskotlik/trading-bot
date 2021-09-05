from datetime import timedelta
from main import run_strategy
from trader import Side, Trader
from downloader import Downloader
from strategy import Parameter, Strategy


class StupidStrategy(Strategy):
    """Example strategy that buys an asset and sells it after a certain period of time"""
    ASSET = 'DOGE-USD'  # trade DOGE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters['sell_delay_seconds'] = Parameter(60 * 60 * 24, 30, 60 * 60 * 24)

    def download_data(self, downloader: Downloader):
        pass

    def trade(self, trader: Trader):
        trader.place_market_order(self.ASSET, Side.BUY)  # buy all
        wait_time_seconds = self.parameters['sell_delay_seconds'].get_value()
        trader.wait(timedelta(seconds=wait_time_seconds))
        trader.place_market_order(self.ASSET, Side.SELL)  # sell all


if __name__ == '__main__':
    run_strategy(StupidStrategy)