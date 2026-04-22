import os
import smtplib
import ssl
from email.mime.text import MIMEText

import requests


def format_alert_message(triggered: list) -> str:
    lines = ["Stock Alert(s) Triggered:\n"]
    for alert in triggered:
        pct = abs(alert["current"] - alert["level"]) / alert["level"] * 100
        reason_map = {
            "crossed_up": "crossed UP through",
            "crossed_down": "crossed DOWN through",
            "proximity": "within 2% of",
        }
        desc = reason_map.get(alert["reason"], alert["reason"])
        lines.append(
            f"  {alert['ticker']} @ ${alert['current']:.2f} — {desc} alert ${alert['level']:.2f} ({pct:.2f}% away)"
        )
    return "\n".join(lines)


def send_telegram(message: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram: missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            return True
        print(f"Telegram: API error — {data}")
        return False
    except Exception as e:
        print(f"Telegram: request failed — {e}")
        return False


def send_gmail(message: str) -> bool:
    sender = os.environ.get("GMAIL_SENDER")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("GMAIL_RECIPIENT")
    if not all([sender, password, recipient]):
        print("Gmail: missing GMAIL_SENDER, GMAIL_APP_PASSWORD, or GMAIL_RECIPIENT")
        return False
    try:
        msg = MIMEText(message)
        msg["Subject"] = "Stock Price Alert"
        msg["From"] = sender
        msg["To"] = recipient
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        return True
    except Exception as e:
        print(f"Gmail: send failed — {e}")
        return False


def notify(triggered: list) -> None:
    if not triggered:
        return
    message = format_alert_message(triggered)
    if send_telegram(message):
        print("Notification sent via Telegram.")
        return
    if send_gmail(message):
        print("Notification sent via Gmail.")
        return
    print("Notification failed: both Telegram and Gmail failed.")
