from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = DATA_DIR / "data_cache"
OUTPUT_DIR = DATA_DIR / "outputs"
OFFLINE_DIR = DATA_DIR / "offline_data"


@dataclass(frozen=True)
class DateRange:
    start: str | None = None
    end: str | None = None

    def to_slice(self) -> slice:
        start = pd.to_datetime(self.start) if self.start else None
        end = pd.to_datetime(self.end) if self.end else None
        return slice(start, end)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def parse_date(date_value: str | datetime) -> pd.Timestamp:
    return pd.to_datetime(date_value)


def normalize_symbol(symbol: str) -> str:
    return symbol.strip()


def coerce_float_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def list_to_str(items: Iterable[str]) -> str:
    return ",".join(items)
