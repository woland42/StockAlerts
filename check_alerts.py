import os
import datetime
from dotenv import load_dotenv

load_dotenv()

from alerts.config_manager import load_config, get_tickers, get_alerts, remove_alert, save_config
from alerts.price_fetcher import fetch_latest_closes, fetch_history
from alerts.alert_logic import check_all_alerts
from alerts.notifier import notify, send_telegram


def get_prev_prices(tickers: list) -> dict:
    prev = {}
    for ticker in tickers:
        try:
            df = fetch_history(ticker, period="5d")
            if len(df) >= 2:
                prev[ticker] = float(df["Close"].iloc[-2])
            else:
                prev[ticker] = None
        except Exception:
            prev[ticker] = None
    return prev


def main() -> None:
    config = load_config()
    tickers = get_tickers(config)

    if not tickers:
        print("No tickers configured.")
        return

    print(f"Checking {len(tickers)} ticker(s): {', '.join(tickers)}")

    current_prices = fetch_latest_closes(tickers)
    prev_prices = get_prev_prices(tickers)

    for ticker in tickers:
        curr = current_prices.get(ticker)
        prev = prev_prices.get(ticker)
        alerts = get_alerts(config, ticker)
        curr_str = f"${curr:.2f}" if curr is not None else "N/A"
        prev_str = f"${prev:.2f}" if prev is not None else "N/A"
        print(f"  {ticker}: current={curr_str}, prev={prev_str}, alerts={alerts}")

    triggered = check_all_alerts(config, current_prices, prev_prices)

    if triggered:
        print(f"\n{len(triggered)} alert(s) triggered:")
        for a in triggered:
            print(f"  {a['ticker']} @ ${a['current']:.2f} — {a['reason']} level ${a['level']:.2f}")
        
        if notify(triggered):
            print("Cleaning up triggered alerts from config...")
            for a in triggered:
                remove_alert(config, a["ticker"], a["level"])
            save_config(config)
            print("Config updated successfully.")
    else:
        print("\nNo alerts triggered.")
        
        # Check for forced test alert
        force_val = os.environ.get("FORCE_ALERT")
        print(f"DEBUG: FORCE_ALERT value is: '{force_val}'")
        if force_val == "true":
            print("Forcing test notification...")
            success = send_telegram("🔔 Stock Alert Service: Test notification. Your monitoring system is working!")
            print(f"DEBUG: send_telegram success: {success}")

        # Monday Heartbeat: If no alerts triggered on a Monday, send a status update.
        elif datetime.datetime.now().weekday() == 0:  # 0 is Monday
            print("DEBUG: Sending Monday heartbeat...")
            send_telegram("🔔 Stock Alert Service: Heartbeat (Monday). Monitoring is active and running.")


if __name__ == "__main__":
    main()
