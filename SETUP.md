# Setup Instructions

## Local Development

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare Data
Create a `matches_csv/` directory and add your CSV files:
- `elo_players.csv`
- `charting-m-stats-Overview.csv`
- `ao_players.csv`

### 4. Run the App
```bash
streamlit run app.py
```

## Deployment to Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)

### Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets (if needed)**
   If you need to load data from external sources or use API keys:
   - Go to your app settings on Streamlit Cloud
   - Add secrets in TOML format

### Data Considerations

**Option 1: Include data in repository** (if not too large)
- Keep `matches_csv/` in your repo
- Make sure it's not in `.gitignore`

**Option 2: Load from external source**
- Modify `src/data_loader.py` to load from:
  - Cloud storage (AWS S3, Google Cloud Storage)
  - URL endpoints
  - Database

Example for loading from URL:
```python
def load_elo_data():
    url = "https://your-data-source.com/elo_players.csv"
    return pd.read_csv(url)
```

## Environment Variables

If you need environment variables, create a `.streamlit/secrets.toml` file locally:

```toml
# .streamlit/secrets.toml
data_source = "local"  # or "remote"
api_key = "your-api-key-here"
```

On Streamlit Cloud, add these in the app settings under "Secrets".

## Troubleshooting

### Import Errors
If you get import errors, make sure:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. You're running from the project root directory

### Data Loading Errors
1. Check that `matches_csv/` directory exists
2. Verify CSV files have correct names and format
3. Check file permissions

### Streamlit Cloud Deployment Issues
1. Ensure `requirements.txt` is at root level
2. Check that `app.py` is at root level
3. Verify all imports use relative paths
4. Check Streamlit Cloud logs for specific errors

## Performance Optimization

For large datasets:
1. Use caching with `@st.cache_data` decorator (already implemented in `data_loader.py`)
2. Consider pre-computing regression models
3. Reduce number of Monte Carlo simulations for faster results

## Testing

To test the app locally before deployment:
```bash
# Test data loading
python -c "from src.data_loader import load_elo_data; print(load_elo_data().head())"

# Test calculations
python -c "from src.probability_calculator import calculate_win_probability; print(calculate_win_probability(2000, 1900))"
```
