PROXIMITY_THRESHOLD = 0.01


def is_within_proximity(current: float, level: float, threshold: float = PROXIMITY_THRESHOLD) -> bool:
    if level == 0:
        return False
    return abs(current - level) / level <= threshold


def has_crossed(prev: float, current: float, level: float) -> str | None:
    if prev < level <= current:
        return "crossed_up"
    if prev > level >= current:
        return "crossed_down"
    return None


def check_ticker_alerts(ticker: str, current: float, prev: float | None, levels: list) -> list:
    triggered = []
    for level in levels:
        reason = None
        if prev is not None:
            reason = has_crossed(prev, current, level)
        if reason is None and is_within_proximity(current, level):
            reason = "proximity"
        if reason is not None:
            triggered.append({
                "ticker": ticker,
                "level": level,
                "current": current,
                "reason": reason,
            })
    return triggered


def check_all_alerts(config: dict, current_prices: dict, prev_prices: dict) -> list:
    triggered = []
    for ticker, ticker_data in config.get("tickers", {}).items():
        current = current_prices.get(ticker)
        if current is None:
            continue
        prev = prev_prices.get(ticker)
        levels = ticker_data.get("alerts", [])
        triggered.extend(check_ticker_alerts(ticker, current, prev, levels))
    return triggered
