import pandas as pd
import ta

def analyze_technical_indicators(df):
    # Wskaźniki techniczne
    df['EMA50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['EMA200'] = ta.trend.ema_indicator(df['close'], window=200)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    df['MACD'] = ta.trend.macd_diff(df['close'])
    df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
    df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)

    # Dodaj puste kolumny
    df['signal'] = None
    df['tp'] = None
    df['sl'] = None

    # Przeskanuj wszystkie świece
    for i in range(len(df)):
        if (
            df['EMA50'].iloc[i] > df['EMA200'].iloc[i] and
            df['RSI'].iloc[i] < 70 and
            df['MACD'].iloc[i] > 0 and
            df['ADX'].iloc[i] > 20
        ):
            entry = df['close'].iloc[i]
            atr = df['ATR'].iloc[i]
            df.at[i, 'signal'] = 'buy'
            df.at[i, 'sl'] = entry - 1.5 * atr
            df.at[i, 'tp'] = entry + 1.5 * (entry - (entry - 1.5 * atr))  # lub: entry + 1.5 * atr

        elif (
            df['EMA50'].iloc[i] < df['EMA200'].iloc[i] and
            df['RSI'].iloc[i] > 30 and
            df['MACD'].iloc[i] < 0 and
            df['ADX'].iloc[i] > 20
        ):
            entry = df['close'].iloc[i]
            atr = df['ATR'].iloc[i]
            df.at[i, 'signal'] = 'sell'
            df.at[i, 'sl'] = entry + 1.5 * atr
            df.at[i, 'tp'] = entry - 1.5 * (entry + 1.5 * atr - entry)  # lub: entry - 1.5 * atr

    return df
