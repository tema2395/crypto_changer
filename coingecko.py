from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()


def get_usdt_uah_price():
    price = cg.get_price(ids="tether", vs_currencies="uah")
    return price["tether"]["uah"]


def get_usdt_rub_price():
    price = cg.get_price(ids="tether", vs_currencies="rub")
    return price["tether"]["rub"]
