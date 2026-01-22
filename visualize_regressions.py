"""
Visualization script for analyzing player statistics vs opponent ELO
This creates plots similar to your original analysis code
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os

from src.data_loader import load_elo_data, load_overview_data


def plot_player_regressions(player_name, df_overview, elo_df, output_dir="plots"):
    """
    Create regression plots for a single player
    
    Args:
        player_name: Name of the player to analyze
        df_overview: DataFrame with match statistics
        elo_df: DataFrame with ELO ratings
        output_dir: Directory to save plots
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n----- Plotting for Player: {player_name} -----\n")
    
    # Get player's matches
    df_player = df_overview.loc[df_overview['player'] == player_name]
    df_player_opponents = df_player.merge(
        df_overview[df_overview['player'] != player_name],
        on="match_id",
        suffixes=("", "_opp")
    )

    # Generate opponent stats
    opponent_stats = []
    for idx, row in df_player_opponents.iterrows():
        opponent = row.get('player_opp')
        
        serve_pts = row.get('serve_pts', None)
        first_in = row.get('first_in', None)
        first_won = row.get('first_won', None)
        second_in = row.get('second_in', None)
        second_won = row.get('second_won', None)
        first_in_opp = row.get('first_in_opp', None)
        first_won_opp = row.get('first_won_opp', None)
        second_in_opp = row.get('second_in_opp', None)
        second_won_opp = row.get('second_won_opp', None)

        # Compute percentages
        first_in_pct = first_in / serve_pts if (pd.notna(serve_pts) and pd.notna(first_in) and serve_pts > 0) else None
        first_win_pct = first_won / first_in if (pd.notna(first_in) and pd.notna(first_won) and first_in > 0) else None
        second_win_pct = second_won / second_in if (pd.notna(second_in) and pd.notna(second_won) and second_in > 0) else None
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
            'first_in_pct': first_in_pct,
            'first_win_pct': first_win_pct,
            'second_win_pct': second_win_pct,
            'return_first_win_pct': return_first_win_pct,
            'return_second_win_pct': return_second_win_pct,
            'elo': elo
        })

    # Filter data
    filtered_stats_first_win = [
        d for d in opponent_stats 
        if d['elo'] is not None and d['first_win_pct'] is not None and 0.1 < d['first_win_pct'] < 0.9
    ]
    filtered_stats_first_in = [
        d for d in opponent_stats 
        if d['elo'] is not None and d['first_in_pct'] is not None
    ]
    filtered_stats_second_win = [
        d for d in opponent_stats 
        if d['elo'] is not None and d['second_win_pct'] is not None and 0.1 < d['second_win_pct'] < 0.9
    ]
    filtered_stats_return_first_win = [
        d for d in opponent_stats 
        if d['elo'] is not None and d['return_first_win_pct'] is not None and 0.1 < d['return_first_win_pct'] < 0.9
    ]
    filtered_stats_return_second_win = [
        d for d in opponent_stats 
        if d['elo'] is not None and d['return_second_win_pct'] is not None and 0.1 < d['return_second_win_pct'] < 0.9
    ]

    # Prepare arrays
    elo_values_first_win = np.array([d['elo'] for d in filtered_stats_first_win]).reshape(-1, 1)
    first_win_pct_values = np.array([d['first_win_pct'] for d in filtered_stats_first_win])

    elo_values_first_in = np.array([d['elo'] for d in filtered_stats_first_in]).reshape(-1, 1)
    first_in_pct_values = np.array([d['first_in_pct'] for d in filtered_stats_first_in])

    elo_values_second_win = np.array([d['elo'] for d in filtered_stats_second_win]).reshape(-1, 1)
    second_win_pct_values = np.array([d['second_win_pct'] for d in filtered_stats_second_win])

    elo_values_return_first_win = np.array([d['elo'] for d in filtered_stats_return_first_win]).reshape(-1, 1)
    return_first_win_pct_values = np.array([d['return_first_win_pct'] for d in filtered_stats_return_first_win])

    elo_values_return_second_win = np.array([d['elo'] for d in filtered_stats_return_second_win]).reshape(-1, 1)
    return_second_win_pct_values = np.array([d['return_second_win_pct'] for d in filtered_stats_return_second_win])

    # Fit regressions
    def fit_and_predict(x, y):
        reg = LinearRegression()
        reg.fit(x, y)
        y_pred = reg.predict(x)
        slope = reg.coef_[0]
        intercept = reg.intercept_
        r2 = reg.score(x, y)
        return reg, y_pred, slope, intercept, r2

    reg_fw, pred_fw, slope_fw, intercept_fw, r2_fw = fit_and_predict(elo_values_first_win, first_win_pct_values)
    reg_fi, pred_fi, slope_fi, intercept_fi, r2_fi = fit_and_predict(elo_values_first_in, first_in_pct_values)
    reg_sw, pred_sw, slope_sw, intercept_sw, r2_sw = fit_and_predict(elo_values_second_win, second_win_pct_values)
    reg_rfw, pred_rfw, slope_rfw, intercept_rfw, r2_rfw = fit_and_predict(elo_values_return_first_win, return_first_win_pct_values)
    reg_rsw, pred_rsw, slope_rsw, intercept_rsw, r2_rsw = fit_and_predict(elo_values_return_second_win, return_second_win_pct_values)

    # Create figure with 5 plots
    fig, axes = plt.subplots(5, 1, figsize=(10, 25))

    # 1st Serve Points Won %
    axes[0].scatter(elo_values_first_win, first_win_pct_values, color='blue', alpha=0.7, label='Data')
    axes[0].plot(elo_values_first_win, pred_fw, color='red', label=f'Linear fit (slope={slope_fw:.4f})')
    axes[0].set_xlabel('Opponent Elo')
    axes[0].set_ylabel('Player First Serve Won %')
    axes[0].set_title(f'{player_name}: 1st Serve Points Won % vs. Opponent Elo')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[0].text(0.05, 0.95, f'y = {slope_fw:.4f} * Elo + {intercept_fw:.4f}\n$R^2$ = {r2_fw:.3f}',
                 transform=axes[0].transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 1st Serve In %
    axes[1].scatter(elo_values_first_in, first_in_pct_values, color='green', alpha=0.7, label='Data')
    axes[1].plot(elo_values_first_in, pred_fi, color='red', label=f'Linear fit (slope={slope_fi:.4f})')
    axes[1].set_xlabel('Opponent Elo')
    axes[1].set_ylabel('Player First Serve In %')
    axes[1].set_title(f'{player_name}: 1st Serve In % vs. Opponent Elo')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    axes[1].text(0.05, 0.95, f'y = {slope_fi:.4f} * Elo + {intercept_fi:.4f}\n$R^2$ = {r2_fi:.3f}',
                 transform=axes[1].transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 2nd Serve Won %
    axes[2].scatter(elo_values_second_win, second_win_pct_values, color='purple', alpha=0.7, label='Data')
    axes[2].plot(elo_values_second_win, pred_sw, color='red', label=f'Linear fit (slope={slope_sw:.4f})')
    axes[2].set_xlabel('Opponent Elo')
    axes[2].set_ylabel('Player Second Serve Won %')
    axes[2].set_title(f'{player_name}: 2nd Serve Points Won % vs. Opponent Elo')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    axes[2].text(0.05, 0.95, f'y = {slope_sw:.4f} * Elo + {intercept_sw:.4f}\n$R^2$ = {r2_sw:.3f}',
                 transform=axes[2].transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Return 1st Serve Won %
    axes[3].scatter(elo_values_return_first_win, return_first_win_pct_values, color='orange', alpha=0.7, label='Data')
    axes[3].plot(elo_values_return_first_win, pred_rfw, color='red', label=f'Linear fit (slope={slope_rfw:.4f})')
    axes[3].set_xlabel('Opponent Elo')
    axes[3].set_ylabel('Return 1st Serve Won %')
    axes[3].set_title(f'{player_name}: Return 1st Serve Points Won % vs. Opponent Elo')
    axes[3].grid(True, alpha=0.3)
    axes[3].legend()
    axes[3].text(0.05, 0.95, f'y = {slope_rfw:.4f} * Elo + {intercept_rfw:.4f}\n$R^2$ = {r2_rfw:.3f}',
                 transform=axes[3].transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Return 2nd Serve Won %
    axes[4].scatter(elo_values_return_second_win, return_second_win_pct_values, color='brown', alpha=0.7, label='Data')
    axes[4].plot(elo_values_return_second_win, pred_rsw, color='red', label=f'Linear fit (slope={slope_rsw:.4f})')
    axes[4].set_xlabel('Opponent Elo')
    axes[4].set_ylabel('Return 2nd Serve Won %')
    axes[4].set_title(f'{player_name}: Return 2nd Serve Points Won % vs. Opponent Elo')
    axes[4].grid(True, alpha=0.3)
    axes[4].legend()
    axes[4].text(0.05, 0.95, f'y = {slope_rsw:.4f} * Elo + {intercept_rsw:.4f}\n$R^2$ = {r2_rsw:.3f}',
                 transform=axes[4].transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    
    # Save figure
    filename = f"{output_dir}/{player_name.replace(' ', '_')}_regression_analysis.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Saved plot: {filename}")
    
    plt.close()


def main():
    """Main function to generate plots for multiple players"""
    
    # Load data
    print("Loading data...")
    elo_df = load_elo_data()
    elo_df["Elo"] = (elo_df["Elo"] + elo_df["hElo"]) / 2
    overview_df = load_overview_data()
    
    # List of players to analyze
    players_to_plot = [
        'Alexander Zverev', 
        'Felix Auger Aliassime', 
        'Jannik Sinner', 
        'Alex De Minaur', 
        'Carlos Alcaraz', 
        'Alexander Bublik', 
        'Taylor Fritz', 
        'Lorenzo Musetti', 
        'Novak Djokovic', 
        'Daniil Medvedev'
    ]
    
    # Filter to players that exist in the data
    available_players = set(overview_df['player'].unique())
    players_to_plot = [p for p in players_to_plot if p in available_players]
    
    if not players_to_plot:
        print("No players found in data. Using top 10 by match count...")
        player_match_counts = overview_df['player'].value_counts().head(10)
        players_to_plot = player_match_counts.index.tolist()
    
    print(f"\nGenerating plots for {len(players_to_plot)} players...")
    
    # Generate plots
    for player in players_to_plot:
        try:
            plot_player_regressions(player, overview_df, elo_df)
        except Exception as e:
            print(f"Error plotting {player}: {e}")
    
    print(f"\n✓ Finished! Plots saved in 'plots/' directory")


if __name__ == "__main__":
    main()
