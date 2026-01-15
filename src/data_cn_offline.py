from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils import OFFLINE_DIR, DateRange, normalize_symbol


class CNDataLoaderOffline:
    def __init__(self, offline_dir: Path | None = None) -> None:
        self.offline_dir = offline_dir or OFFLINE_DIR

    def load(self, symbol: str, date_range: DateRange | None = None) -> pd.DataFrame:
        symbol = normalize_symbol(symbol)
        file_path = self.offline_dir / f"{symbol}.csv"
        data = pd.read_csv(file_path, parse_dates=["Date"]).set_index("Date").sort_index()
        if date_range:
            data = data.loc[date_range.to_slice()]
        return data
