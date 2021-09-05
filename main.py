from datetime import datetime
from typing import Callable

import colorama
from dotenv import load_dotenv

import api
from downloader import Downloader
from strategy import Strategy
from trader import TestTrader


def run_strategy(strategy_builder: Callable[[datetime], Strategy]):
    load_dotenv()
    colorama.init()

    client = api.connect()
    time = datetime(2021, 9, 3)
    # time = datetime.now()
    downloader = Downloader(client)
    trader = TestTrader(client, usd=100, time=time)

    strategy: Strategy = strategy_builder(time)

    print('Downloading data...')
    strategy.download_data(downloader)

    print('Trading...\n')
    trader.show_portfolio()
    strategy.trade(trader)
    trader.show_portfolio()


if __name__ == '__main__':
    pass
