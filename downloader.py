from datetime import datetime, timedelta
from utils import memoize_diskcache
from definitions import ROOT_DIR
from functools import wraps

import diskcache
from cbpro import AuthenticatedClient as CBProClient

cache = diskcache.Cache(ROOT_DIR / 'cache')

class Downloader:
    MAX_CANDLES = 300  # as per get_product_historic_rates docs
    ALLOWED_GRANULARITIES = [60, 300, 900, 3600, 21600,
                             86400]  # from api error message

    def __init__(self, client: CBProClient):
        self.client = client

    @memoize_diskcache(cache)
    def product_list(self) -> list[dict[str, str]]:
        return self.client.get_products()

    # TODO improved historical data cache
    @memoize_diskcache(cache)
    def historical_data(self, ticker: str, start: datetime,
                        end: datetime) -> list[dict[str, float]]:
        duration = end - start

        # can't have more than MAX_CANDLES datapoints
        min_granularity = duration.total_seconds() / self.MAX_CANDLES

        # get the lowest allowed granularity that isn't > max_granularity
        valid_granularities = [
            g for g in self.ALLOWED_GRANULARITIES if g >= min_granularity
        ]
        if not valid_granularities:
            raise RuntimeError("Period is too large")
        granularity = valid_granularities[0]

        return [{
            'time': time,
            'low': low,
            'high': high,
            'open': open_price,
            'close': close,
            'volume': volume
        } for time, low, high, open_price, close, volume
                in self.client.get_product_historic_rates(
                    ticker, start.isoformat(), end.isoformat(), granularity)]
