import os

import cbpro


def connect() -> cbpro.AuthenticatedClient:
    """Authenticate to the cbpro API"""

    API_KEY = os.getenv('API_KEY')
    if API_KEY == None:
        raise RuntimeError("API_KEY environment variable is not set")

    API_SECRET = os.getenv('API_SECRET')
    if API_SECRET == None:
        raise RuntimeError("API_SECRET environment variable is not set")

    API_PASSCODE = os.getenv('API_PASSCODE')
    if API_PASSCODE == None:
        raise RuntimeError("API_PASSCODE environment variable is not set")

    return cbpro.AuthenticatedClient(API_KEY, API_SECRET, API_PASSCODE)
