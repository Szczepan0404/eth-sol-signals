import pandas as pd
from binance.client import Client
import datetime

def load_binance_data(pair: str, interval: str, lookback: int):
    client = Client()

    # Zamiana pary np. ETH/USDT → ETHUSDT
    symbol = pair.replace("/", "")

    # Pobranie świec
    klines = client.get_klines(symbol=symbol, interval=interval, limit=lookback)
    if not klines:
        return None

    df = pd.DataFrame(klines, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])

    # Konwersja czasu i ustawienie jako indeksu
    df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    df.set_index("time", inplace=True)

    # Wybieramy potrzebne kolumny i konwertujemy na float
    df = df[["open", "high", "low", "close", "volume"]].astype(float)

    return df
