"""Reporting helpers.

The report is generated only after the frozen experiment card has been run. This
module is a placeholder so the repository has one obvious place for tables and
figures rather than ad-hoc notebook code.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["format_metric_table"]


def format_metric_table(metrics: pd.DataFrame, decimals: int = 4) -> str:
    """Render a metrics frame as a Markdown table."""
    if not isinstance(metrics, pd.DataFrame):
        raise TypeError("metrics must be a pandas DataFrame")
    return metrics.round(decimals).to_markdown()
