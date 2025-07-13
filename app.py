import streamlit as st
import pandas as pd
from indicators import analyze_technical_indicators
from utils import load_binance_data
from telegram_alerts import send_telegram_message
import plotly.graph_objects as go
from zoneinfo import ZoneInfo  # 🇵🇱 dodajemy strefę czasową Polski

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

    # Upewnij się, że indeks ma strefę czasową
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")

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

    # ✅ Szukamy ostatniego zamkniętego sygnału (pomijamy ostatnią świecę)
    recent_signals = df.iloc[:-1]
    if recent_signals['signal'].notna().any():
        signal_row = recent_signals[recent_signals['signal'].notna()].iloc[-1]
        signal_time = recent_signals[recent_signals['signal'].notna()].index[-1]

        # 🔁 Konwersja na polską strefę czasową
        signal_time_pl = signal_time.tz_convert(ZoneInfo("Europe/Warsaw"))

        signal = signal_row['signal']
        entry = signal_row['close']
        sl = signal_row['sl']
        tp = signal_row['tp']

        # Tabelka z parametrami sygnału
        st.markdown("### 📋 Ostatni zamknięty sygnał")
        signal_table = pd.DataFrame({
            "Data i godzina (PL)": [signal_time_pl.strftime("%Y-%m-%d %H:%M")],
            "Sygnał": [signal.upper()],
            "Cena wejścia": [f"{entry:.2f}"],
            "Stop Loss": [f"{sl:.2f}"],
            "Take Profit": [f"{tp:.2f}"]
        })
        st.table(signal_table)

        # Powiadomienie Telegram
        message = f"""
📈 Sygnał **{signal.upper()}** dla {pair} ({interval})  
🕒 Czas (Polska): {signal_time_pl.strftime("%Y-%m-%d %H:%M")}  
🎯 Cena wejścia: {entry:.2f}  
✅ TP: {tp:.2f}  
⛔ SL: {sl:.2f}
        """
        send_telegram_message(message.strip())
    else:
        st.info("Brak nowego sygnału w ostatnich zamkniętych świecach.")
else:
    st.error("❌ Nie udało się pobrać danych z Binance.")
