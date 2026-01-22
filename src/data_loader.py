"""
Data loading functions for tennis statistics
"""
import pandas as pd
import os


def load_elo_data():
    """Load ELO ratings data"""
    csv_path = os.path.join("tables_csv", "elo_players.csv")
    return pd.read_csv(csv_path)


def load_overview_data():
    """Load overview statistics CSV and extract match_date from match_id"""
    csv_path = os.path.join("tables_csv", "charting-m-stats-Overview.csv")
    df = pd.read_csv(csv_path)
    df["match_date"] = df["match_id"].astype(str).str[:8]
    df = df[df["match_date"].str.match(r"^\d{8}$", na=False)].copy()
    df = df[df["set"] == "Total"].copy()
    return df


def load_ao_players():
    """Load Australian Open players list"""
    csv_path = os.path.join("tables_csv", "ao_players.csv")
    ao_df = pd.read_csv(csv_path)
    if "Player" in ao_df.columns:
        return set(ao_df["Player"].dropna().unique())
    return set(ao_df[ao_df.columns[0]].dropna().unique())
