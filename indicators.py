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

    # Inicjalizacja kolumn
    df['signal'] = None
    df['tp'] = None
    df['sl'] = None

    # Skanujemy od drugiej świecy, bo korzystamy z zamknięcia poprzedniej
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]  # poprzednia świeca (zamknięta)
        entry = df['close'].iloc[i]  # obecna świeca (czyli "po zamknięciu tamtej")
        atr = prev['ATR']

        # BUY
        if (
            prev['EMA50'] > prev['EMA200'] and
            prev['RSI'] < 70 and
            prev['MACD'] > 0 and
            prev['ADX'] > 20
        ):
            df.at[i, 'signal'] = 'buy'
            df.at[i, 'sl'] = entry - 1.5 * atr
            df.at[i, 'tp'] = entry + 1.5 * atr

        # SELL
        elif (
            prev['EMA50'] < prev['EMA200'] and
            prev['RSI'] > 30 and
            prev['MACD'] < 0 and
            prev['ADX'] > 20
        ):
            df.at[i, 'signal'] = 'sell'
            df.at[i, 'sl'] = entry + 1.5 * atr
            df.at[i, 'tp'] = entry - 1.5 * atr

    return df
