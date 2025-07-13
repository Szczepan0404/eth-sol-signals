import streamlit as st
import pandas as pd
from indicators import analyze_technical_indicators
from utils import load_binance_data
from telegram_alerts import send_telegram_message
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🔍 ETH/USDT & SOL/USDT Technical Analysis")

# Wybór pary i interwału
pair = st.selectbox("Select trading pair", ["ETH/USDT", "SOL/USDT"])
interval = st.selectbox("Select time interval", ["15m", "1h", "4h", "1d"])
lookback = st.slider("Number of candles", min_value=100, max_value=1000, value=300)

# Pobranie danych
data = load_binance_data(pair, interval, lookback)

if data is not None and not data.empty:
    # Konwersja do czasu lokalnego
    data.index = data.index.tz_convert("Europe/Warsaw")

    df = analyze_technical_indicators(data)

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

    # Filtrujemy 3 ostatnie zamknięte sygnały (nie bieżąca świeca)
    last_signals = df.iloc[:-1].dropna(subset=["signal"]).tail(3)

    if not last_signals.empty:
        # Formatowanie danych
        signal_table = pd.DataFrame({
            "Data/godzina": last_signals.index.strftime("%Y-%m-%d %H:%M:%S"),
            "Sygnał": last_signals["signal"].str.upper(),
            "Cena wejścia": last_signals["close"].astype(float).round(2),
            "Stop Loss": last_signals["sl"].astype(float).round(2),
            "Take Profit": last_signals["tp"].astype(float).round(2)
        })

        st.markdown("### 📋 Ostatnie 3 sygnały (zamknięte świece)")
        st.table(signal_table)

        # Wysyłka ostatniego z nich na Telegram
        latest = last_signals.iloc[-1]
        message = f"""
📈 Sygnał **{latest['signal'].upper()}** dla {pair} ({interval})  
🕒 Data/godzina: {latest.name.strftime('%Y-%m-%d %H:%M:%S')}  
🎯 Cena wejścia: {latest['close']:.2f}  
✅ TP: {latest['tp']:.2f}  
⛔ SL: {latest['sl']:.2f}
        """
        send_telegram_message(message.strip())
    else:
        st.info("Brak nowych sygnałów w ostatnich zamkniętych świecach.")
else:
    st.error("❌ Nie udało się pobrać danych z Binance.")
