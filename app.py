import streamlit as st
import pandas as pd  # Dodane! By działało pd.notna()
from indicators import analyze_technical_indicators
from utils import load_binance_data, plot_chart_with_signals
from telegram_alerts import send_telegram_message

st.set_page_config(layout="wide")
st.title("🔍 ETH/USDT & SOL/USDT Technical Analysis")

# Wybór pary i interwału
pair = st.selectbox("Select trading pair", ["ETH/USDT", "SOL/USDT"])
interval = st.selectbox("Select time interval", ["15m", "1h", "4h", "1d"])
lookback = st.slider("Number of candles", min_value=100, max_value=1000, value=300)

# Pobranie danych
data = load_binance_data(pair, interval, lookback)

# Usuwamy rzędy z brakującymi danymi OHLC
if data is not None:
    data = data.dropna(subset=["open", "high", "low", "close"])

if data is not None and not data.empty:
    df = analyze_technical_indicators(data)

    # Tworzymy listę sygnałów do wykresu
    signals = []
    for i, row in df.iterrows():
        if pd.notna(row["signal"]):
            signals.append({
                "time": i,
                "type": row["signal"].upper(),
                "price": row["close"],
                "tp": row["tp"],
                "sl": row["sl"]
            })

    # Pobranie ostatniego sygnału z pełnymi danymi
    filtered_signals = df.dropna(subset=["signal", "close", "sl", "tp"])
    last_row = filtered_signals.iloc[-1] if not filtered_signals.empty else None

    if last_row is not None:
        signal = last_row["signal"]
        price = last_row["close"]
        sl = last_row["sl"]
        tp = last_row["tp"]

        # ✅ Wyświetlenie w aplikacji
        st.markdown(f"### 📊 Sygnał: **{signal.upper()}**")
        st.markdown(f"- 🎯 Cena wejścia: **{price:.2f}**")
        st.markdown(f"- ⛔ Stop Loss: **{sl:.2f}**")
        st.markdown(f"- ✅ Take Profit: **{tp:.2f}**")

        # ✅ Wysyłanie powiadomienia na Telegram
        message = f"""
📈 Sygnał **{signal.upper()}** dla {pair} ({interval})
🎯 Cena wejścia: {price:.2f}
✅ TP: {tp:.2f}
⛔ SL: {sl:.2f}
        """
        send_telegram_message(message.strip())

    # ✅ Wyświetlenie wykresu z sygnałami
    plot_chart_with_signals(df, signals)

else:
    st.error("❌ Nie udało się pobrać danych z Binance lub dane są niekompletne.")
