# Data Structure Examples

This document shows the expected structure for each CSV file.

## elo_players.csv

Required columns:
- `Player`: Player full name (string)
- `Elo`: Current ELO rating (float)
- `hElo`: Hard court ELO rating (float)

Example:
```csv
Player,Elo,hElo
Novak Djokovic,2100.5,2050.3
Carlos Alcaraz,2080.2,2075.1
Jannik Sinner,2070.8,2090.5
Daniil Medvedev,2065.3,2080.2
Alexander Zverev,2045.7,2040.8
```

The app will average `Elo` and `hElo` to get the final ELO rating used in calculations.

## charting-m-stats-Overview.csv

Required columns:
- `match_id`: Unique identifier for each match (format: YYYYMMDD_tournament_round)
- `player`: Player name (must match names in elo_players.csv)
- `set`: Set information (must include rows where set="Total")
- `serve_pts`: Total serve points
- `first_in`: First serves in
- `first_won`: First serve points won
- `second_in`: Second serves in (total serves - first serves in)
- `second_won`: Second serve points won

Example:
```csv
match_id,player,set,serve_pts,first_in,first_won,second_in,second_won,aces,dfs,break_pts,break_pts_won
20240115_AO_R1,Novak Djokovic,Total,120,78,62,42,28,8,2,5,3
20240115_AO_R1,Rafael Nadal,Total,115,70,55,45,25,6,3,4,2
20240116_AO_R1,Carlos Alcaraz,Total,125,85,68,40,22,10,1,6,4
20240116_AO_R1,Felix Auger Aliassime,Total,130,82,60,48,26,7,4,5,2
```

Notes:
- Each match has two rows (one per player)
- The `set="Total"` rows contain aggregate statistics for the entire match
- `match_id` must start with 8 digits (YYYYMMDD format)
- All numeric columns should be integers or floats

## ao_players.csv

Simple list of player names for filtering.

Required columns:
- `Player`: Player full name (must match names in other CSV files)

Example:
```csv
Player
Novak Djokovic
Carlos Alcaraz
Jannik Sinner
Daniil Medvedev
Alexander Zverev
Taylor Fritz
Casper Ruud
Andrey Rublev
Holger Rune
Grigor Dimitrov
```

## Data Quality Requirements

### Player Names
- Must be **exactly consistent** across all three CSV files
- Watch for:
  - Extra spaces
  - Different name formats (e.g., "Rafael Nadal" vs "R. Nadal")
  - Accents and special characters
  - Case sensitivity

### Match Statistics
- `serve_pts` should equal `first_in + second_in` approximately
- `first_won` should be ≤ `first_in`
- `second_won` should be ≤ `second_in`
- Values should be realistic percentages when calculated:
  - First serve in: typically 55-70%
  - First serve won: typically 65-80%
  - Second serve won: typically 45-60%

### Date Format
- Match IDs must start with `YYYYMMDD` (8 digits)
- Example: `20240115` for January 15, 2024
- Invalid: `2024115`, `24-01-15`, `01/15/2024`

## Minimum Data Requirements

For the app to work properly, you need:
- At least 3-5 players in all three CSV files
- At least 20-30 matches per player for reliable regression
- Matches against various opponents with different ELO ratings

## Data Sources

Possible sources for tennis data:
- Tennis Abstract (www.tennisabstract.com)
- ATP Tour website
- Match Charting Project
- Custom data collection

## Validation Script

You can validate your data with this Python script:

```python
import pandas as pd

# Load data
elo_df = pd.read_csv("matches_csv/elo_players.csv")
overview_df = pd.read_csv("matches_csv/charting-m-stats-Overview.csv")
ao_df = pd.read_csv("matches_csv/ao_players.csv")

# Check columns
print("ELO columns:", elo_df.columns.tolist())
print("Overview columns:", overview_df.columns.tolist())
print("AO columns:", ao_df.columns.tolist())

# Check player name consistency
elo_players = set(elo_df['Player'].unique())
overview_players = set(overview_df['player'].unique())
ao_players = set(ao_df['Player'].unique())

print(f"\nPlayers in ELO: {len(elo_players)}")
print(f"Players in Overview: {len(overview_players)}")
print(f"Players in AO: {len(ao_players)}")

# Check for mismatches
in_ao_not_elo = ao_players - elo_players
in_ao_not_overview = ao_players - overview_players

if in_ao_not_elo:
    print("\nWarning: Players in AO list but not in ELO:", in_ao_not_elo)
if in_ao_not_overview:
    print("Warning: Players in AO list but not in Overview:", in_ao_not_overview)

# Check data quality
print("\n--- Data Quality Checks ---")
print(f"Matches with Total stats: {len(overview_df[overview_df['set'] == 'Total'])}")
print(f"Date format check: {overview_df['match_id'].astype(str).str[:8].str.match(r'^\d{8}$').sum()} valid dates")

# Check for NaN values
print("\nMissing values in Overview:")
print(overview_df[['serve_pts', 'first_in', 'first_won', 'second_in', 'second_won']].isna().sum())
```
