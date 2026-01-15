from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.utils import OUTPUT_DIR, ensure_dir


def compute_stats(nav: pd.Series, returns: pd.Series) -> pd.DataFrame:
    total_return = nav.iloc[-1] / nav.iloc[0] - 1
    drawdown = nav / nav.cummax() - 1
    max_drawdown = drawdown.min()
    sharpe = 0.0
    if returns.std() != 0:
        sharpe = (returns.mean() / returns.std()) * (252 ** 0.5)
    win_rate = (returns > 0).mean()
    stats = pd.DataFrame([
        {
            "Total Return": total_return,
            "Max Drawdown": max_drawdown,
            "Sharpe": sharpe,
            "Win Rate": win_rate,
        }
    ])
    return stats


def save_stats(stats: pd.DataFrame, name: str) -> Path:
    ensure_dir(OUTPUT_DIR)
    path = OUTPUT_DIR / f"stats_{name}.csv"
    stats.to_csv(path, index=False)
    return path


def save_nav_report(nav: pd.Series, name: str) -> Path:
    ensure_dir(OUTPUT_DIR)
    fig, ax = plt.subplots(figsize=(10, 4))
    nav.plot(ax=ax, title="Net Asset Value")
    ax.set_xlabel("Date")
    ax.set_ylabel("NAV")
    fig.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    html = f"""
    <html>
    <head><meta charset="utf-8"><title>Report</title></head>
    <body>
      <h1>Net Asset Value</h1>
      <img src="data:image/png;base64,{img_str}" alt="NAV" />
      <h2>Latest NAV</h2>
      <pre>{nav.tail().to_string()}</pre>
    </body>
    </html>
    """
    path = OUTPUT_DIR / f"report_{name}.html"
    path.write_text(html, encoding="utf-8")
    return path


def save_selected_sectors(selected: pd.DataFrame, name: str) -> Path:
    ensure_dir(OUTPUT_DIR)
    path = OUTPUT_DIR / f"selected_sectors_{name}.csv"
    selected.to_csv(path, index=True)
    return path
