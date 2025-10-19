# Cryptocurrency Investment Dashboard

A comprehensive Streamlit application for cryptocurrency analysis and ML-based price predictions.

**Group 4 - AT3 Assignment**
**Course:** 36120 Advanced Machine Learning
**Institution:** University of Technology Sydney (UTS)

## Overview

This dashboard provides data-driven insights for cryptocurrency investors, featuring:
- Real-time price data for Bitcoin, Ethereum, XRP, and Solana
- Historical price analysis and visualization
- Technical analysis with popular indicators
- Machine Learning-based next-day high price predictions
- Market insights and trend analysis

## Features

### Supported Cryptocurrencies
- Bitcoin (BTC)
- Ethereum (ETH)
- XRP
- Solana (SOL)

### Analysis Tools
- **Overview & Prediction**: Current metrics and ML predictions
- **Historical Data**: Candlestick charts, volume analysis, and statistics
- **Technical Analysis**: Moving averages, RSI, and other indicators
- **Market Insights**: Volatility analysis, market cap trends, and key insights

## Project Structure

```
streamlit/
├── app/
│   └── main.py              # Main Streamlit application
├── students/
│   ├── student_bitcoin.py   # Bitcoin analysis module
│   ├── student_ethereum.py  # Ethereum analysis module (add your own)
│   ├── student_xrp.py       # XRP analysis module (add your own)
│   └── student_solana.py    # Solana analysis module (add your own)
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── Dockerfile              # Docker configuration
├── README.md               # This file
└── github.txt             # GitHub repository link
```

## Requirements

- Python 3.11.4
- Streamlit 1.36.0
- Pandas 2.2.2
- Plotly (for interactive charts)
- Requests (for API calls)

See [requirements.txt](requirements.txt) for complete list.

## Installation

### Local Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd streamlit
```

2. **Activate conda environment**
```powershell
conda activate adml-at3
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Run the application**

Using PowerShell script:
```powershell
.\run.ps1
```

Or using batch file:
```cmd
run.bat
```

Or manually:
```powershell
streamlit run app\main.py
```

5. **Access the dashboard**
- Open your browser to: http://localhost:8501

### Docker Setup

1. **Build Docker image**
```bash
docker build -t crypto-dashboard .
```

2. **Run container**
```bash
docker run -p 8501:8501 crypto-dashboard
```

3. **Access the dashboard**
- Open your browser to: http://localhost:8501

## Configuration

### FastAPI URL Configuration

Each student module needs to be configured with the correct FastAPI endpoint URL. Edit the `FASTAPI_URL` in your student module:

```python
# In students/student_bitcoin.py
FASTAPI_URL = "http://localhost:8000"  # Local development
# or
FASTAPI_URL = "https://your-api.onrender.com"  # Production
```

### API Data Sources

The app uses the following data sources:
- **CryptoCompare API**: Real-time cryptocurrency data (free tier, no API key required)
- **Student FastAPI endpoints**: ML model predictions

## Adding Student Modules

Each student should create their own module following this template:

1. **Create file**: `students/student_{cryptocurrency}.py`

2. **Implement required functions**:
   - `display_overview_and_prediction()`: Show current data and ML prediction
   - `display_historical_data()`: Display historical charts
   - `display_technical_analysis()`: Show technical indicators
   - `display_market_insights()`: Provide market analysis

3. **Reference the existing Bitcoin module** (`students/student_bitcoin.py`) for implementation details

4. **Update FastAPI URL** to point to your deployed model

## Deployment

### Streamlit Community Cloud

1. **Push code to GitHub**
```bash
git add .
git commit -m "Add Streamlit dashboard"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file path: `app/main.py`
   - Deploy

3. **Configure secrets** (if needed)
   - Add API keys or URLs in Streamlit Cloud settings

### Docker Deployment (Render/Other platforms)

1. **Ensure Dockerfile is configured**
2. **Push to GitHub**
3. **Create new Web Service on Render**
   - Select Docker runtime
   - Port: 8501
   - Deploy

## Usage

1. **Select Cryptocurrency**: Use the sidebar dropdown to choose Bitcoin, Ethereum, XRP, or Solana

2. **Navigate Tabs**:
   - **Overview & Prediction**: View current price and ML prediction
   - **Historical Data**: Analyze price trends over different time periods
   - **Technical Analysis**: Review moving averages and RSI
   - **Market Insights**: Understand volatility and market trends

3. **Interpret Predictions**:
   - Green arrow: Bullish prediction (price expected to rise)
   - Red arrow: Bearish prediction (price expected to fall)
   - Percentage: Expected change from current price

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/ students/
```

### Linting
```bash
flake8 app/ students/
```

## Assignment Requirements Checklist

- [x] Streamlit app with cryptocurrency selection
- [x] Historical data display via API calls
- [x] ML model predictions integration
- [x] Separate student modules in `students/` folder
- [x] `requirements.txt` with all dependencies
- [x] `pyproject.toml` for project configuration
- [x] `Dockerfile` for containerization
- [x] `README.md` with setup instructions
- [x] Modular structure for team collaboration

## Data Sources

- **CryptoCompare API**: https://min-api.cryptocompare.com/
  - Historical OHLCV data
  - Real-time price updates
  - No API key required for basic usage

## Troubleshooting

### Streamlit Won't Start
- Ensure Python 3.11.4 is installed
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify port 8501 is not in use

### Prediction Not Loading
- Check FastAPI service is running
- Verify `FASTAPI_URL` in student module is correct
- Check network connectivity to API endpoint

### Data Not Displaying
- Verify internet connection (for API calls)
- Check CryptoCompare API is accessible
- Review browser console for errors

### Docker Issues
- Ensure Docker daemon is running
- Check port 8501 is available
- Verify all files are copied correctly in Dockerfile

## Contributing

### For Team Members

1. Create your student module for your assigned cryptocurrency
2. Follow the function structure in `student_bitcoin.py`
3. Update `FASTAPI_URL` to your deployed API
4. Test locally before pushing
5. Update this README if you add new features

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

## License

This project is for educational purposes as part of UTS coursework.

## Team Members

- Student 1: Bitcoin (BTC) - Linear Regression
- Student 2: [Cryptocurrency] - [Algorithm]
- Student 3: [Cryptocurrency] - [Algorithm]
- Student 4: [Cryptocurrency] - [Algorithm]

## Links

- **Main Repository**: https://github.com/tooichitake/cryptocurrency-service
- **Live Dashboard**: https://your-app.streamlit.app
- **Live APIs**:
  - Bitcoin: https://bitcoin-api.onrender.com
  - [Others]: [URLs]

## Acknowledgments

- **Course**: 36120 Advanced Machine Learning
- **Institution**: University of Technology Sydney (UTS)
- **Assignment**: AT3 - Data Product with Machine Learning
- **APIs**: CryptoCompare for cryptocurrency data

## Disclaimer

This dashboard is for educational purposes only and should not be considered as financial advice. Cryptocurrency investments carry significant risks. Always do your own research and consult with financial advisors before making investment decisions.

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review assignment requirements document
- Contact team members
- Consult course instructors

---

**Built with Streamlit | 36120 Advanced Machine Learning - UTS | Group 4**
