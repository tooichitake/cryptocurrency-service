"""
Solana Analysis Module - Vanilla LSTM Model
Student ID: 25657673
Model: Vanilla LSTM (128 units)
Cryptocurrency: Solana (SOL)
Features: 31 engineered features from 23-step preprocessing pipeline
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# Configuration
FASTAPI_URL = "https://solana-lstm-api-25657673.onrender.com"  # Deployed FastAPI on Render
CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data/v2/histoday"
CRYPTOCOMPARE_NEWS_API = "https://min-api.cryptocompare.com/data/v2/news/"


@st.cache_data(ttl=300)
def fetch_solana_data(days=365):
    """
    Fetch Solana historical data from CryptoCompare API
    
    Note: CryptoCompare uses UTC timezone as standard.
    Daily data points are at 00:00:00 UTC.
    Data refreshes every 5 minutes (TTL=300s).
    """
    try:
        from datetime import timezone
        utc_now = datetime.now(timezone.utc)
        
        response = requests.get(
            CRYPTOCOMPARE_API,
            params={
                'fsym': 'SOL',
                'tsym': 'USD',
                'limit': days,
                'toTs': int(utc_now.timestamp())
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
    Get next-day high price prediction from FastAPI
    
    Returns prediction from Vanilla LSTM model with 31 features
    """
    try:
        response = requests.get(
            f"{FASTAPI_URL}/predict/SOL",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to prediction API: {str(e)}")
        return None


@st.cache_data(ttl=600)
def fetch_solana_news(limit=20):
    """
    Fetch Solana news from CryptoCompare API
    
    Returns the latest Solana-related news articles.
    Cache for 10 minutes (600s).
    """
    try:
        response = requests.get(
            CRYPTOCOMPARE_NEWS_API,
            params={
                'lang': 'EN',
                'categories': 'SOL',
                'excludeCategories': 'Sponsored'
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('Type') == 100:
            news_list = data.get('Data', [])[:limit]
            return news_list
        else:
            st.error(f"News API Error: {data.get('Message', 'Unknown error')}")
            return []
    
    except Exception as e:
        st.warning(f"Unable to fetch news: {str(e)}")
        return []


def inject_coinbase_css():
    """Inject Coinbase-inspired CSS styling"""
    st.markdown("""
    <style>
        /* Global Coinbase font family */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        /* Hero price display */
        .price-hero {
            font-size: 3.5rem;
            font-weight: 700;
            color: #050F19;
            line-height: 1.2;
            margin: 8px 0;
        }
        .price-change-positive {
            color: #05B169;
            font-size: 1.5rem;
            font-weight: 600;
        }
        .price-change-negative {
            color: #DF5060;
            font-size: 1.5rem;
            font-weight: 600;
        }

        /* Stat cards matching Coinbase */
        .stat-card {
            background: #FAFBFC;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #E7EAED;
        }
        .stat-label {
            font-size: 0.875rem;
            color: #5B616E;
            font-weight: 500;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-value {
            font-size: 1.375rem;
            font-weight: 600;
            color: #050F19;
        }

        /* Prediction card with Coinbase blue gradient */
        .prediction-card {
            background: linear-gradient(135deg, #9945FF 0%, #14F195 100%);
            border-radius: 16px;
            padding: 28px;
            color: white;
            margin: 24px 0;
            box-shadow: 0 4px 12px rgba(153, 69, 255, 0.2);
        }
        .prediction-label {
            font-size: 0.875rem;
            opacity: 0.9;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .prediction-value {
            font-size: 2.75rem;
            font-weight: 700;
            margin-bottom: 12px;
        }
        .prediction-change {
            font-size: 1.25rem;
            font-weight: 600;
            opacity: 0.95;
        }

        /* Section headers */
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #050F19;
            margin: 32px 0 16px 0;
        }

        /* News card styling */
        .news-card {
            background: white;
            border: 1px solid #E7EAED;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            transition: all 0.2s;
            cursor: pointer;
        }
        .news-card:hover {
            background: #F7F8FA;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .news-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: #050F19;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        .news-meta {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 0.875rem;
            color: #5B616E;
            margin-bottom: 12px;
        }
        .news-source {
            font-weight: 600;
            color: #9945FF;
        }
        .news-body {
            color: #050F19;
            font-size: 0.9375rem;
            line-height: 1.6;
            margin-bottom: 12px;
        }
        .news-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .news-tag {
            background: #F0E6FF;
            color: #9945FF;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)


def display_overview():
    """Display Coinbase-style overview with current price and market stats"""
    
    inject_coinbase_css()
    
    # Fetch data
    df = fetch_solana_data(days=365)
    
    if df is None or df.empty:
        st.error("Unable to fetch Solana data. Please check your internet connection.")
        return
    
    latest = df.iloc[-1]
    prev_close = df.iloc[-2]['close']
    price_change = latest['close'] - prev_close
    price_change_pct = (price_change / prev_close) * 100
    is_positive = price_change >= 0
    
    # Hero price display
    change_symbol = "▲" if is_positive else "▼"
    change_class = "price-change-positive" if is_positive else "price-change-negative"
    
    from datetime import timezone
    latest_date_utc = pd.to_datetime(latest['date']).tz_localize(timezone.utc)
    data_time_str = latest_date_utc.strftime("%b %d, %Y")
    
    st.markdown(f"""
    <div style="margin-bottom: 32px;">
        <div class="price-hero">${latest['close']:,.2f}</div>
        <div class="{change_class}">
            {change_symbol} ${abs(price_change):,.2f} ({price_change_pct:+.2f}%)
        </div>
        <div style="color: #6B7280; font-size: 0.875rem; margin-top: 8px;">
            {data_time_str}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Market stats row
    col1, col2, col3, col4 = st.columns(4)
    
    mktcap_change_pct = price_change_pct
    prev_volume = df.iloc[-2]['volume']
    volume_change_pct = ((latest['volume'] - prev_volume) / prev_volume) * 100 if prev_volume > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Market Cap</div>
            <div class="stat-value">${latest['marketCap']/1e9:.2f}B</div>
            <div style="color: {'#05B169' if price_change_pct >= 0 else '#DF5060'}; font-size: 0.875rem; margin-top: 4px;">
                {'↗' if price_change_pct >= 0 else '↘'} {price_change_pct:+.2f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">24h Volume</div>
            <div class="stat-value">{latest['volume']:,.0f} SOL</div>
            <div style="color: {'#05B169' if volume_change_pct >= 0 else '#DF5060'}; font-size: 0.875rem; margin-top: 4px;">
                {'↗' if volume_change_pct >= 0 else '↘'} {volume_change_pct:+.2f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        high_change_pct = ((latest['high'] - prev_close) / prev_close) * 100
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">24h High</div>
            <div class="stat-value">${latest['high']:,.2f}</div>
            <div style="color: {'#05B169' if high_change_pct >= 0 else '#DF5060'}; font-size: 0.875rem; margin-top: 4px;">
                {'↗' if high_change_pct >= 0 else '↘'} {high_change_pct:+.2f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        low_change_pct = ((latest['low'] - prev_close) / prev_close) * 100
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">24h Low</div>
            <div class="stat-value">${latest['low']:,.2f}</div>
            <div style="color: {'#05B169' if low_change_pct >= 0 else '#DF5060'}; font-size: 0.875rem; margin-top: 4px;">
                {'↗' if low_change_pct >= 0 else '↘'} {low_change_pct:+.2f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Price chart section
    st.markdown('<div class="section-header">Price Chart</div>', unsafe_allow_html=True)
    
    # Time period selector
    time_period = st.radio(
        "Select time period",
        ["1D", "1W", "1M", "3M", "1Y", "All"],
        index=2,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    period_map = {
        "1D": 1,
        "1W": 7,
        "1M": 30,
        "3M": 90,
        "1Y": 365,
        "All": len(df)
    }
    display_days = period_map[time_period]
    df_chart = df.tail(display_days).copy()
    
    # Determine trend color (Solana gradient colors)
    trend_positive = df_chart['close'].iloc[-1] >= df_chart['close'].iloc[0]
    line_color = '#14F195' if trend_positive else '#9945FF'
    fill_color = 'rgba(20, 241, 149, 0.1)' if trend_positive else 'rgba(153, 69, 255, 0.1)'
    
    y_min = df_chart['close'].min()
    y_max = df_chart['close'].max()
    y_range = y_max - y_min
    y_padding = y_range * 0.1
    
    df_chart['pct_change'] = ((df_chart['close'] - df_chart['close'].iloc[0]) / df_chart['close'].iloc[0]) * 100
    df_chart['pct_change'] = df_chart['pct_change'].round(2)
    
    # Create price chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_chart['date'],
        y=df_chart['close'],
        mode='lines',
        name='Price',
        line=dict(color=line_color, width=2.5),
        fill='tonexty',
        fillcolor=fill_color,
        customdata=df_chart[['pct_change']].values,
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>Price: $%{y:,.2f}<br>Change: %{customdata[0]:+.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
            title=None,
            tickformat='%b %d',
            showspikes=True,
            spikemode='across+toaxis',
            spikesnap='cursor',
            spikedash='dot',
            spikecolor='rgba(0, 0, 0, 0.5)',
            spikethickness=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            showline=False,
            zeroline=False,
            title=None,
            range=[y_min - y_padding, y_max + y_padding],
            tickprefix='$',
            tickformat=',.0f',
            showspikes=True,
            spikemode='across+toaxis',
            spikesnap='cursor',
            spikedash='dot',
            spikecolor='rgba(0, 0, 0, 0.5)',
            spikethickness=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        showlegend=False,
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.5)",
            font_size=12,
            font_family="Arial, sans-serif",
            font_color="#050F19",
            bordercolor="rgba(0, 0, 0, 0.3)",
            align="left"
        ),
        hoverdistance=-1,
        spikedistance=-1
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance table
    st.markdown('<div class="section-header">Performance</div>', unsafe_allow_html=True)
    
    perf_data = []
    for period_name, days in [("24 Hours", 1), ("1 Week", 7), ("1 Month", 30), ("1 Year", 365)]:
        if len(df) > days:
            old_price = df.iloc[-days-1]['close']
            change = latest['close'] - old_price
            change_pct = (change / old_price) * 100
            perf_data.append({
                "Period": period_name,
                "Price": f"${old_price:,.2f}",
                "Change": f"${change:+,.2f} ({change_pct:+.2f}%)"
            })
    
    perf_df = pd.DataFrame(perf_data)
    st.dataframe(perf_df, use_container_width=True, hide_index=True)


def display_analysis_and_prediction():
    """Display integrated technical analysis and AI prediction"""
    
    inject_coinbase_css()
    
    df = fetch_solana_data(days=365)
    
    if df is None or df.empty:
        st.error("Unable to fetch Solana data")
        return
    
    # Display current price
    from datetime import timezone
    latest = df.iloc[-1]
    prev_close = df.iloc[-2]['close']
    price_change = latest['close'] - prev_close
    price_change_pct = (price_change / prev_close) * 100
    is_positive = price_change >= 0
    
    latest_date_utc = pd.to_datetime(latest['date']).tz_localize(timezone.utc)
    data_time_str = latest_date_utc.strftime("%b %d, %Y")
    
    change_symbol = "▲" if is_positive else "▼"
    change_class = "price-change-positive" if is_positive else "price-change-negative"
    
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: baseline; gap: 16px;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #050F19;">${latest['close']:,.2f}</div>
            <div class="{change_class}" style="font-size: 1.25rem;">
                {change_symbol} ${abs(price_change):,.2f} ({price_change_pct:+.2f}%)
            </div>
        </div>
        <div style="color: #6B7280; font-size: 0.875rem; margin-top: 8px; padding: 8px 12px; background-color: #F9FAFB; border-radius: 6px; display: inline-block;">
            {data_time_str}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Price Prediction Section
    st.markdown('<div class="section-header">AI Price Prediction</div>', unsafe_allow_html=True)
    
    st.info("""
    **Vanilla LSTM Model**
    - **Architecture**: 128-unit LSTM + Dropout(0.2) + Dense(1)
    - **Features**: 31 engineered features from 23-step preprocessing pipeline
    - **Training Data**: Solana historical data (2015-2025)
    - **Target**: Next-day high price prediction
    """)
    
    # Fetch prediction
    with st.spinner("Fetching AI prediction from LSTM model..."):
        prediction_data = get_prediction()
    
    if prediction_data:
        predicted_price = prediction_data.get('predicted_high_price')
        
        if predicted_price:
            current_price = latest['close']
            pred_change = predicted_price - current_price
            pred_change_pct = (pred_change / current_price) * 100
            is_bullish = pred_change > 0
            
            signal = "🚀 Bullish Signal" if is_bullish else "📉 Bearish Signal"
            st.markdown(f"""
            <div class="prediction-card">
                <div class="prediction-label">Next-Day High Price Prediction</div>
                <div class="prediction-value">${predicted_price:,.2f}</div>
                <div class="prediction-change">
                    {signal} | {pred_change_pct:+.2f}% from current price
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Model information
            with st.expander("📊 Model Performance Details"):
                st.markdown("""
                **Model Architecture:**
                - LSTM Layer: 128 units, tanh activation
                - Dropout Layer: 0.2 rate
                - Dense Output: 1 unit, linear activation
                - Total Parameters: 82,049
                
                **Feature Engineering:**
                - Total features created: 150+
                - Selected features: 31 (optimal subset)
                - Feature types: Technical indicators, momentum, volatility, price patterns, volume metrics
                
                **Preprocessing Pipeline (23 steps):**
                1. Data validation & integrity check
                2. Outlier detection (IQR + Z-score)
                3. Conservative outlier handling
                4. Time continuity validation
                5. Technical indicators (SMA, EMA, MACD, Bollinger Bands)
                6. Momentum indicators (RSI, Stochastic, ROC)
                7. Volatility indicators (ATR, Historical Volatility)
                8. Price features (spreads, ratios, gaps)
                9. Volume features (OBV, VWAP, Volume ratios)
                10-23. Time features, lag features, rolling features, missing value handling
                
                **Training Configuration:**
                - Timesteps: 60 days
                - Batch size: 32
                - Learning rate: 0.001
                - Optimizer: Adam
                - Callbacks: EarlyStopping + ReduceLROnPlateau
                
                **Data Source:**
                - Real-time data from Kraken API
                - 90 days rolling window for feature engineering
                """)
        else:
            st.warning("⚠️ Prediction data format error")
    else:
        st.warning("⚠️ Unable to connect to prediction API")
        st.info(f"""
        **Connection Issue**
        
        The prediction service is currently unavailable. Please ensure:
        - FastAPI service is running on `{FASTAPI_URL}`
        - Network connectivity is stable
        - API endpoint `/predict/SOL` is accessible
        
        **For Development:**
        Start the API with: `uvicorn app.main:app --reload --port 8000`
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Simple price history chart
    st.markdown('<div class="section-header">Recent Price History</div>', unsafe_allow_html=True)
    
    recent_df = df.tail(30)
    
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=recent_df['date'],
        open=recent_df['open'],
        high=recent_df['high'],
        low=recent_df['low'],
        close=recent_df['close'],
        name='SOL Price',
        increasing_line_color='#14F195',
        decreasing_line_color='#9945FF'
    ))
    
    fig.update_layout(
        title='Solana - Last 30 Days',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        height=500,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_market_insights():
    """Display market insights and statistics"""
    
    inject_coinbase_css()
    
    st.markdown('<div class="section-header">Market Insights</div>', unsafe_allow_html=True)
    
    df = fetch_solana_data(days=365)
    
    if df is None or df.empty:
        st.error("Unable to fetch market data")
        return
    
    latest = df.iloc[-1]
    df['daily_return'] = df['close'].pct_change()
    volatility = df['daily_return'].std() * np.sqrt(365) * 100
    
    # Market stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ytd_return = ((latest['close'] - df.iloc[0]['close']) / df.iloc[0]['close']) * 100
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">YTD Return</div>
            <div class="stat-value">{ytd_return:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Annualized Volatility</div>
            <div class="stat-value">{volatility:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_volume = df['volume'].mean()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Avg Daily Volume</div>
            <div class="stat-value">{avg_volume:,.0f} SOL</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        price_range = ((df['high'].max() - df['low'].min()) / df['low'].min()) * 100
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Price Range</div>
            <div class="stat-value">{price_range:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Monthly returns
    st.markdown('<div class="section-header">Monthly Returns</div>', unsafe_allow_html=True)
    
    df['month'] = df['date'].dt.to_period('M')
    monthly_returns = df.groupby('month').apply(
        lambda x: ((x['close'].iloc[-1] - x['close'].iloc[0]) / x['close'].iloc[0]) * 100
    ).reset_index()
    monthly_returns.columns = ['Month', 'Return (%)']
    monthly_returns['Month'] = monthly_returns['Month'].apply(lambda x: x.strftime('%b %Y'))
    
    st.dataframe(
        monthly_returns.tail(12),
        use_container_width=True,
        hide_index=True
    )
    
    # Key insights
    st.markdown('<div class="section-header">Key Insights</div>', unsafe_allow_html=True)
    
    st.info(f"""
    📊 **Market Summary**
    - Solana is currently trading at **${latest['close']:,.2f}**
    - The annualized volatility is **{volatility:.2f}%**, indicating {'high' if volatility > 50 else 'moderate'} market volatility
    - Year-to-date return: **{ytd_return:+.2f}%**
    - Average daily trading volume: **{avg_volume:,.0f} SOL**
    
    🔮 **AI Model Insights**
    - Uses **Vanilla LSTM** architecture with 128 units
    - Trained on **31 carefully engineered features**
    - **23-step preprocessing pipeline** ensures data quality
    - Predicts next-day high price with real-time data
    """)


def display_news():
    """Display latest Solana news from CryptoCompare"""
    
    inject_coinbase_css()
    
    st.markdown('<div class="section-header">Latest Solana News</div>', unsafe_allow_html=True)
    
    with st.spinner("Loading latest news..."):
        news_articles = fetch_solana_news(limit=15)
    
    if not news_articles:
        st.warning("Unable to fetch news at this time. Please try again later.")
        return
    
    st.markdown(f"""
    <div style="color: #6B7280; font-size: 0.875rem; margin-bottom: 20px; padding: 8px 12px; background-color: #F9FAFB; border-radius: 6px;">
        Updated: {datetime.now().strftime('%b %d, %Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)
    
    # Display news articles
    for article in news_articles:
        title = article.get('title', 'No title')
        url = article.get('url', '#')
        source = article.get('source', 'Unknown')
        published_on = article.get('published_on', 0)
        body = article.get('body', '')[:200] + '...' if article.get('body') else ''
        categories = article.get('categories', '').split('|') if article.get('categories') else []
        
        try:
            from datetime import timezone
            pub_time = datetime.fromtimestamp(published_on, tz=timezone.utc)
            time_ago = datetime.now(timezone.utc) - pub_time
            if time_ago.days > 0:
                time_str = f"{time_ago.days}d ago"
            elif time_ago.seconds >= 3600:
                time_str = f"{time_ago.seconds // 3600}h ago"
            else:
                time_str = f"{time_ago.seconds // 60}m ago"
        except:
            time_str = "Recently"
        
        st.markdown(f"""
        <a href="{url}" target="_blank" style="text-decoration: none;">
            <div class="news-card">
                <div class="news-title">{title}</div>
                <div class="news-meta">
                    <span class="news-source">{source}</span>
                    <span>•</span>
                    <span>{time_str}</span>
                </div>
                <div class="news-body">{body}</div>
                <div class="news-tags">
                    {''.join([f'<span class="news-tag">{cat}</span>' for cat in categories[:3]])}
                </div>
            </div>
        </a>
        """, unsafe_allow_html=True)
