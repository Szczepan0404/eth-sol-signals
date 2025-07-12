import requests

# 🔁 UZUPEŁNIJ DANYMI TWOJEGO BOTA:
TELEGRAM_BOT_TOKEN = '8169372223:AAGQ-v6duLcL9WSluJnm7RQWAco4HQ4QtXA'
TELEGRAM_CHAT_ID = '8042623691'

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"❌ Błąd podczas wysyłania wiadomości: {response.text}")
        else:
            print("✅ Wiadomość wysłana na Telegram!")
    except Exception as e:
        print(f"❌ Wyjątek podczas wysyłania do Telegrama: {e}")
