from datetime import datetime, timedelta
from typing import Optional

import cbpro


class Strategy:
    MAX_CANDLES = 300  # as per get_product_historic_rates docs
    ALLOWED_GRANULARITIES = [60, 300, 900, 3600, 21600,
                             86400]  # from api error message

    def __init__(self, client: cbpro.AuthenticatedClient):
        self.client = client

    def run(self):
        pass

    def historical_data(self,
                        ticker: str,
                        start: Optional[datetime] = None,
                        end: Optional[datetime] = None) -> list[list[float]]:
        # default to last 2 weeks if timeframe is not specified
        end = end or datetime.now()
        start = start or end - timedelta(hours=2)
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
