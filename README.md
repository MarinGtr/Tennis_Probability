# 🎾 Tennis Probability Calculator

A Streamlit application for calculating tennis match win probabilities using ELO ratings, historical statistics, and Monte Carlo simulations.

## Features

- **ELO-based Predictions**: Calculate win probabilities using player ELO ratings
- **Linear Regression Analysis**: Predict player performance based on opponent strength
- **Monte Carlo Simulations**: Simulate thousands of matches to estimate win probabilities
- **Historical Data Integration**: Use real match data to inform predictions
- **Head-to-Head Analysis**: Incorporate direct matchup history

## Project Structure

```
tennis_app/
├── app.py                          # Main Streamlit application
├── src/
│   ├── __init__.py                # Package initialization
│   ├── data_loader.py             # Data loading functions
│   ├── utils.py                   # Utility functions
│   ├── probability_calculator.py  # ELO-based probability calculations
│   ├── monte_carlo.py             # Monte Carlo simulation engine
│   ├── regression.py              # Linear regression for player stats
│   └── stats_calculator.py        # Player statistics calculation
├── matches_csv/                   # Data directory (not included)
│   ├── elo_players.csv           # Player ELO ratings
│   ├── charting-m-stats-Overview.csv  # Match statistics
│   └── ao_players.csv            # Australian Open players list
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd tennis_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Prepare your data:
   - Create a `matches_csv/` directory in the project root
   - Add the required CSV files:
     - `elo_players.csv`: Player ELO ratings with columns `Player`, `Elo`, `hElo`
     - `charting-m-stats-Overview.csv`: Match statistics
     - `ao_players.csv`: List of players

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser. Select two players from the sidebar to:
1. View ELO-based win probabilities
2. See calculated serve statistics using linear regression
3. Adjust serve statistics manually if needed
4. Run Monte Carlo simulations to estimate win probabilities

## Methodology

### Player Statistics (pg - Player General)

The application uses **linear regression** to predict player performance based on opponent ELO:

```
stat = slope × opponent_ELO + intercept
```

For each player, we calculate:
- 1st Serve In %
- 1st Serve Win %
- 2nd Serve Win %
- Return 1st Serve Win %
- Return 2nd Serve Win %

### Head-to-Head Statistics (pd - Player Direct)

Direct matchup history is calculated using exponentially weighted averages with a configurable half-life.

### Final Statistics

The final statistics blend pg (regression-based) and pd (H2H) using a dynamic weight:

```
weight_d = n / (d_param + n)
final_stat = weight_d × pd + (1 - weight_d) × pg
```

Where:
- `n` is the number of H2H serve points
- `d_param` is a tunable parameter (default: 150)

## Data Requirements

### elo_players.csv
```csv
Player,Elo,hElo
Novak Djokovic,2100,2050
Rafael Nadal,2080,2030
...
```

### charting-m-stats-Overview.csv
Must include columns:
- `match_id`: Unique match identifier
- `player`: Player name
- `set`: Set information (should include "Total")
- `serve_pts`, `first_in`, `first_won`, `second_in`, `second_won`: Serve statistics

### ao_players.csv
```csv
Player
Novak Djokovic
Carlos Alcaraz
...
```

## Configuration

Key parameters in the application:
- `halflife_pd`: Half-life for H2H exponential weighting (default: 360 days)
- `d_param`: Blending parameter between pd and pg (default: 150)
- `num_simulations`: Number of Monte Carlo simulations (default: 10,000)

## Deployment to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository and branch
5. Set the main file path to `app.py`
6. Deploy!

**Important**: Make sure to include your `matches_csv` data in your repository or configure data loading from an external source.

## Dependencies

- `streamlit`: Web application framework
- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `scikit-learn`: Linear regression models

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

[Your Contact Information]
