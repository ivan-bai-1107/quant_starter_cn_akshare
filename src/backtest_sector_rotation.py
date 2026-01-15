from __future__ import annotations

import argparse
from datetime import datetime

import pandas as pd

from src.content_score import calc_sector_buzz
from src.report import compute_stats, save_nav_report, save_selected_sectors, save_stats
from src.sector_cn import get_industry_index_hist, get_industry_list, load_industry_offline
from src.utils import DateRange, list_to_str


def load_sector_prices(industries: list[str], mode: str, date_range: DateRange | None) -> pd.DataFrame:
    frames = []
    for industry in industries:
        if mode == "online":
            data = get_industry_index_hist(industry)
        else:
            data = load_industry_offline(industry)
        if date_range:
            data = data.loc[date_range.to_slice()]
        frames.append(data["Close"].rename(industry))
    return pd.concat(frames, axis=1).dropna(how="all")


def weekly_rebalance_dates(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    weekly = index.to_series().resample("W-FRI").last().dropna()
    return pd.DatetimeIndex(weekly.values)


def select_topk(
    industries: list[str],
    rebalance_date: pd.Timestamp,
    top_k: int,
) -> pd.Series:
    date_str = rebalance_date.strftime("%Y%m%d")
    scores = {}
    for industry in industries:
        scores[industry] = calc_sector_buzz(industry, date_str)
    scores_series = pd.Series(scores).sort_values(ascending=False)
    return scores_series.head(top_k)


def apply_trend_filter(close: pd.Series, window: int = 20) -> bool:
    sma = close.rolling(window).mean()
    if close.empty:
        return False
    return bool(close.iloc[-1] > sma.iloc[-1])


def build_weights(
    close: pd.DataFrame,
    industries: list[str],
    top_k: int,
    use_trend_filter: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    weights = pd.DataFrame(0.0, index=close.index, columns=industries)
    selected_records = []
    rebalance_dates = weekly_rebalance_dates(close.index)

    for date in rebalance_dates:
        scores = select_topk(industries, date, top_k)
        selected = []
        for industry in scores.index:
            series = close[industry].loc[:date].dropna()
            if use_trend_filter and not apply_trend_filter(series):
                continue
            selected.append(industry)
        if not selected:
            continue
        weight = 1 / len(selected)
        weights.loc[date, selected] = weight
        selected_records.append({
            "Date": date,
            "Selected": list_to_str(selected),
            "Scores": scores.to_dict(),
        })

    weights = weights.shift(1).ffill().fillna(0.0)
    selected_df = pd.DataFrame(selected_records).set_index("Date")
    return weights, selected_df


def run_backtest(
    mode: str,
    industries: list[str],
    start: str | None,
    end: str | None,
    top_k: int,
    use_trend_filter: bool,
) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    date_range = DateRange(start, end)
    close = load_sector_prices(industries, mode, date_range)
    weights, selected = build_weights(close, industries, top_k, use_trend_filter)
    returns = close.pct_change().fillna(0.0)
    strategy_returns = (returns * weights).sum(axis=1)
    nav = (1 + strategy_returns).cumprod()
    return nav, strategy_returns, selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["online", "offline"], default="online")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--top_k", type=int, default=3)
    parser.add_argument("--industries", nargs="*")
    parser.add_argument("--trend_filter", action="store_true")
    args = parser.parse_args()

    industries = args.industries
    if not industries:
        industries = get_industry_list()

    nav, returns, selected = run_backtest(
        args.mode,
        industries,
        args.start,
        args.end,
        args.top_k,
        args.trend_filter,
    )
    stats = compute_stats(nav, returns)
    tag = f"sector_rotation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    save_stats(stats, tag)
    save_nav_report(nav, tag)
    if not selected.empty:
        save_selected_sectors(selected, tag)


if __name__ == "__main__":
    main()
