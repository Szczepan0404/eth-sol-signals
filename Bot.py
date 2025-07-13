import time
import pandas as pd
from datetime import datetime
import pytz
from utils import load_binance_data
from indicators import analyze_technical_indicators
from telegram_alerts import send_telegram_message

# Konfiguracja
PAIR = "ETH/USDT"
INTERVAL = "1h"
LOOKBACK = 300
CHECK_INTERVAL = 60 * 60  # co godzinę (w sekundach)

warsaw_tz = pytz.timezone("Europe/Warsaw")

last_signal_time = None

while True:
    try:
        # Pobierz dane
        df = load_binance_data(PAIR, INTERVAL, LOOKBACK)
        if df is None or df.empty:
            print("Brak danych.")
            time.sleep(CHECK_INTERVAL)
            continue

        df = analyze_technical_indicators(df)

        # Przetwórz czas
        if df.index.tz is None or df.index.tzinfo is None:
            df.index = pd.to_datetime(df.index, unit="ms", utc=True).tz_convert(warsaw_tz)
        else:
            df.index = df.index.tz_convert(warsaw_tz)

        # Ostatnia świeca zamknięta
        row = df.iloc[-2]
        timestamp = df.index[-2]

        if pd.notna(row["signal"]) and timestamp != last_signal_time:
            signal = row["signal"]
            price = row["close"]
            tp = row["tp"]
            sl = row["sl"]

            message = f"""
📢 **Nowy sygnał ({PAIR})**
🕒 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
📈 Sygnał: {signal.upper()}
🎯 Cena wejścia: {price:.2f}
✅ TP: {tp:.2f}
⛔ SL: {sl:.2f}
            """
            send_telegram_message(message.strip())
            last_signal_time = timestamp

        else:
            print(f"[{datetime.now(warsaw_tz)}] Brak nowego sygnału.")

    except Exception as e:
        print(f"Błąd: {e}")

    time.sleep(CHECK_INTERVAL)
