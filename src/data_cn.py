from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils import CACHE_DIR, DateRange, ensure_dir, normalize_symbol


class CNDataLoader:
    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or CACHE_DIR / "price"
        ensure_dir(self.cache_dir)

    def load(self, symbol: str, date_range: DateRange | None = None, adjust: str = "qfq") -> pd.DataFrame:
        symbol = normalize_symbol(symbol)
        cache_path = self.cache_dir / f"{symbol}_{adjust}.csv"
        if cache_path.exists():
            data = pd.read_csv(cache_path, parse_dates=["Date"]).set_index("Date")
        else:
            import akshare as ak  # noqa: WPS433

            data = ak.stock_zh_a_hist(symbol=symbol, adjust=adjust)
            data = self._normalize_columns(data)
            data.to_csv(cache_path, index=True)

        if date_range:
            data = data.loc[date_range.to_slice()]
        return data

    @staticmethod
    def _normalize_columns(data: pd.DataFrame) -> pd.DataFrame:
        column_map = {
            "日期": "Date",
            "开盘": "Open",
            "收盘": "Close",
            "最高": "High",
            "最低": "Low",
            "成交量": "Volume",
            "成交额": "Amount",
        }
        data = data.rename(columns=column_map)
        keep = ["Date", "Open", "High", "Low", "Close", "Volume", "Amount"]
        data = data[keep]
        data["Date"] = pd.to_datetime(data["Date"])
        data = data.set_index("Date").sort_index()
        return data
