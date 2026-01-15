from __future__ import annotations

import pandas as pd


def sma_signal(close: pd.Series, fast: int = 20, slow: int = 50) -> pd.Series:
    fast_sma = close.rolling(fast).mean()
    slow_sma = close.rolling(slow).mean()
    signal = (fast_sma > slow_sma).astype(float)
    return signal.fillna(0.0)
