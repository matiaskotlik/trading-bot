from collections import OrderedDict
from datetime import datetime, timedelta
import math
from trader import Trader
from downloader import Downloader
from symbol import parameters
from genetic import Agent, Gene
import statistics
from typing import Optional

from cbpro import AuthenticatedClient as CBProClient


class Parameter:
    """Strategy parameter with output in the range [min_value, max_value)"""
    DEFAULT_RANGE_PERCENTAGE = 0.5

    def __init__(self,
                 initial_value: float,
                 min_val: Optional[float] = None,
                 max_val: Optional[float] = None):
        default_range = (initial_value * self.DEFAULT_RANGE_PERCENTAGE)
        self.min = min_val or initial_value - default_range
        self.max = max_val or initial_value + default_range
        self.value = (initial_value - self.min) / (self.max - self.min)

        # make sure difference between initial_value and the result of get_value() is negligible
        assert math.isclose(initial_value, self.get_value())

    def get_value(self) -> float:
        """Get the value of the parameter"""
        return self.min + self.value * (self.max - self.min)


class IntParameter(Parameter):
    """Strategy parameter where output is an integer in the range [min_value, max_value)"""
    def get_value(self) -> int:
        return int(super().get_value())


class Strategy:
    def __init__(self, start_time: Optional[datetime] = None):
        self.start_time = start_time or datetime.now()
        self.parameters: OrderedDict[str, Parameter] = {}

    def download_data(self, downloader: Downloader):
        raise NotImplementedError

    def trade(self, trader: Trader):
        raise NotImplementedError

    def create_agent_from_parameters(self) -> Agent:
        return Agent([Gene(param.value) for param in self.parameters.values()])

    def update_parameters_from_agent(self, agent: Agent):
        for (gene, param) in zip(agent.genes, parameters.values()):
            param.value = gene.value
    
    def print_parameters(self):
        for name, param in parameters.items():
            print(f'{name:10.10}: {param.value}')

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
