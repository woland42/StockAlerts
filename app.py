import streamlit as st
import plotly.graph_objects as go

from alerts.config_manager import (
    load_config, save_config,
    get_tickers, get_alerts,
    add_ticker, remove_ticker, add_alert, remove_alert,
)
from alerts.price_fetcher import fetch_history


def init_session_state() -> None:
    if "config" not in st.session_state:
        st.session_state["config"] = load_config()


def render_sidebar() -> None:
    st.sidebar.header("Tickers")

    with st.sidebar.form("add_ticker_form", clear_on_submit=True):
        new_ticker = st.text_input("Add ticker (e.g. AAPL)")
        submitted = st.form_submit_button("Add")
        if submitted and new_ticker.strip():
            st.session_state["config"] = add_ticker(st.session_state["config"], new_ticker.strip())
            save_config(st.session_state["config"])
            st.rerun()

    tickers = get_tickers(st.session_state["config"])
    for ticker in tickers:
        col1, col2 = st.sidebar.columns([3, 1])
        col1.write(ticker)
        if col2.button("✕", key=f"remove_{ticker}"):
            st.session_state["config"] = remove_ticker(st.session_state["config"], ticker)
            save_config(st.session_state["config"])
            st.rerun()


def render_ticker_section(ticker: str) -> None:
    st.subheader(ticker)

    period = st.selectbox(
        "Period", ["1mo", "3mo", "6mo", "1y", "2y"],
        index=2, key=f"period_{ticker}"
    )

    try:
        df = fetch_history(ticker, period=period)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"],
            mode="lines", name="Close",
            line=dict(color="#1f77b4", width=1.5),
        ))
        alerts = get_alerts(st.session_state["config"], ticker)
        for level in alerts:
            fig.add_hline(
                y=level,
                line_dash="dash", line_color="red",
                annotation_text=f"${level:.2f}",
                annotation_position="right",
            )
        fig.update_layout(
            title=ticker,
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=350,
            margin=dict(l=40, r=80, t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not fetch data for {ticker}: {e}")

    st.markdown("**Alert levels**")
    alerts = get_alerts(st.session_state["config"], ticker)
    if alerts:
        for level in alerts:
            col1, col2 = st.columns([4, 1])
            col1.write(f"${level:.2f}")
            if col2.button("Remove", key=f"rm_alert_{ticker}_{level}"):
                st.session_state["config"] = remove_alert(st.session_state["config"], ticker, level)
                save_config(st.session_state["config"])
                st.rerun()
    else:
        st.caption("No alerts defined yet.")

    with st.form(f"add_alert_{ticker}", clear_on_submit=True):
        new_level = st.number_input("New alert price", min_value=0.01, step=1.0, format="%.2f", key=f"alert_input_{ticker}")
        if st.form_submit_button("Add Alert"):
            st.session_state["config"] = add_alert(st.session_state["config"], ticker, new_level)
            save_config(st.session_state["config"])
            st.rerun()

    st.divider()


def main() -> None:
    st.set_page_config(page_title="Stock Alerts", layout="wide")
    st.title("Stock Price Alerts")

    init_session_state()
    render_sidebar()

    tickers = get_tickers(st.session_state["config"])
    if not tickers:
        st.info("Add a ticker in the sidebar to get started.")
        return

    for ticker in tickers:
        render_ticker_section(ticker)


if __name__ == "__main__":
    main()
