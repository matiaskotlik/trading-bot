from http import client
import os
import statistics
from datetime import datetime, timedelta
from math import ceil
from pprint import pprint
from strategy import Strategy
from typing import Optional

import cbpro
from dotenv import load_dotenv

import api


def run_strategy(strategy_builder):
    load_dotenv()  # todo this should probably be in main() aswell
    client = api.connect()
    strategy = strategy_builder(client)
    strategy.run()


if __name__ == '__main__':
    pass
