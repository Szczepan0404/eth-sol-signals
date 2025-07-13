import pandas as pd
import requests
import time

def load_binance_data(symbol: str, interval: str, limit: int = 300) -> pd.DataFrame:
    symbol = symbol.replace("/", "")
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])

        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df.columns = ["timestamp", "open", "high", "low", "close", "volume"]

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)

        df = df.astype(float)

        return df

    except Exception as e:
        print(f"❌ Błąd podczas pobierania danych z Binance: {e}")
        return pd.DataFrame()
