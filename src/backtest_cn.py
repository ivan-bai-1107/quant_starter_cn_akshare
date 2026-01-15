from __future__ import annotations

import argparse
from datetime import datetime

import pandas as pd

from src.data_cn import CNDataLoader
from src.data_cn_offline import CNDataLoaderOffline
from src.report import compute_stats, save_nav_report, save_stats
from src.strategy import sma_signal
from src.utils import DateRange, normalize_symbol


def run_backtest(symbol: str, mode: str, start: str | None, end: str | None, adjust: str) -> tuple[pd.Series, pd.Series]:
    date_range = DateRange(start, end)
    if mode == "online":
        loader = CNDataLoader()
        data = loader.load(symbol, date_range=date_range, adjust=adjust)
    else:
        loader = CNDataLoaderOffline()
        data = loader.load(symbol, date_range=date_range)

    close = data["Close"]
    signal = sma_signal(close)
    weights = signal.shift(1).fillna(0.0)
    returns = close.pct_change().fillna(0.0)
    strat_returns = returns * weights
    nav = (1 + strat_returns).cumprod()
    return nav, strat_returns


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["online", "offline"], default="online")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--adjust", default="qfq")
    args = parser.parse_args()

    symbol = normalize_symbol(args.symbol)
    nav, returns = run_backtest(symbol, args.mode, args.start, args.end, args.adjust)
    stats = compute_stats(nav, returns)
    tag = f"cn_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    save_stats(stats, tag)
    save_nav_report(nav, tag)


if __name__ == "__main__":
    main()
