from datetime import datetime, timedelta
from pprint import pprint

from main import run_strategy
from strategy import Strategy


class VolatileStrategy(Strategy):
    """A strategy that finds volatile assets and does grid trading on them"""
    def run(self):
        pprint(self.find_volatile_tickers())

    def find_volatile_tickers(self):
        """Returns a list of assets sorted by volatility over the last our of trading"""
        now = datetime.now()
        start = now - timedelta(hours=1)
        end = now
        products = [
            p for p in self.client.get_products() if p['id'].endswith('-USD')
        ]  # filter only USD pairs
        product_variance = [
            {
                'id': p['id'],
                'variance': self.avg_percent_volatility(p['id'], start, end)
                # 'variance': self.avg_close_price_percent_diff(p['id'], start, end)
            } for p in products
        ]
        product_variance.sort(key=lambda p: p['variance'], reverse=True)
        return product_variance


if __name__ == '__main__':
    run_strategy(VolatileStrategy)
