from __future__ import annotations

import json
from pathlib import Path

from src.utils import CACHE_DIR, ensure_dir


class NewsFetcher:
    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or CACHE_DIR / "news"
        ensure_dir(self.cache_dir)

    def fetch_stock_news(self, symbol: str, date_yyyymmdd: str, force: bool = False) -> list[dict]:
        day_dir = self.cache_dir / date_yyyymmdd
        ensure_dir(day_dir)
        cache_path = day_dir / f"{symbol}.json"
        if cache_path.exists() and not force:
            return json.loads(cache_path.read_text(encoding="utf-8"))

        import akshare as ak  # noqa: WPS433

        data = ak.stock_news_em(symbol=symbol)
        title_col = "标题" if "标题" in data.columns else "新闻标题"
        time_col = "发布时间" if "发布时间" in data.columns else "时间"
        records = []
        for _, row in data.iterrows():
            records.append({
                "title": row.get(title_col, ""),
                "time": row.get(time_col, ""),
            })

        cache_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        return records
