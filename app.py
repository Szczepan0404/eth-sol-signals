import streamlit as st
import pandas as pd
from indicators import analyze_technical_indicators
from utils import load_binance_data
from telegram_alerts import send_telegram_message
import plotly.graph_objects as go
import pytz

# Konfiguracja
st.set_page_config(layout="wide")
st.title("🔍 ETH/USDT & SOL/USDT Technical Analysis")

# Wybór pary i interwału
pair = st.selectbox("Select trading pair", ["ETH/USDT", "SOL/USDT"])
interval = st.selectbox("Select time interval", ["15m", "1h", "4h", "1d"])
lookback = st.slider("Number of candles", min_value=100, max_value=1000, value=300)

# Pobranie danych
data = load_binance_data(pair, interval, lookback)

if data is not None and not data.empty:
    df = analyze_technical_indicators(data)

    # Upewniamy się, że indeks to DatetimeIndex z czasem UTC
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")

    # Konwersja na czas Europe/Warsaw
    warsaw = pytz.timezone("Europe/Warsaw")
    df.index = df.index.tz_convert(warsaw)

    # Wykres świecowy
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Candles'
        )
    ])
    fig.update_layout(title=f'{pair} Candlestick Chart', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Ostatni zamknięty sygnał = przedostatnia świeca
    if df['signal'].notna().iloc[-2]:
        signal_row = df.iloc[-2]
        signal = signal_row['signal']
        entry = signal_row['close']
        sl = signal_row['sl']
        tp = signal_row['tp']
        signal_time = df.index[-2].strftime("%Y-%m-%d %H:%M:%S")

        st.markdown("### 📋 Ostatni zamknięty sygnał")
        signal_table = pd.DataFrame({
            "Data i godzina": [signal_time],
            "Sygnał": [signal.upper()],
            "Cena wejścia": [f"{entry:.2f}"],
            "Stop Loss": [f"{sl:.2f}"],
            "Take Profit": [f"{tp:.2f}"]
        })
        st.table(signal_table)

        # Telegram
        message = f"""
📈 Sygnał **{signal.upper()}** dla {pair} ({interval})  
🕒 Czas: {signal_time}  
🎯 Cena wejścia: {entry:.2f}  
✅ TP: {tp:.2f}  
⛔ SL: {sl:.2f}
        """
        send_telegram_message(message.strip())
    else:
        st.info("Brak nowego sygnału w ostatniej zamkniętej świecy.")

    # Historia 3 ostatnich sygnałów
    last_signals = df[df['signal'].notna()].iloc[-3:]
    if not last_signals.empty:
        st.markdown("### 📈 Historia 3 ostatnich sygnałów")
        history_data = {
            "Data i godzina": last_signals.index.strftime("%Y-%m-%d %H:%M:%S"),
            "Sygnał": last_signals["signal"].str.upper(),
            "Cena wejścia": last_signals["close"].round(2),
            "Stop Loss": last_signals["sl"].round(2),
            "Take Profit": last_signals["tp"].round(2),
        }
        history_table = pd.DataFrame(history_data)
        st.table(history_table)
else:
    st.error("❌ Nie udało się pobrać danych z Binance.")
