"""
Player statistics calculation combining regression-based pg and H2H pd
"""
import pandas as pd
import numpy as np

from src.regression import compute_pg_with_regression, predict_pg_from_regression


def find_expo_average(df, numerator_col, denominator_col=None, date_col="match_date", halflife=180):
    """
    Calculate exponentially weighted average (used only for pd - player-direct H2H stats)
    
    Args:
        df: DataFrame with match data
        numerator_col: Column name for numerator
        denominator_col: Column name for denominator (optional)
        date_col: Column name for date
        halflife: Half-life for exponential decay in days
    
    Returns:
        Exponentially weighted average
    """
    cols = [numerator_col, date_col]
    if denominator_col is not None:
        cols.insert(1, denominator_col)

    d = df[cols].copy()
    d[date_col] = pd.to_datetime(d[date_col], format="%Y%m%d", errors="coerce")
    d = d.dropna(subset=[date_col])

    today = pd.Timestamp.today().normalize()
    d["days_ago"] = (today - d[date_col]).dt.days
    decay_lambda = np.log(2) / halflife
    d["weight"] = np.exp(-decay_lambda * d["days_ago"])

    if denominator_col is not None:
        d = d[d[denominator_col] > 0]
        weighted_num = (d[numerator_col] * d["weight"]).sum()
        weighted_den = (d[denominator_col] * d["weight"]).sum()
        if weighted_den == 0:
            return np.nan
        return weighted_num / weighted_den

    return (d[numerator_col] * d["weight"]).sum()


