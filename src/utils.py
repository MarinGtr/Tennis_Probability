"""
Utility functions for tennis probability calculator
"""
import numpy as np


def pct(x):
    """Convert a decimal to percentage string"""
    if x is None:
        return "NA"
    try:
        if np.isnan(x):
            return "NA"
    except Exception:
        pass
    return f"{round(100 * float(x))}%"


def safe_stat_value(stat_value, default_value):
    """Return stat value if valid, otherwise return default"""
    if stat_value is None:
        return default_value
    try:
        if np.isnan(stat_value):
            return default_value
    except Exception:
        pass
    if stat_value < 0 or stat_value > 1:
        return default_value
    return stat_value
