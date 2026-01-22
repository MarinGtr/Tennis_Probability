"""
Tennis Probability Calculator - Main Application
"""
import streamlit as st
import pandas as pd

from src.data_loader import load_elo_data, load_overview_data, load_ao_players
from src.stats_calculator import compute_player_comparison_stats
from src.probability_calculator import calculate_win_probability
from src.monte_carlo import monte_carlo_simulation
from src.utils import pct, safe_stat_value

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(
    page_title="Tennis Game Probability",
    page_icon="🎾",
    layout="centered"
)

st.title("🎾 Tennis Probability Calculator")
st.markdown("---")

# ----------------------------
# Load data
# ----------------------------
try:
    elo_df = load_elo_data()
    if "hElo" not in elo_df.columns:
        st.error("ELO data must contain both 'Elo' and 'hElo' columns.")
        st.stop()

    elo_df["Elo"] = (elo_df["Elo"] + elo_df["hElo"]) / 2

    ao_players = load_ao_players()
    elo_df = elo_df[elo_df["Player"].isin(ao_players)]
    if len(elo_df) == 0: 
        st.error("No Players found")
        st.stop()
    player_names = sorted(elo_df["Player"].dropna().unique().tolist())

except Exception as e:
    st.error(f"Error loading ELO or AO player data: {e}")
    st.stop()

try:
    overview_df = load_overview_data()
    overview_df = overview_df[overview_df["player"].isin(ao_players)].copy()
except Exception as e:
    st.warning(f"Warning: Could not load overview statistics data: {e}")
    overview_df = None

# ----------------------------
# Sidebar UI
# ----------------------------
st.sidebar.header("Select Players")
player1 = st.sidebar.selectbox(
    "Player 1", options=[""] + player_names, key="player1_select",
    format_func=lambda x: x if x else "Choose a player..."
)
player2 = st.sidebar.selectbox(
    "Player 2", options=[""] + player_names, key="player2_select",
    format_func=lambda x: x if x else "Choose a player..."
)

DEFAULTS = {
    "player1_first_in": 0.99,
    "player1_first_win": 0.7250798290361934,
    "player1_second_win": 0.5229896049963166,
    "player2_first_in": 0.99,
    "player2_first_win": 0.6978813372924711,
    "player2_second_win": 0.5383737814353623,
}