def compute_player_comparison_stats(
    df_overview,
    elo_df,
    playerA,
    playerB,
    halflife_pd=360,
    d_param=150
):
    """
    Compute player statistics using:
    - pd (player-direct): exponential weighted average from H2H matches
    - pg (player-general): LINEAR REGRESSION based on opponent ELO
    
    Args:
        df_overview: DataFrame with all match statistics
        elo_df: DataFrame with ELO ratings
        playerA: Name of player A
        playerB: Name of player B
        halflife_pd: Half-life for exponential decay in H2H calculation
        d_param: Parameter for weighting between pd and pg
    
    Returns:
        Dictionary with calculated statistics and debug information
    """
    
    # Get player ELOs
    playerA_elo = float(elo_df[elo_df['Player'] == playerA]['Elo'].values[0])
    playerB_elo = float(elo_df[elo_df['Player'] == playerB]['Elo'].values[0])
    
    # Head-to-head matches (for pd calculation)
    h2h_matches = (
        df_overview[df_overview["player"].isin([playerA, playerB])]
        .groupby("match_id")
        .filter(lambda x: set(x["player"]) == {playerA, playerB})
    )

    df_A_serving = h2h_matches.loc[h2h_matches["player"] == playerA]
    df_B_serving = h2h_matches.loc[h2h_matches["player"] == playerB]

    # Player-specific (pd) from H2H
    A_1stIn_pd = find_expo_average(df_A_serving, "first_in", "serve_pts", halflife=halflife_pd)
    A_1stWin_pd = find_expo_average(df_A_serving, "first_won", "first_in", halflife=halflife_pd)
    A_2ndWin_pd = find_expo_average(df_A_serving, "second_won", "second_in", halflife=halflife_pd)

    B_1stIn_pd = find_expo_average(df_B_serving, "first_in", "serve_pts", halflife=halflife_pd)
    B_1stWin_pd = find_expo_average(df_B_serving, "first_won", "first_in", halflife=halflife_pd)
    B_2ndWin_pd = find_expo_average(df_B_serving, "second_won", "second_in", halflife=halflife_pd)

    # Player-global (pg) using LINEAR REGRESSION
    df_A = df_overview.loc[df_overview["player"] == playerA]
    df_B = df_overview.loc[df_overview["player"] == playerB]
    
    # Compute regression models for both players
    A_regression = compute_pg_with_regression(df_A, df_overview, elo_df, playerA)
    B_regression = compute_pg_with_regression(df_B, df_overview, elo_df, playerB)
    
    # Predict pg stats using opponent's ELO
    A_1stIn_pg = predict_pg_from_regression(A_regression['reg_first_in'], playerB_elo, default_value=0.65)
    A_1stWin_pg = predict_pg_from_regression(A_regression['reg_first_win'], playerB_elo, default_value=0.7)
    A_2ndWin_pg = predict_pg_from_regression(A_regression['reg_second_win'], playerB_elo, default_value=0.5)
    A_1stWin_return_pg = predict_pg_from_regression(A_regression['reg_return_first'], playerB_elo, default_value=0.3)
    A_2ndWin_return_pg = predict_pg_from_regression(A_regression['reg_return_second'], playerB_elo, default_value=0.5)
    
    B_1stIn_pg = predict_pg_from_regression(B_regression['reg_first_in'], playerA_elo, default_value=0.65)
    B_1stWin_pg = predict_pg_from_regression(B_regression['reg_first_win'], playerA_elo, default_value=0.7)
    B_2ndWin_pg = predict_pg_from_regression(B_regression['reg_second_win'], playerA_elo, default_value=0.5)
    B_1stWin_return_pg = predict_pg_from_regression(B_regression['reg_return_first'], playerA_elo, default_value=0.3)
    B_2ndWin_return_pg = predict_pg_from_regression(B_regression['reg_return_second'], playerA_elo, default_value=0.5)

    # Weight between pd and pg
    n = find_expo_average(df_B_serving, "serve_pts", halflife=halflife_pd)
    weight_d = n / (d_param + n) if (not np.isnan(n) and n > 0) else 0

    def safe_value(val, fallback=0):
        return val if not np.isnan(val) else fallback

    # Calculate final statistics by blending pd and pg
    
    # 1st in
    A_1stIn_pd_safe = safe_value(A_1stIn_pd, A_1stIn_pg)
    A_1stIn_pg_safe = safe_value(A_1stIn_pg, 0.65)
    B_1stIn_pd_safe = safe_value(B_1stIn_pd, B_1stIn_pg)
    B_1stIn_pg_safe = safe_value(B_1stIn_pg, 0.65)
    A_1stIn = weight_d * A_1stIn_pd_safe + (1 - weight_d) * A_1stIn_pg_safe
    B_1stIn = weight_d * B_1stIn_pd_safe + (1 - weight_d) * B_1stIn_pg_safe

    # 1st win (include return blending)
    A_1stWin_pd_safe = safe_value(A_1stWin_pd, A_1stWin_pg)
    A_1stWin_pg_safe = safe_value(A_1stWin_pg, 0.7)
    B_1stWin_return_pg_safe = safe_value(B_1stWin_return_pg, 0.3)

    B_1stWin_pd_safe = safe_value(B_1stWin_pd, B_1stWin_pg)
    B_1stWin_pg_safe = safe_value(B_1stWin_pg, 0.7)
    A_1stWin_return_pg_safe = safe_value(A_1stWin_return_pg, 0.3)

    A_1stWin = weight_d * A_1stWin_pd_safe + (1 - weight_d) * (A_1stWin_pg_safe + 1 - B_1stWin_return_pg_safe) / 2
    B_1stWin = weight_d * B_1stWin_pd_safe + (1 - weight_d) * (B_1stWin_pg_safe + 1 - A_1stWin_return_pg_safe) / 2

    # 2nd win (include return blending)
    A_2ndWin_pd_safe = safe_value(A_2ndWin_pd, A_2ndWin_pg)
    A_2ndWin_pg_safe = safe_value(A_2ndWin_pg, 0.5)
    B_2ndWin_return_pg_safe = safe_value(B_2ndWin_return_pg, 0.5)

    B_2ndWin_pd_safe = safe_value(B_2ndWin_pd, B_2ndWin_pg)
    B_2ndWin_pg_safe = safe_value(B_2ndWin_pg, 0.5)
    A_2ndWin_return_pg_safe = safe_value(A_2ndWin_return_pg, 0.5)

    A_2ndWin = weight_d * A_2ndWin_pd_safe + (1 - weight_d) * (A_2ndWin_pg_safe + 1 - B_2ndWin_return_pg_safe) / 2
    B_2ndWin = weight_d * B_2ndWin_pd_safe + (1 - weight_d) * (B_2ndWin_pg_safe + 1 - A_2ndWin_return_pg_safe) / 2

    return {
        f"{playerA}_1stIn": A_1stIn,
        f"{playerA}_1stWin": A_1stWin,
        f"{playerA}_2ndWin": A_2ndWin,
        f"{playerB}_1stIn": B_1stIn,
        f"{playerB}_1stWin": B_1stWin,
        f"{playerB}_2ndWin": B_2ndWin,
        "debug": {
            "playerA": playerA,
            "playerB": playerB,
            "weight_d": weight_d,

            "A_1stIn_pg": A_1stIn_pg, 
            "A_1stIn_pd": A_1stIn_pd, 
            "A_1stIn_final": A_1stIn,
            "A_regression_1stIn": f"slope={A_regression['slope_first_in']:.6f}, R²={A_regression['r2_first_in']:.3f}" if A_regression['slope_first_in'] is not None else "N/A",
            
            "A_1stWin_pg": A_1stWin_pg, 
            "A_1stWin_pd": A_1stWin_pd, 
            "A_1stWin_final": A_1stWin,
            "A_regression_1stWin": f"slope={A_regression['slope_first_win']:.6f}, R²={A_regression['r2_first_win']:.3f}" if A_regression['slope_first_win'] is not None else "N/A",
            
            "A_2ndWin_pg": A_2ndWin_pg, 
            "A_2ndWin_pd": A_2ndWin_pd, 
            "A_2ndWin_final": A_2ndWin,
            "A_regression_2ndWin": f"slope={A_regression['slope_second_win']:.6f}, R²={A_regression['r2_second_win']:.3f}" if A_regression['slope_second_win'] is not None else "N/A",
            
            "A_1stWin_return_pg": A_1stWin_return_pg, 
            "A_regression_return_1st": f"slope={A_regression['slope_return_first']:.6f}, R²={A_regression['r2_return_first']:.3f}" if A_regression['slope_return_first'] is not None else "N/A",
            
            "A_2ndWin_return_pg": A_2ndWin_return_pg,
            "A_regression_return_2nd": f"slope={A_regression['slope_return_second']:.6f}, R²={A_regression['r2_return_second']:.3f}" if A_regression['slope_return_second'] is not None else "N/A",

            "B_1stIn_pg": B_1stIn_pg, 
            "B_1stIn_pd": B_1stIn_pd, 
            "B_1stIn_final": B_1stIn,
            "B_regression_1stIn": f"slope={B_regression['slope_first_in']:.6f}, R²={B_regression['r2_first_in']:.3f}" if B_regression['slope_first_in'] is not None else "N/A",
            
            "B_1stWin_pg": B_1stWin_pg, 
            "B_1stWin_pd": B_1stWin_pd, 
            "B_1stWin_final": B_1stWin,
            "B_regression_1stWin": f"slope={B_regression['slope_first_win']:.6f}, R²={B_regression['r2_first_win']:.3f}" if B_regression['slope_first_win'] is not None else "N/A",
            
            "B_2ndWin_pg": B_2ndWin_pg, 
            "B_2ndWin_pd": B_2ndWin_pd, 
            "B_2ndWin_final": B_2ndWin,
            "B_regression_2ndWin": f"slope={B_regression['slope_second_win']:.6f}, R²={B_regression['r2_second_win']:.3f}" if B_regression['slope_second_win'] is not None else "N/A",
            
            "B_1stWin_return_pg": B_1stWin_return_pg,
            "B_regression_return_1st": f"slope={B_regression['slope_return_first']:.6f}, R²={B_regression['r2_return_first']:.3f}" if B_regression['slope_return_first'] is not None else "N/A",
            
            "B_2ndWin_return_pg": B_2ndWin_return_pg,
            "B_regression_return_2nd": f"slope={B_regression['slope_return_second']:.6f}, R²={B_regression['r2_return_second']:.3f}" if B_regression['slope_return_second'] is not None else "N/A",
        }
    }
