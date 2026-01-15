from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils import OFFLINE_DIR


def get_industry_list() -> list[str]:
    import akshare as ak  # noqa: WPS433

    data = ak.stock_board_industry_name_em()
    return data["板块名称"].tolist()


def get_industry_index_hist(industry_name: str) -> pd.DataFrame:
    import akshare as ak  # noqa: WPS433

    data = ak.stock_board_industry_hist_em(symbol=industry_name)
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
    return data.set_index("Date").sort_index()


def get_industry_cons(industry_name: str, top_n: int = 20) -> list[str]:
    import akshare as ak  # noqa: WPS433

    data = ak.stock_board_industry_cons_em(symbol=industry_name)
    codes = data["代码"].tolist()
    return codes[:top_n]


def load_industry_offline(industry_name: str, offline_dir: Path | None = None) -> pd.DataFrame:
    base_dir = offline_dir or OFFLINE_DIR
    file_path = base_dir / f"{industry_name}.csv"
    data = pd.read_csv(file_path, parse_dates=["Date"]).set_index("Date").sort_index()
    return data
