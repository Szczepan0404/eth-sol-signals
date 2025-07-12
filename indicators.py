import pandas as pd
import ta

def analyze_technical_indicators(df):
    signals = []

    df['EMA50'] = ta.trend.ema_indicator(df['close'], window=50).ema_indicator()
    df['EMA200'] = ta.trend.ema_indicator(df['close'], window=200).ema_indicator()
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    macd = ta.trend.macd_diff(df['close'])
    df['MACD'] = macd
    df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
    df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)

    if (
        df['EMA50'].iloc[-1] > df['EMA200'].iloc[-1] and
        df['RSI'].iloc[-1] < 70 and
        df['MACD'].iloc[-1] > 0 and
        df['ADX'].iloc[-1] > 20
    ):
        sl = df['close'].iloc[-1] - 1.5 * df['ATR'].iloc[-1]
        tp = df['close'].iloc[-1] + 1.5 * (df['close'].iloc[-1] - sl)
        signals.append({'type': 'BUY', 'price': df['close'].iloc[-1], 'sl': sl, 'tp': tp})

    elif (
        df['EMA50'].iloc[-1] < df['EMA200'].iloc[-1] and
        df['RSI'].iloc[-1] > 30 and
        df['MACD'].iloc[-1] < 0 and
        df['ADX'].iloc[-1] > 20
    ):
        sl = df['close'].iloc[-1] + 1.5 * df['ATR'].iloc[-1]
        tp = df['close'].iloc[-1] - 1.5 * (sl - df['close'].iloc[-1])
        signals.append({'type': 'SELL', 'price': df['close'].iloc[-1], 'sl': sl, 'tp': tp})

    return signals