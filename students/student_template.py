"""
[Cryptocurrency] Analysis Module - Student Implementation Template
Displays historical data, predictions, and technical analysis for [Cryptocurrency]

Student: [Your Name]
Model: [Your ML Algorithm]
Cryptocurrency: [Your Cryptocurrency]
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Configuration
FASTAPI_URL = "http://localhost:8000"  # TODO: Update with your deployed FastAPI URL
CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data/v2/histoday"

# TODO: Update these with your cryptocurrency details
CRYPTO_SYMBOL = "BTC"  # Change to ETH, XRP, SOL, etc.
CRYPTO_NAME = "Bitcoin"  # Change to Ethereum, XRP, Solana, etc.


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_crypto_data(days=365):
    """
    Fetch cryptocurrency historical data from CryptoCompare API

    Args:
        days: Number of days of historical data to fetch

    Returns:
        DataFrame with OHLCV data
    """
    try:
        response = requests.get(
            CRYPTOCOMPARE_API,
            params={
                'fsym': CRYPTO_SYMBOL,
                'tsym': 'USD',
                'limit': days,
                'toTs': int(datetime.now().timestamp())
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        if data.get('Response') != 'Success':
            st.error(f"API Error: {data.get('Message', 'Unknown error')}")
            return None

        df = pd.DataFrame(data['Data']['Data'])
        df['date'] = pd.to_datetime(df['time'], unit='s')
        df = df.rename(columns={'volumefrom': 'volume'})
        df['marketCap'] = df['close'] * df['volume']

        return df[['date', 'open', 'high', 'low', 'close', 'volume', 'marketCap']].sort_values('date').reset_index(drop=True)

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_prediction():
    """
    Get next-day high price prediction from your FastAPI

    Returns:
        Dictionary with prediction data
    """
    try:
        # TODO: Update endpoint path if needed
        response = requests.get(
            f"{FASTAPI_URL}/predict/{CRYPTO_SYMBOL.lower()}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to prediction API: {str(e)}")
        return None


def display_overview_and_prediction():
    """
    Display overview and ML prediction

    TODO: Customize this function with your own visualizations and insights
    """
    st.markdown(f"### {CRYPTO_NAME} Price Overview & Prediction")

    # Fetch current data
    df = fetch_crypto_data(days=30)

    if df is not None and not df.empty:
        latest = df.iloc[-1]

        # Display current metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Current Price",
                f"${latest['close']:,.2f}",
                f"{((latest['close'] - df.iloc[-2]['close']) / df.iloc[-2]['close'] * 100):.2f}%"
            )

        with col2:
            st.metric("24h High", f"${latest['high']:,.2f}")

        with col3:
            st.metric("24h Low", f"${latest['low']:,.2f}")

        with col4:
            st.metric("24h Volume", f"{latest['volume']:,.0f} {CRYPTO_SYMBOL}")

        st.markdown("---")

        # ML Prediction Section
        st.markdown("### Machine Learning Prediction")

        with st.spinner("Fetching prediction from ML model..."):
            prediction_data = get_prediction()

        if prediction_data and 'prediction' in prediction_data:
            predicted_price = prediction_data['prediction']

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("#### Next-Day High Price Prediction")
                st.markdown(f"<h2 style='color: #1f77b4;'>${predicted_price:,.2f}</h2>", unsafe_allow_html=True)

                current_price = latest['close']
                change_pct = ((predicted_price - current_price) / current_price) * 100
                direction = "📈 Bullish" if change_pct > 0 else "📉 Bearish"

                st.markdown(f"**Direction:** {direction}")
                st.markdown(f"**Expected Change:** {change_pct:+.2f}%")
                st.markdown(f"**Current Price:** ${current_price:,.2f}")

            with col2:
                # TODO: Add your own prediction visualization
                fig = go.Figure()
                recent_df = df.tail(7)

                fig.add_trace(go.Scatter(
                    x=recent_df['date'],
                    y=recent_df['close'],
                    mode='lines+markers',
                    name='Historical Close',
                    line=dict(color='#1f77b4', width=2)
                ))

                next_day = recent_df['date'].iloc[-1] + timedelta(days=1)
                fig.add_trace(go.Scatter(
                    x=[recent_df['date'].iloc[-1], next_day],
                    y=[recent_df['close'].iloc[-1], predicted_price],
                    mode='lines+markers',
                    name='Prediction',
                    line=dict(color='#ff7f0e', width=2, dash='dash'),
                    marker=dict(size=10, symbol='star')
                ))

                fig.update_layout(
                    title='7-Day Price Trend + Prediction',
                    xaxis_title='Date',
                    yaxis_title='Price (USD)',
                    hovermode='x unified',
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

            # Model information
            with st.expander("Model Information"):
                st.markdown(f"""
                **Algorithm:** [Your ML Algorithm]

                **Features:** [Describe your features]

                **Training Data:** [Describe your training data]

                **Target:** Next-day high price (USD)

                **Model Performance:**
                - [Add your metrics, e.g., RMSE, MAE, R²]

                **Data Source:** CryptoCompare API (real-time data)
                """)

        else:
            st.warning("Unable to fetch prediction. Please ensure the FastAPI service is running.")
            st.code(f"FastAPI URL: {FASTAPI_URL}")

    else:
        st.error(f"Unable to fetch {CRYPTO_NAME} data. Please try again later.")


def display_historical_data():
    """
    Display historical price data and charts

    TODO: Customize with your own analysis
    """
    st.markdown("### Historical Price Data")

    time_range = st.selectbox(
        "Select Time Range",
        ["30 Days", "90 Days", "180 Days", "1 Year"],
        index=1
    )

    days_map = {"30 Days": 30, "90 Days": 90, "180 Days": 180, "1 Year": 365}
    days = days_map[time_range]

    df = fetch_crypto_data(days=days)

    if df is not None and not df.empty:
        # TODO: Add your own historical data visualizations

        # Example: Candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        )])

        fig.update_layout(
            title=f'{CRYPTO_NAME} Price - Last {time_range}',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            height=500,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # TODO: Add more visualizations and analysis

    else:
        st.error("Unable to fetch historical data.")


def display_technical_analysis():
    """
    Display technical analysis indicators

    TODO: Add your own technical indicators and analysis
    """
    st.markdown("### Technical Analysis")

    df = fetch_crypto_data(days=180)

    if df is not None and not df.empty:
        # TODO: Calculate and display your technical indicators

        # Example: Simple Moving Averages
        df['SMA_7'] = df['close'].rolling(window=7).mean()
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['close'], name='Close', line=dict(color='black')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['SMA_7'], name='SMA 7', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['SMA_20'], name='SMA 20', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['SMA_50'], name='SMA 50', line=dict(color='red')))

        fig.update_layout(
            title='Price with Moving Averages',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # TODO: Add more technical analysis

    else:
        st.error("Unable to fetch data for technical analysis.")


def display_market_insights():
    """
    Display market insights and additional analysis

    TODO: Add your own market insights and analysis
    """
    st.markdown("### Market Insights")

    df = fetch_crypto_data(days=365)

    if df is not None and not df.empty:
        # TODO: Add your own market insights

        # Example: Price changes
        col1, col2, col3 = st.columns(3)

        latest_price = df['close'].iloc[-1]
        price_7d = df['close'].iloc[-7] if len(df) >= 7 else df['close'].iloc[0]
        price_30d = df['close'].iloc[-30] if len(df) >= 30 else df['close'].iloc[0]
        price_90d = df['close'].iloc[-90] if len(df) >= 90 else df['close'].iloc[0]

        with col1:
            change_7d = ((latest_price - price_7d) / price_7d) * 100
            st.metric("7-Day Change", f"{change_7d:+.2f}%")

        with col2:
            change_30d = ((latest_price - price_30d) / price_30d) * 100
            st.metric("30-Day Change", f"{change_30d:+.2f}%")

        with col3:
            change_90d = ((latest_price - price_90d) / price_90d) * 100
            st.metric("90-Day Change", f"{change_90d:+.2f}%")

        # TODO: Add more insights

        st.markdown("---")
        st.warning("""
        **Disclaimer:** This analysis is for educational purposes only. Not financial advice.
        """)

    else:
        st.error("Unable to fetch data for market insights.")


# TODO: Add any additional helper functions you need
