from datetime import datetime, timedelta
from trader import Trader
from downloader import Downloader
from symbol import parameters
from genetic import Gene
import statistics
from typing import Optional

from cbpro import AuthenticatedClient as CBProClient


class Parameter:
    """Strategy parameter with output in the range [min_value, max_value)"""
    def __init__(self, min_val: float, max_val: float):
        self.min = min_val
        self.max = max_val

    def get_value(self, gene: Gene):
        return self.min + gene.value * (self.max - self.min)


class IntParameter(Parameter):
    """Strategy parameter where output is an integer in the range [min_value, max_value)"""
    def get_value(self, gene: Gene):
        return int(super().get_value(gene))


class Strategy:
    def __init__(self, now: Optional[datetime] = None):
        self.now = now or datetime.now()
        self.parameters: list[Parameter] = []

    def download_data(self, downloader: Downloader):
        raise NotImplementedError

    def trade(self, trader: Trader):
        raise NotImplementedError

    def add_parameter(self, p: Parameter) -> Parameter:
        self.parameters.append(p)
        return p

    def avg_close_price_percent_diff(
            self, historical_data: list[dict[str, float]]) -> float:
        """Calculate average close price percent difference"""
        prices = [p['close'] for p in historical_data]
        # calculate percentage difference of each closing price compared to last
        percent_change = [
            abs((value - benchmark) / benchmark)
            for benchmark, value in zip(prices, prices[1:])
        ]
        # calculate average percent difference
        return statistics.mean(percent_change)

    def avg_percent_volatility(
            self, historical_data: list[dict[str, float]]) -> float:
        """Calculate average percent volatility"""
        percent_volatility = [
            (p['high'] - p['low']) / ((p['high'] + p['low'] / 2))
            for p in historical_data
        ]
        return statistics.mean(percent_volatility)
