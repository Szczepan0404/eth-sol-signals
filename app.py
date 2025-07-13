import streamlit as st
import pandas as pd
import pytz
from indicators import analyze_technical_indicators
from utils import load_binance_data
from telegram_alerts import send_telegram_message
import plotly.graph_objects as go

# Konfiguracja strefy czasowej
warsaw_tz = pytz.timezone("Europe/Warsaw")

st.set_page_config(layout="wide")
st.title("🔍 ETH/USDT & SOL/USDT Technical Analysis")

# Wybór pary i interwału
pair = st.selectbox("Select trading pair", ["ETH/USDT", "SOL/USDT"])
interval = st.selectbox("Select time interval", ["15m", "1h", "4h", "1d"])
lookback = st.slider("Number of candles", min_value=100, max_value=1000, value=300)

# Pobranie danych
data = load_binance_data(pair, interval, lookback)

if data is not None and not data.empty:
    # Konwersja indeksu do datetime (jeśli nie jest) i ustawienie strefy czasowej
    if not pd.api.types.is_datetime64_any_dtype(data.index):
        data.index = pd.to_datetime(data.index)

    data.index = data.index.tz_localize("UTC").tz_convert(warsaw_tz)

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

    # Pobranie ostatniego zamkniętego sygnału (przedostatni wiersz)
    signal_row = df.iloc[-2] if df['signal'].notna().iloc[-2] else None

    if signal_row is not None:
        signal = signal_row['signal']
        entry = signal_row['close']
        sl = signal_row['sl']
        tp = signal_row['tp']
        timestamp = df.index[-2].strftime("%Y-%m-%d %H:%M:%S")

        # Tabela z ostatnim sygnałem
        st.markdown("### 📋 Ostatni zamknięty sygnał")
        signal_table = pd.DataFrame({
            "Data/godzina": [timestamp],
            "Sygnał": [signal.upper()],
            "Cena wejścia": [f"{entry:.2f}"],
            "Stop Loss": [f"{sl:.2f}"],
            "Take Profit": [f"{tp:.2f}"]
        })
        st.table(signal_table)

        # Wysyłka do Telegrama
        message = f"""
📈 Sygnał **{signal.upper()}** dla {pair} ({interval})  
🕒 Czas (PL): {timestamp}  
🎯 Cena wejścia: {entry:.2f}  
✅ TP: {tp:.2f}  
⛔ SL: {sl:.2f}
        """
        send_telegram_message(message.strip())
    else:
        st.info("Brak nowego sygnału w ostatniej zamkniętej świecy.")

    # Historia ostatnich 3 sygnałów
    st.markdown("### 📈 Historia 3 ostatnich sygnałów")
    last_signals = df[df['signal'].notna()].tail(3)

    if not last_signals.empty:
        history_table = pd.DataFrame({
            "Data/godzina": last_signals.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S"),
            "Sygnał": last_signals["signal"].str.upper(),
            "Cena wejścia": last_signals["close"].round(2),
            "Stop Loss": pd.to_numeric(last_signals["sl"], errors="coerce").round(2),
            "Take Profit": pd.to_numeric(last_signals["tp"], errors="coerce").round(2)
        })
        st.table(history_table)
    else:
        st.info("Brak historii sygnałów.")

else:
    st.error("❌ Nie udało się pobrać danych z Binance.")
