from datetime import datetime
from typing import Callable

import colorama
from dotenv import load_dotenv

import api
from downloader import Downloader
from strategy import Strategy
from trader import Trader


def run_strategy(strategy_builder: Callable[[datetime], Strategy]):
    load_dotenv()
    colorama.init()

    client = api.connect()
    downloader = Downloader(client)
    trader = Trader(client)

    time = datetime(2021, 9, 4)

    strategy: Strategy = strategy_builder(time)

    print('Downloading data...')
    strategy.download_data(downloader)

    print('Trading...')
    strategy.trade(trader)

    print('Done!')


if __name__ == '__main__':
    pass
