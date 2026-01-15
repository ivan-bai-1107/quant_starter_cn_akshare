from __future__ import annotations

from src.news_cn import NewsFetcher
from src.sector_cn import get_industry_cons


def calc_sector_buzz(industry_name: str, date_yyyymmdd: str, top_cons: int = 20) -> float:
    fetcher = NewsFetcher()
    cons = get_industry_cons(industry_name, top_n=top_cons)
    total = 0
    for symbol in cons:
        news = fetcher.fetch_stock_news(symbol, date_yyyymmdd)
        total += len(news)
    return float(total)


def calc_sector_sentiment(industry_name: str, date_yyyymmdd: str, top_cons: int = 20) -> float:
    raise NotImplementedError("Sentiment scoring is not implemented in MVP")
