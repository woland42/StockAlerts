import json
import os
import tempfile
from pathlib import Path

CONFIG_PATH = Path("data/config.json")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        config = {"tickers": {}}
        save_config(config)
        return config
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=CONFIG_PATH.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        os.replace(tmp_path, CONFIG_PATH)
    except Exception:
        os.unlink(tmp_path)
        raise


def get_tickers(config: dict) -> list:
    return sorted(config.get("tickers", {}).keys())


def get_alerts(config: dict, ticker: str) -> list:
    return sorted(config.get("tickers", {}).get(ticker, {}).get("alerts", []))


def add_ticker(config: dict, ticker: str) -> dict:
    ticker = ticker.upper().strip()
    if ticker not in config.setdefault("tickers", {}):
        config["tickers"][ticker] = {"alerts": []}
    return config


def remove_ticker(config: dict, ticker: str) -> dict:
    config.setdefault("tickers", {}).pop(ticker, None)
    return config


def add_alert(config: dict, ticker: str, level: float) -> dict:
    alerts = config.setdefault("tickers", {}).setdefault(ticker, {"alerts": []})["alerts"]
    if level not in alerts:
        alerts.append(level)
    return config


def remove_alert(config: dict, ticker: str, level: float) -> dict:
    alerts = config.get("tickers", {}).get(ticker, {}).get("alerts", [])
    if level in alerts:
        alerts.remove(level)
    return config
