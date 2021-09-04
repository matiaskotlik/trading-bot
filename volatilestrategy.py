import statistics
from datetime import datetime, timedelta
from pprint import pprint
from typing import Optional

from dotenv import load_dotenv

from main import run_strategy
from strategy import Strategy


class VolatileStrategy(Strategy):
    """A strategy that finds volatile assets and does grid trading on them"""

    def run(self):
        pprint(self.find_volatile_tickers())

    def find_volatile_tickers(self):
        """Returns a list of assets sorted by volatility"""
        now = datetime.now()
        start = now - timedelta(hours=1)
        end = now
        products = [
            p for p in self.client.get_products() if p['id'].endswith('-USD')
        ]  # get all USD exchanges
        product_variance = [
            {
                'id': p['id'],
                'variance': self.avg_percent_volatility(p['id'], start, end)
                # 'variance': self.avg_close_price_percent_diff(p['id'], start, end)
            } for p in products
        ]
        product_variance.sort(key=lambda p: p['variance'], reverse=True)
        return product_variance

    def avg_close_price_percent_diff(self,
                                     ticker: str,
                                     start: Optional[datetime] = None,
                                     end: Optional[datetime] = None):
        """Calculate average close price percent difference"""
        data = self.historical_data(ticker, start, end)
        prices = [p['close'] for p in data]
        # calculate percentage difference of each closing price compared to last
        percent_change = [
            abs((value - benchmark) / benchmark)
            for benchmark, value in zip(prices, prices[1:])
        ]
        # calculate average % difference
        return statistics.mean(percent_change)

    def avg_percent_volatility(self,
                               ticker: str,
                               start: Optional[datetime] = None,
                               end: Optional[datetime] = None):
        """Calculate average percent volatility"""
        data = self.historical_data(ticker, start, end)
        percent_volatility = [
            (p['high'] - p['low']) / ((p['high'] + p['low'] / 2)) for p in data
        ]
        return statistics.mean(percent_volatility)


if __name__ == '__main__':
    run_strategy(VolatileStrategy)
