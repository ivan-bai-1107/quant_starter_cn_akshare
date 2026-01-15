# quant_starter_cn_akshare

A-share research starter with online/offline data loading, sector rotation backtests, and news-based buzz scoring.

## Setup

```bash
pip install -r requirements.txt
```

## Visual UI

Run the Streamlit app for an interactive interface:

```bash
streamlit run app.py
```

## Single Stock Backtest

Online:

```bash
python -m src.backtest_cn --mode online --symbol 600519 --start 2018-01-01 --end 2025-12-31 --adjust qfq
```

Offline (expects `offline_data/600519.csv`):

```bash
python -m src.backtest_cn --mode offline --symbol 600519
```

## Sector Rotation Backtest

Online:

```bash
python -m src.backtest_sector_rotation --mode online --start 2018-01-01 --end 2025-12-31 --top_k 3 --industries 半导体 银行 医药商业 煤炭 证券 --trend_filter
```

Offline (expects `offline_data/<行业名>.csv`):

```bash
python -m src.backtest_sector_rotation --mode offline --top_k 3 --industries 半导体 银行 医药商业
```

## Outputs

- `outputs/stats_*.csv`: summary statistics
- `outputs/report_*.html`: NAV curve report
- `outputs/selected_sectors_*.csv`: selected sectors per rebalance date

## Offline data format

CSV columns must include:

```
Date, Open, High, Low, Close, Volume, Amount
```
