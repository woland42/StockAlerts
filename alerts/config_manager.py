import os
import json
import gspread
from google.oauth2.service_account import Credentials

# Scopes required for Google Sheets and Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_gspread_client():
    """Authenticates and returns a gspread client."""
    # Try Streamlit secrets first (for hosting)
    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=SCOPES
            )
            return gspread.authorize(creds)
    except Exception:
        pass

    # Fallback to environment variable (for GitHub Actions and local)
    creds_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    if creds_json:
        info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        return gspread.authorize(creds)
    
    raise Exception("No Google Cloud credentials found. Set GCP_SERVICE_ACCOUNT_JSON or streamlit secrets.")

def get_worksheet():
    """Opens the 'StockAlertsConfig' spreadsheet and returns the first worksheet."""
    client = get_gspread_client()
    # You must share the sheet with the service account email
    try:
        return client.open("StockAlertsConfig").sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        # Create it if it doesn't exist (only works if Drive API is enabled and account has permission)
        sh = client.create("StockAlertsConfig")
        return sh.sheet1

def load_config() -> dict:
    """
    Loads configuration from Google Sheets.
    The sheet is expected to have headers: Ticker, AlertPrice
    """
    try:
        ws = get_worksheet()
        records = ws.get_all_records()
        
        config = {"tickers": {}}
        for row in records:
            ticker = str(row.get("Ticker", "")).upper().strip()
            level = row.get("AlertPrice")
            
            if not ticker:
                continue
            
            if ticker not in config["tickers"]:
                config["tickers"][ticker] = {"alerts": []}
            
            if level is not None and level != "":
                try:
                    config["tickers"][ticker]["alerts"].append(float(level))
                except (ValueError, TypeError):
                    pass
        return config
    except Exception as e:
        print(f"Error loading config from Google Sheets: {e}")
        return {"tickers": {}}

def save_config(config: dict) -> None:
    """
    Saves configuration to Google Sheets.
    Overwrites the entire sheet with current tickers and alerts.
    """
    try:
        ws = get_worksheet()
        # Prepare data with headers
        rows = [["Ticker", "AlertPrice"]]
        
        for ticker, data in config.get("tickers", {}).items():
            alerts = data.get("alerts", [])
            if not alerts:
                rows.append([ticker, ""])
            else:
                for level in alerts:
                    rows.append([ticker, level])
        
        # Clear and update the sheet
        ws.clear()
        ws.update("A1", rows)
    except Exception as e:
        print(f"Error saving config to Google Sheets: {e}")
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
