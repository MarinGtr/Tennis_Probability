"""
ELO-based probability calculations
"""
import numpy as np


def fiveodds(p3):
    """Convert best-of-3 probability to best-of-5"""
    p1 = np.roots([-2, 3, 0, -1 * p3])[1]
    p5 = (p1 ** 3) * (4 - 3 * p1 + (6 * (1 - p1) * (1 - p1)))
    return p5


def calculate_win_probability(elo1, elo2, bo5=True):
    """Calculate win probability based on ELO ratings"""
    proba = 1 / (1 + 10 ** ((elo2 - elo1) / 400))
    if bo5:
        proba = fiveodds(proba)
    return proba
