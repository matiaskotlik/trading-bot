import os

import cbpro
from dotenv import load_dotenv

import api

load_dotenv()

client = api.connect()

accounts = client.get_accounts()
print(accounts)