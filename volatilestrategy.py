from datetime import datetime, timedelta
from pprint import pprint

from downloader import Downloader
from main import run_strategy
from strategy import Strategy
from trader import OrderType, Side, Trader


class VolatileStrategy(Strategy):
    """A strategy that finds volatile assets and does grid trading on them"""
    def trade(self, trader: Trader):
        product = self.find_volatile_tickers()[0]['id']
        # buy $10 of the most volatile product
        trader.place_order(product,
                           side=Side.BUY,
                           order_type=OrderType.MARKET,
                           price=10)

    def download_data(self, downloader: Downloader):
        start = self.start_time - timedelta(hours=1)
        end = self.start_time

        self.products = [
            p for p in downloader.product_list() if p['id'].endswith('-USD')
        ]  # filter only USD pairs

        self.product_data = {
            p['id']: downloader.historical_data(p['id'], start, end)
            for p in self.products
        }

    def find_volatile_tickers(self):
        """Returns a list of assets sorted by volatility over the last our of trading"""
        product_variance = [{
            'id': p['id'],
            'volatility': self.calculate_product_volatility(p)
        } for p in self.products]
        product_variance.sort(key=lambda p: p['volatility'], reverse=True)
        return product_variance

    def calculate_product_volatility(self, product: dict[str, str]) -> float:
        data = self.product_data[product['id']]
        return self.avg_percent_volatility(data)
        # return self.avg_close_price_percent_diff(data)


if __name__ == '__main__':
    run_strategy(VolatileStrategy)
