import streamlit as st
from indicators import analyze_technical_indicators
from utils import load_binance_data, plot_chart_with_signals

st.set_page_config(layout="wide")

st.title("🔍 ETH/USDT & SOL/USDT Technical Analysis")

pair = st.selectbox("Select trading pair", ["ETH/USDT", "SOL/USDT"])
interval = st.selectbox("Select time interval", ["15m", "1h", "4h", "1d"])
lookback = st.slider("Number of candles", min_value=100, max_value=1000, value=300)

data = load_binance_data(pair, interval, lookback)
if data is not None and not data.empty:
    signals = analyze_technical_indicators(data)
    plot_chart_with_signals(data, signals)
else:
    st.error("Failed to fetch data from Binance.")