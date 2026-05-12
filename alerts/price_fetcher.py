import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data(ttl=3600)
def fetch_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    df = yf.Ticker(ticker).history(period=period)
    if df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'")
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df[["Close"]]


def fetch_latest_close(ticker: str) -> float | None:
    try:
        df = yf.Ticker(ticker).history(period="5d")
        if df.empty:
            return None
        return float(df["Close"].iloc[-1])
    except Exception:
        return None


def fetch_latest_closes(tickers: list) -> dict:
    result = {}
    if not tickers:
        return result
    try:
        data = yf.download(tickers, period="5d", group_by="ticker", auto_adjust=True, progress=False)
        if len(tickers) == 1:
            ticker = tickers[0]
            result[ticker] = float(data["Close"].iloc[-1]) if not data.empty else None
        else:
            for ticker in tickers:
                try:
                    closes = data[ticker]["Close"].dropna()
                    result[ticker] = float(closes.iloc[-1]) if not closes.empty else None
                except Exception:
                    result[ticker] = None
    except Exception:
        for ticker in tickers:
            result[ticker] = fetch_latest_close(ticker)
    return result
