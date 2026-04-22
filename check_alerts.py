from dotenv import load_dotenv

load_dotenv()

from alerts.config_manager import load_config, get_tickers, get_alerts
from alerts.price_fetcher import fetch_latest_closes, fetch_history
from alerts.alert_logic import check_all_alerts
from alerts.notifier import notify


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
    else:
        print("\nNo alerts triggered.")

    notify(triggered)


if __name__ == "__main__":
    main()
