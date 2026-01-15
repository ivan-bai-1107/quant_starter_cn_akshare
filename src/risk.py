from __future__ import annotations

import pandas as pd


def apply_stop_loss(close: pd.Series, threshold: float = 0.1) -> pd.Series:
    peak = close.cummax()
    drawdown = (close - peak) / peak
    signal = (drawdown > -threshold).astype(float)
    return signal.fillna(0.0)
