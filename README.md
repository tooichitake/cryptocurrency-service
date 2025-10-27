# 📈 Cryptocurrency Investment Dashboard

> A comprehensive Streamlit application for cryptocurrency analysis and ML-based price predictions.

[![Python](https://img.shields.io/badge/Python-3.11.4-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](#license)

---

## 🎯 Overview

This dashboard provides data-driven insights for cryptocurrency investors, featuring:

- 💹 **Real-time price data** for Bitcoin, Ethereum, XRP, and Solana
- 📊 **Historical price analysis** with interactive visualizations
- 📉 **Technical indicators** - Moving averages, RSI, Bollinger Bands, and more
- 🤖 **Machine Learning predictions** - Next-day high price forecasts
- 📈 **Market insights** - Volatility analysis and trend indicators

## ✨ Features

### 💰 Supported Cryptocurrencies

| Cryptocurrency | Status | ML Prediction |
|----------------|--------|---------------|
| 🟠 Bitcoin (BTC) | ✅ Active | ✅ Available |
| 🔵 Ethereum (ETH) | 🔜 Coming soon | - |
| ⚪ XRP | 🔜 Coming soon | - |
| 🟣 Solana (SOL) | 🔜 Coming soon | - |

### 📊 Analysis Tools

| Tool | Description |
|------|-------------|
| **Overview & Prediction** | Current metrics and ML-powered next-day predictions |
| **Historical Data** | Interactive candlestick charts and volume analysis |
| **Technical Analysis** | Moving averages, RSI, MACD, Bollinger Bands |
| **Market Insights** | Volatility metrics, market cap trends, and signals |

## 📁 Project Structure

```
cryptocurrency-service/
├── app/
│   └── main.py                    # Main Streamlit application
├── students/
│   └── 25605217.py                # Bitcoin analysis module
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
├── Dockerfile                     # Docker configuration
└── README.md                      # This file
```

## 🔧 Requirements

- Python 3.11.4
- Streamlit 1.36.0
- Pandas 2.2.2
- Plotly (for interactive charts)
- Requests (for API calls)

See [requirements.txt](requirements.txt) for complete list.

## 🚀 Installation & Usage

### Quick Start

```bash
# 1️⃣ Clone the repository
git clone https://github.com/tooichitake/cryptocurrency-service.git
cd cryptocurrency-service

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Run the dashboard
streamlit run app/main.py

# 4️⃣ Open your browser at http://localhost:8501
```

### 🐳 Docker Setup

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

## 📡 Data Sources

- **CryptoCompare API**: Real-time cryptocurrency data (free tier, no API key required)

## 🏗️ Technical Architecture

The application uses a modular architecture:

- **Streamlit Frontend**: Interactive dashboard for data visualization
- **ML Models**: Linear Regression model for Bitcoin price prediction
- **Data Pipeline**: Real-time data fetching from CryptoCompare API
- **Prediction API**: External RESTful API for model predictions

## 🌐 Deployment

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

### Docker Deployment (Optional)

1. **Ensure Dockerfile is configured**
2. **Push to GitHub**
3. **Create new Web Service on Render**
   - Select Docker runtime
   - Port: 8501
   - Deploy

## 📖 Usage

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

## 🛠️ Development

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


## ⚠️ Troubleshooting

### Streamlit Won't Start
- Ensure Python 3.11.4 is installed
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify port 8501 is not in use

### Prediction Not Loading
- Check network connectivity to prediction API endpoint
- Verify API service is accessible

### Data Not Displaying
- Verify internet connection (for API calls)
- Check CryptoCompare API is accessible
- Review browser console for errors

### Docker Issues
- Ensure Docker daemon is running
- Check port 8501 is available
- Verify all files are copied correctly in Dockerfile


## 📄 License

This project is for educational purposes only.

## 🔗 Links

- **Repository**: https://github.com/tooichitake/cryptocurrency-service
- **Live Dashboard**: [Coming soon]

## 🙏 Acknowledgments

- **Data Provider**: CryptoCompare API for cryptocurrency market data

## ⚠️ Disclaimer

This dashboard is for educational purposes only and should not be considered as financial advice. Cryptocurrency investments carry significant risks. Always do your own research and consult with financial advisors before making investment decisions.

## 💬 Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Open an issue on [GitHub](https://github.com/tooichitake/cryptocurrency-service/issues)

---

**Built with Streamlit & Python**
