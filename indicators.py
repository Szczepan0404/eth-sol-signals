import pandas as pd
import ta

def analyze_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # Wskaźniki techniczne
    df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)
    df["RSI"] = ta.momentum.rsi(df["close"], window=14)
    df["MACD"] = ta.trend.macd_diff(df["close"])
    df["ADX"] = ta.trend.adx(df["high"], df["low"], df["close"], window=14)
    df["ATR"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14)

    # Kolumny sygnałów
    df["signal"] = None
    df["tp"] = None
    df["sl"] = None

    for i in range(len(df)):
        if (
            df["EMA50"].iloc[i] > df["EMA200"].iloc[i] and
            df["RSI"].iloc[i] < 70 and
            df["MACD"].iloc[i] > 0 and
            df["ADX"].iloc[i] > 20
        ):
            entry = df["close"].iloc[i]
            atr = df["ATR"].iloc[i]
            df.at[df.index[i], "signal"] = "buy"
            df.at[df.index[i], "sl"] = entry - 1.5 * atr
            df.at[df.index[i], "tp"] = entry + 1.5 * atr

        elif (
            df["EMA50"].iloc[i] < df["EMA200"].iloc[i] and
            df["RSI"].iloc[i] > 30 and
            df["MACD"].iloc[i] < 0 and
            df["ADX"].iloc[i] > 20
        ):
            entry = df["close"].iloc[i]
            atr = df["ATR"].iloc[i]
            df.at[df.index[i], "signal"] = "sell"
            df.at[df.index[i], "sl"] = entry + 1.5 * atr
            df.at[df.index[i], "tp"] = entry - 1.5 * atr

    return df
