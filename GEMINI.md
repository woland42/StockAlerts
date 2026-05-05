# StockAlerts

Self-hosted stock monitoring and alerting system with a Streamlit dashboard and automated price tracking.

## Core Components

- **Dashboard (`app.py`):** Streamlit interface for managing tickers and price alerts. Uses Plotly for visualization.
- **Monitoring Script (`check_alerts.py`):** Headless script to fetch latest prices and trigger notifications.
- **Alert Logic (`alerts/alert_logic.py`):** Detects price crossings and proximity (within 2%).
- **Notifiers (`alerts/notifier.py`):** Supports Telegram and Gmail notifications via environment variables.
- **Configuration (`data/config.json`):** Stores tickers and their associated alert levels.

## Workflows

### Running the Dashboard
```bash
streamlit run app.py
```

### Checking Alerts Manually
```bash
python check_alerts.py
```

### Automation
The project is configured to run via GitHub Actions (`.github/workflows/check_alerts.yml`).

## Configuration
Requires the following environment variables for notifications:
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `GMAIL_SENDER`, `GMAIL_APP_PASSWORD`, `GMAIL_RECIPIENT`
