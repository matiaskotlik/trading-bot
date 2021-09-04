from dotenv import load_dotenv

import api


def run_strategy(strategy_builder):
    load_dotenv()
    client = api.connect()
    strategy = strategy_builder(client)
    strategy.run()


if __name__ == '__main__':
    pass
