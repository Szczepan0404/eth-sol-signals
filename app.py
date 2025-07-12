import streamlit as st
from indicators import analyze_technical_indicators
from utils import load_binance_data, plot_chart_with_signals
from telegram_alerts import send_telegram_message  # Dodane

st.set_page_config(layout="wide")

st.title("🔍 ETH/USDT & SOL/USDT Technical Analysis")

# Wybór pary i interwału
pair = st.selectbox("Select trading pair", ["ETH/USDT", "SOL/USDT"])
interval = st.selectbox("Select time interval", ["15m", "1h", "4h", "1d"])
lookback = st.slider("Number of candles", min_value=100, max_value=1000, value=300)

# Pobieranie danych z Binance
data = load_binance_data(pair, interval, lookback)

# Analiza i wykres
if data is not None and not data.empty:
    signals = analyze_technical_indicators(data)

    # Sprawdź ostatni sygnał i wyślij wiadomość na Telegram
    last_signal = signals.iloc[-1]["signal"]
    if last_signal == "buy":
        send_telegram_message(f"🟢 BUY sygnał dla {pair} na interwale {interval}")
    elif last_signal == "sell":
        send_telegram_message(f"🔴 SELL sygnał dla {pair} na interwale {interval}")

    plot_chart_with_signals(data, signals)
else:
    st.error("Failed to fetch data from Binance.")