# ----------------------------
# Main app logic
# ----------------------------
if player1 and player2:
    if player1 == player2:
        st.warning("Select two different players.")
        st.stop()

    player1_row = elo_df[elo_df["Player"] == player1]
    player2_row = elo_df[elo_df["Player"] == player2]
    if player1_row.empty or player2_row.empty:
        st.error("Could not find both players in the ELO data.")
        st.stop()

    elo1 = float(player1_row["Elo"].values[0])
    elo2 = float(player2_row["Elo"].values[0])
    prob1 = calculate_win_probability(elo1, elo2)
    prob2 = 1 - prob1

    st.subheader("Win Probability (Based on ELO)")
    c1, c2 = st.columns(2)
    with c1:
        st.metric(f"Probability {player1} wins", f"{prob1*100:.1f}%")
    with c2:
        st.metric(f"Probability {player2} wins", f"{prob2*100:.1f}%")

    st.markdown("---")

    # Calculate serve statistics
    calculated_stats = None
    if overview_df is not None:
        try:
            overview_players = overview_df["player"].unique()
            if player1 in overview_players and player2 in overview_players:
                with st.spinner("Calculating serve statistics using linear regression..."):
                    calculated_stats = compute_player_comparison_stats(
                        overview_df, elo_df, player1, player2,
                        halflife_pd=360, d_param=150
                    )
                st.success("✅ Serve statistics calculated using linear regression based on opponent ELO")
            else:
                missing = [p for p in [player1, player2] if p not in overview_players]
                st.info(f"⚠️ Note: {' and '.join(missing)} not found in historical match data. Using default values.")
        except Exception as e:
            st.warning(f"⚠️ Could not calculate serve statistics: {e}. Using default values.")

    # Display debug information
    if calculated_stats and "debug" in calculated_stats:
        dbg = calculated_stats["debug"]
        with st.expander("🔎 Detailed serve/return calculations (pg via regression vs pd vs final)", expanded=False):
            rows = [
                [dbg["playerA"], "Serve", "1st Serve In", 
                 pct(dbg["A_1stIn_pg"]), 
                 pct(dbg["A_1stIn_pd"]), 
                 pct(dbg["A_1stIn_final"]),
                 dbg["A_regression_1stIn"]],
                
                [dbg["playerA"], "Serve", "1st Serve Win", 
                 pct(dbg["A_1stWin_pg"]), 
                 pct(dbg["A_1stWin_pd"]), 
                 pct(dbg["A_1stWin_final"]),
                 dbg["A_regression_1stWin"]],
                
                [dbg["playerA"], "Serve", "2nd Serve Win", 
                 pct(dbg["A_2ndWin_pg"]), 
                 pct(dbg["A_2ndWin_pd"]), 
                 pct(dbg["A_2ndWin_final"]),
                 dbg["A_regression_2ndWin"]],
                
                [dbg["playerA"], "Return", "1st Serve Return Win", 
                 pct(dbg["A_1stWin_return_pg"]), 
                 "", 
                 "",
                 dbg["A_regression_return_1st"]],
                
                [dbg["playerA"], "Return", "2nd Serve Return Win", 
                 pct(dbg["A_2ndWin_return_pg"]), 
                 "", 
                 "",
                 dbg["A_regression_return_2nd"]],

                [dbg["playerB"], "Serve", "1st Serve In", 
                 pct(dbg["B_1stIn_pg"]), 
                 pct(dbg["B_1stIn_pd"]), 
                 pct(dbg["B_1stIn_final"]),
                 dbg["B_regression_1stIn"]],
                
                [dbg["playerB"], "Serve", "1st Serve Win", 
                 pct(dbg["B_1stWin_pg"]), 
                 pct(dbg["B_1stWin_pd"]), 
                 pct(dbg["B_1stWin_final"]),
                 dbg["B_regression_1stWin"]],
                
                [dbg["playerB"], "Serve", "2nd Serve Win", 
                 pct(dbg["B_2ndWin_pg"]), 
                 pct(dbg["B_2ndWin_pd"]), 
                 pct(dbg["B_2ndWin_final"]),
                 dbg["B_regression_2ndWin"]],
                
                [dbg["playerB"], "Return", "1st Serve Return Win", 
                 pct(dbg["B_1stWin_return_pg"]), 
                 "", 
                 "",
                 dbg["B_regression_return_1st"]],
                
                [dbg["playerB"], "Return", "2nd Serve Return Win", 
                 pct(dbg["B_2ndWin_return_pg"]), 
                 "", 
                 "",
                 dbg["B_regression_return_2nd"]],
            ]
            df_dbg = pd.DataFrame(rows, columns=["Player", "Type", "Metric", "pg (regression)", "pd (H2H)", "final", "Regression Info"])
            st.dataframe(df_dbg, use_container_width=True, hide_index=True)
            st.markdown(f"**weight_d (H2H weight):** `{dbg['weight_d']:.3f}`")
            st.markdown("**Note:** pg values are now calculated using linear regression: `stat = slope × opponent_ELO + intercept`")

    # Defaults for MC inputs
    if calculated_stats:
        p1_first_in_default = safe_stat_value(calculated_stats.get(f"{player1}_1stIn"), DEFAULTS["player1_first_in"])
        p1_first_win_default = safe_stat_value(calculated_stats.get(f"{player1}_1stWin"), DEFAULTS["player1_first_win"])
        p1_second_win_default = safe_stat_value(calculated_stats.get(f"{player1}_2ndWin"), DEFAULTS["player1_second_win"])
        p2_first_in_default = safe_stat_value(calculated_stats.get(f"{player2}_1stIn"), DEFAULTS["player2_first_in"])
        p2_first_win_default = safe_stat_value(calculated_stats.get(f"{player2}_1stWin"), DEFAULTS["player2_first_win"])
        p2_second_win_default = safe_stat_value(calculated_stats.get(f"{player2}_2ndWin"), DEFAULTS["player2_second_win"])
    else:
        p1_first_in_default = DEFAULTS["player1_first_in"]
        p1_first_win_default = DEFAULTS["player1_first_win"]
        p1_second_win_default = DEFAULTS["player1_second_win"]
        p2_first_in_default = DEFAULTS["player2_first_in"]
        p2_first_win_default = DEFAULTS["player2_first_win"]
        p2_second_win_default = DEFAULTS["player2_second_win"]

    st.markdown("### Serve Statistics Input")
    st.markdown("*Values are pre-filled from linear regression predictions based on opponent ELO. You can adjust them manually.*")

    col_stats1, col_stats2 = st.columns(2)
    with col_stats1:
        st.markdown(f"**{player1}**")
        p1_first_in = st.number_input(
            "% 1st Serve In", 0.0, 100.0, float(p1_first_in_default) * 100, 0.5,
            key=f"p1_first_in_{player1}"
        ) / 100.0
        p1_first_win = st.number_input(
            "% 1st Serve Win", 0.0, 100.0, float(p1_first_win_default) * 100, 0.5,
            key=f"p1_first_win_{player1}"
        ) / 100.0
        p1_second_win = st.number_input(
            "% 2nd Serve Win", 0.0, 100.0, float(p1_second_win_default) * 100, 0.5,
            key=f"p1_second_win_{player1}"
        ) / 100.0

    with col_stats2:
        st.markdown(f"**{player2}**")
        p2_first_in = st.number_input(
            "% 1st Serve In", 0.0, 100.0, float(p2_first_in_default) * 100, 0.5,
            key=f"p2_first_in_{player2}"
        ) / 100.0
        p2_first_win = st.number_input(
            "% 1st Serve Win", 0.0, 100.0, float(p2_first_win_default) * 100, 0.5,
            key=f"p2_first_win_{player2}"
        ) / 100.0
        p2_second_win = st.number_input(
            "% 2nd Serve Win", 0.0, 100.0, float(p2_second_win_default) * 100, 0.5,
            key=f"p2_second_win_{player2}"
        ) / 100.0

    num_simulations = 10000

    if st.button("🚀 Run Monte Carlo Simulation", type="primary"):
        with st.spinner(f"Running {num_simulations:,} simulations..."):
            mc_prob1 = monte_carlo_simulation(
                p1_first_in, p1_first_win, p1_second_win,
                p2_first_in, p2_first_win, p2_second_win,
                num_simulations=num_simulations
            )
            mc_prob2 = 1 - mc_prob1

        st.markdown("---")
        st.subheader("📊 Simulation Results")

        col_mc1, col_mc2 = st.columns(2)
        with col_mc1:
            st.metric(
                f"Probability {player1} wins (MC)",
                f"{mc_prob1*100:.2f}%",
                delta=f"{(mc_prob1 - prob1)*100:+.2f}% vs ELO"
            )
        with col_mc2:
            st.metric(
                f"Probability {player2} wins (MC)",
                f"{mc_prob2*100:.2f}%",
                delta=f"{(mc_prob2 - prob2)*100:+.2f}% vs ELO"
            )

        st.markdown("### Comparison: ELO vs Monte Carlo")
        comparison_data = pd.DataFrame({
            "Method": [player1, player2],
            "ELO Prediction": [prob1 * 100, prob2 * 100],
            "Monte Carlo Simulation": [mc_prob1 * 100, mc_prob2 * 100],
        })
        st.bar_chart(comparison_data.set_index("Method"), height=400)

else:
    st.info("👈 Please select two different players to see win probability.")
