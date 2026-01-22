"""
Linear regression-based player statistics calculation
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def compute_pg_with_regression(df_player, df_overview, elo_df, player_name):
    """
    Compute pg (player-general) stats using linear regression: stat = slope * opponent_elo + intercept
    
    Args:
        df_player: DataFrame with player's matches
        df_overview: DataFrame with all matches
        elo_df: DataFrame with ELO ratings
        player_name: Name of the player
    
    Returns:
        Dictionary with regression models and parameters for each statistic
    """
    # Merge player matches with opponents
    df_player_opponents = df_player.merge(
        df_overview[df_overview['player'] != player_name],
        on="match_id",
        suffixes=("", "_opp")
    )
    
    # Build opponent stats list
    opponent_stats = []
    for idx, row in df_player_opponents.iterrows():
        opponent = row.get('player_opp')
        
        # Get player's serve stats
        serve_pts = row.get('serve_pts', None)
        first_in = row.get('first_in', None)
        first_won = row.get('first_won', None)
        second_in = row.get('second_in', None)
        second_won = row.get('second_won', None)
        
        # Get opponent's serve stats (for return calculations)
        first_in_opp = row.get('first_in_opp', None)
        first_won_opp = row.get('first_won_opp', None)
        second_in_opp = row.get('second_in_opp', None)
        second_won_opp = row.get('second_won_opp', None)

        # Compute percentages for the player
        first_in_pct = first_in / serve_pts if (pd.notna(serve_pts) and pd.notna(first_in) and serve_pts > 0) else None
        first_win_pct = first_won / first_in if (pd.notna(first_in) and pd.notna(first_won) and first_in > 0) else None
        second_win_pct = second_won / second_in if (pd.notna(second_in) and pd.notna(second_won) and second_in > 0) else None

        # Return percentages (1 - opponent's win%)
        return_first_win_pct = 1 - (first_won_opp / first_in_opp) if (pd.notna(first_in_opp) and pd.notna(first_won_opp) and first_in_opp > 0) else None
        return_second_win_pct = 1 - (second_won_opp / second_in_opp) if (pd.notna(second_in_opp) and pd.notna(second_won_opp) and second_in_opp > 0) else None

        # Get opponent Elo
        elo = None
        if opponent is not None:
            elo_row = elo_df[elo_df['Player'] == opponent]
            if not elo_row.empty:
                elo = float(elo_row.iloc[0]['Elo'])

        opponent_stats.append({
            'opponent': opponent,
            'elo': elo,
            'first_in_pct': first_in_pct,
            'first_win_pct': first_win_pct,
            'second_win_pct': second_win_pct,
            'return_first_win_pct': return_first_win_pct,
            'return_second_win_pct': return_second_win_pct
        })
    
    # Filter and perform regression
    def filter_and_regress(stat_key, apply_bounds=True):
        """
        Filter data and perform linear regression
        
        Args:
            stat_key: Key for the statistic to regress
            apply_bounds: If True, filter stat values between 0.1 and 0.9
        
        Returns:
            Tuple of (regression_model, slope, intercept, r2)
        """
        if apply_bounds:
            filtered = [d for d in opponent_stats 
                       if d['elo'] is not None 
                       and d[stat_key] is not None 
                       and 0.1 < d[stat_key] < 0.9]
        else:
            filtered = [d for d in opponent_stats 
                       if d['elo'] is not None 
                       and d[stat_key] is not None]
        
        if len(filtered) < 3:  # Need at least 3 points for regression
            return None, None, None, None
        
        X = np.array([d['elo'] for d in filtered]).reshape(-1, 1)
        y = np.array([d[stat_key] for d in filtered])
        
        reg = LinearRegression()
        reg.fit(X, y)
        
        slope = reg.coef_[0]
        intercept = reg.intercept_
        r2 = reg.score(X, y)
        
        return reg, slope, intercept, r2
    
    # Perform regressions for each stat
    reg_first_in, slope_first_in, intercept_first_in, r2_first_in = filter_and_regress('first_in_pct', apply_bounds=False)
    reg_first_win, slope_first_win, intercept_first_win, r2_first_win = filter_and_regress('first_win_pct', apply_bounds=True)
    reg_second_win, slope_second_win, intercept_second_win, r2_second_win = filter_and_regress('second_win_pct', apply_bounds=True)
    reg_return_first, slope_return_first, intercept_return_first, r2_return_first = filter_and_regress('return_first_win_pct', apply_bounds=True)
    reg_return_second, slope_return_second, intercept_return_second, r2_return_second = filter_and_regress('return_second_win_pct', apply_bounds=True)
    
    return {
        'reg_first_in': reg_first_in,
        'slope_first_in': slope_first_in,
        'intercept_first_in': intercept_first_in,
        'r2_first_in': r2_first_in,
        
        'reg_first_win': reg_first_win,
        'slope_first_win': slope_first_win,
        'intercept_first_win': intercept_first_win,
        'r2_first_win': r2_first_win,
        
        'reg_second_win': reg_second_win,
        'slope_second_win': slope_second_win,
        'intercept_second_win': intercept_second_win,
        'r2_second_win': r2_second_win,
        
        'reg_return_first': reg_return_first,
        'slope_return_first': slope_return_first,
        'intercept_return_first': intercept_return_first,
        'r2_return_first': r2_return_first,
        
        'reg_return_second': reg_return_second,
        'slope_return_second': slope_return_second,
        'intercept_return_second': intercept_return_second,
        'r2_return_second': r2_return_second,
    }


def predict_pg_from_regression(regression_model, opponent_elo, default_value=0.5):
    """
    Predict a statistic using the regression model and opponent's ELO
    
    Args:
        regression_model: Trained LinearRegression model
        opponent_elo: ELO rating of the opponent
        default_value: Default value if prediction fails
    
    Returns:
        Predicted statistic value (clipped between 0 and 1)
    """
    if regression_model is None:
        return default_value
    
    try:
        prediction = regression_model.predict([[opponent_elo]])[0]
        # Clip to reasonable bounds
        return np.clip(prediction, 0.0, 1.0)
    except Exception:
        return default_value
