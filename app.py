# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from binance.client import Client
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.volatility import AverageTrueRange
import datetime

st.set_page_config(layout="wide")

# Konfiguracja Binance
API_KEY = ""
API_SECRET = ""
client = Client(API_KEY, API_SECRET)

# Domyślne ustawienia
DEFAULT_SYMBOL = "ETHUSDT"
DEFAULT_INTERVAL = "1h"
INTERVALS = {
    "15m": Client.KLINE_INTERVAL_15MINUTE,
    "1h": Client.KLINE_INTERVAL_1HOUR,
    "4h": Client.KLINE_INTERVAL_4HOUR,
    "1d": Client.KLINE_INTERVAL_1DAY
}

# Funkcja do pobierania danych
def get_data(symbol, interval, lookback_days=30):
    klines = client.get_historical_klines(symbol, interval, f"{lookback_days} day ago UTC")
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

# Oblicz wskaźniki
def calculate_indicators(df):
    df["EMA50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["EMA200"] = EMAIndicator(df["close"], window=200).ema_indicator()
    df["RSI"] = RSIIndicator(df["close"]).rsi()
    macd = MACD(df["close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    bb = BollingerBands(df["close"])
    df["BB_upper"] = bb.bollinger_hband()
    df["BB_lower"] = bb.bollinger_lband()
    df["ADX"] = ADXIndicator(df["high"], df["low"], df["close"]).adx()
    df["ATR"] = AverageTrueRange(df["high"], df["low"]()
