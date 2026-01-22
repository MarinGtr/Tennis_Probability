"""
Basic tests for tennis probability calculator
Run with: python -m pytest test_app.py
"""
import numpy as np
import pandas as pd
from src.probability_calculator import calculate_win_probability, fiveodds
from src.monte_carlo import simulate_point, simulate_game
from src.utils import pct, safe_stat_value


def test_fiveodds():
    """Test best-of-5 conversion"""
    # Test with 50% win probability
    result = fiveodds(0.5)
    assert 0.45 < result < 0.55, "50% BO3 should be close to 50% BO5"
    
    # Test with 70% win probability
    result = fiveodds(0.7)
    assert 0.75 < result < 0.85, "70% BO3 should increase in BO5"


def test_calculate_win_probability():
    """Test ELO-based probability calculation"""
    # Equal ELO should give ~50% probability
    prob = calculate_win_probability(2000, 2000, bo5=False)
    assert 0.49 < prob < 0.51, "Equal ELO should give ~50% probability"
    
    # Higher ELO should give higher probability
    prob1 = calculate_win_probability(2100, 2000)
    prob2 = calculate_win_probability(2000, 2100)
    assert prob1 > 0.5, "Higher ELO should have >50% win probability"
    assert prob2 < 0.5, "Lower ELO should have <50% win probability"
    assert abs(prob1 - (1 - prob2)) < 0.01, "Probabilities should be complementary"


def test_simulate_point():
    """Test point simulation"""
    # With 100% first serve in and 100% first serve won, server should always win
    wins = sum([simulate_point(1.0, 1.0, 0.5) for _ in range(100)])
    assert wins == 100, "100% serve should win all points"
    
    # With 0% first serve and 0% second serve won, server should never win
    wins = sum([simulate_point(0.0, 0.5, 0.0) for _ in range(100)])
    assert wins == 0, "0% serve won should win no points"


def test_simulate_game():
    """Test game simulation"""
    # Run multiple games and check that results are boolean
    for _ in range(10):
        result = simulate_game(0.65, 0.75, 0.55, 0.65, 0.70, 0.50)
        assert result in [True, False], "Game result should be boolean"


def test_pct():
    """Test percentage formatting"""
    assert pct(0.5) == "50%"
    assert pct(0.725) == "73%"
    assert pct(None) == "NA"
    assert pct(np.nan) == "NA"


def test_safe_stat_value():
    """Test safe stat value handling"""
    assert safe_stat_value(0.5, 0.3) == 0.5
    assert safe_stat_value(None, 0.3) == 0.3
    assert safe_stat_value(np.nan, 0.3) == 0.3
    assert safe_stat_value(1.5, 0.3) == 0.3  # Out of bounds
    assert safe_stat_value(-0.1, 0.3) == 0.3  # Out of bounds


if __name__ == "__main__":
    # Run tests manually
    print("Running tests...")
    
    test_fiveodds()
    print("✓ test_fiveodds passed")
    
    test_calculate_win_probability()
    print("✓ test_calculate_win_probability passed")
    
    test_simulate_point()
    print("✓ test_simulate_point passed")
    
    test_simulate_game()
    print("✓ test_simulate_game passed")
    
    test_pct()
    print("✓ test_pct passed")
    
    test_safe_stat_value()
    print("✓ test_safe_stat_value passed")
    
    print("\n✓ All tests passed!")
