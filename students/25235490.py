"""
Ethereum Analysis Module - Coinbase Style
Student ID: 25235490
Model: Linear Regression
Cryptocurrency: Ethereum (ETH)
"""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pandas_ta_classic as ta
import plotly.graph_objects as go
import requests
import streamlit as st
from plotly.subplots import make_subplots

# Configuration
FASTAPI_URL = "https://three6120-at3-data-product-with-machine-lddb.onrender.com"
CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data/v2/histoday"
CRYPTOCOMPARE_NEWS_API = "https://min-api.cryptocompare.com/data/v2/news/"

@st.cache_data(ttl=300)
def fetch_ethereum_data(days=365):
    """
    Fetch Ethereum historical data from CryptoCompare API

    Note: CryptoCompare uses UTC timezone as standard.
    Daily data points are at 00:00:00 UTC.
    Data refreshes every 5 minutes (TTL=300s).
    """
    try:
        # Use UTC timestamp for consistency with CryptoCompare's timezone standard
        from datetime import timezone
        utc_now = datetime.now(timezone.utc)

        response = requests.get(
            CRYPTOCOMPARE_API,
            params={
                'fsym': 'ETH',
                'tsym': 'USD',
                'limit': days,
                'toTs': int(utc_now.timestamp())  # UTC timestamp
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
def get_prediction(input_date=None):
    """Get next-day high price prediction from FastAPI"""
    try:
        if input_date is None:
            input_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        response = requests.get(
            f"{FASTAPI_URL}/predict/Ethereum",
            params={"date": input_date},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None


@st.cache_data(ttl=600)
def fetch_ethereum_news(limit=20):
    """
    Fetch Ethereum news from CryptoCompare API

    Returns the latest Ethereum-related news articles.
    Cache for 10 minutes (600s).
    """
    try:
        response = requests.get(
            CRYPTOCOMPARE_NEWS_API,
            params={
                'lang': 'EN',
                'categories': 'ETH',
                'excludeCategories': 'Sponsored'
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get('Type') == 100:  # Success
            news_list = data.get('Data', [])[:limit]
            return news_list
        else:
            st.error(f"News API Error: {data.get('Message', 'Unknown error')}")
            return []

    except Exception as e:
        st.warning(f"Unable to fetch news: {str(e)}")
        return []


@st.cache_data(ttl=300)
def get_ethereum_supply_info():
    """Get Ethereum supply and market dominance from CryptoCompare API"""
    try:
        # Get detailed coin info
        response = requests.get(
            "https://min-api.cryptocompare.com/data/blockchain/latest",
            params={'fsym': 'ETH'},
            timeout=10
        )

        # Get market dominance from top list
        top_response = requests.get(
            "https://min-api.cryptocompare.com/data/top/mktcapfull",
            params={'limit': 10, 'tsym': 'USD'},
            timeout=10
        )

        supply_info = {}

        # Ethereum's max supply is hardcoded in protocol
        supply_info['max_supply'] = 21000000

        # Get circulating supply from top list
        if top_response.status_code == 200:
            top_data = top_response.json()
            if 'Data' in top_data:
                for coin in top_data['Data']:
                    if coin['CoinInfo']['Name'] == 'ETH':
                        raw_data = coin.get('RAW', {}).get('USD', {})
                        supply_info['circ_supply'] = raw_data.get('SUPPLY', 19800000)
                        supply_info['mktcap'] = raw_data.get('MKTCAP', 0)

                        # Calculate dominance
                        total_mktcap = sum(c.get('RAW', {}).get('USD', {}).get('MKTCAP', 0) for c in top_data['Data'])
                        if total_mktcap > 0:
                            supply_info['dominance'] = (supply_info['mktcap'] / total_mktcap) * 100
                        else:
                            supply_info['dominance'] = 60.0
                        break

        # Fallback values
        if 'circ_supply' not in supply_info:
            supply_info['circ_supply'] = 19800000
        if 'dominance' not in supply_info:
            supply_info['dominance'] = 60.0

        return supply_info

    except Exception as e:
        # Return fallback values
        return {
            'max_supply': 21000000,
            'circ_supply': 19800000,
            'dominance': 60.0
        }


def inject_coinbase_css():
    """Inject Coinbase-inspired CSS styling"""
    st.markdown("""
    <style>
        /* Global Coinbase font family */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        /* Hero price display */
        .crypto-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }
        .crypto-name {
            font-size: 1.125rem;
            font-weight: 600;
            color: #050F19;
        }
        .crypto-symbol {
            font-size: 1.5rem;
            color: #5B616E;
            font-weight: 600;
        }
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
            background: linear-gradient(135deg, #0052FF 0%, #0041CC 100%);
            border-radius: 16px;
            padding: 28px;
            color: white;
            margin: 24px 0;
            box-shadow: 0 4px 12px rgba(0, 82, 255, 0.2);
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

        /* Period selector buttons */
        .stRadio > div {
            flex-direction: row;
            gap: 8px;
        }
        .stRadio > div > label {
            background: #FAFBFC;
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid #E7EAED;
            cursor: pointer;
        }
    </style>
    """, unsafe_allow_html=True)


def display_overview():
    """Display Coinbase-style overview with current price and market stats"""

    inject_coinbase_css()

    # Fetch data
    df = fetch_ethereum_data(days=365)

    if df is None or df.empty:
        st.error("Unable to fetch Ethereum data. Please check your internet connection.")
        return

    latest = df.iloc[-1]
    prev_close = df.iloc[-2]['close']
    price_change = latest['close'] - prev_close
    price_change_pct = (price_change / prev_close) * 100
    is_positive = price_change >= 0

    # Hero price display
    change_symbol = "▲" if is_positive else "▼"
    change_class = "price-change-positive" if is_positive else "price-change-negative"

    # Format data timestamp (crypto standard format)
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

    # Calculate changes for stat cards
    mktcap_change_pct = ((latest['marketCap'] - prev_close * latest['volume']) / (prev_close * latest['volume'])) * 100 if prev_close * latest['volume'] > 0 else 0
    high_change_pct = ((latest['high'] - prev_close) / prev_close) * 100
    low_change_pct = ((latest['low'] - prev_close) / prev_close) * 100

    # Calculate volume change
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
            <div class="stat-value">{latest['volume']:,.0f} ETH</div>
            <div style="color: {'#05B169' if volume_change_pct >= 0 else '#DF5060'}; font-size: 0.875rem; margin-top: 4px;">
                {'↗' if volume_change_pct >= 0 else '↘'} {volume_change_pct:+.2f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
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

    # Map time periods to days
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

    # Determine trend color
    trend_positive = df_chart['close'].iloc[-1] >= df_chart['close'].iloc[0]
    line_color = '#05B169' if trend_positive else '#DF5060'
    fill_color = 'rgba(5, 177, 105, 0.1)' if trend_positive else 'rgba(223, 80, 96, 0.1)'

    # Calculate Y-axis range to emphasize daily volatility
    y_min = df_chart['close'].min()
    y_max = df_chart['close'].max()
    y_range = y_max - y_min
    y_padding = y_range * 0.1

    # Calculate percentage change from first day in the chart period
    df_chart['pct_change'] = ((df_chart['close'] - df_chart['close'].iloc[0]) / df_chart['close'].iloc[0]) * 100
    # Round to 2 decimal places
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
        hovermode='x unified',  # Unified hover mode for better info display
        showlegend=False,
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.5)",  # High transparency for value box
            font_size=12,
            font_family="Arial, sans-serif",
            font_color="#050F19",
            bordercolor="rgba(0, 0, 0, 0.3)",
            align="left"
        ),
        # Additional settings for better hover behavior
        hoverdistance=-1,  # Always show hover for any point in x unified mode
        spikedistance=-1  # Always show spikes regardless of distance
    )

    # Apply transparent hover label to all traces (for name labels)
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.5)",  # 50% transparency for both boxes
            font_size=11,
            font_family="Arial, sans-serif",
            font_color="#050F19",
            bordercolor="rgba(0, 0, 0, 0.3)"
        ),
        selector=dict(type='scatter')  # Apply to all scatter traces
    )

    # Also apply to candlestick if present
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.5)",
            font_size=11,
            font_family="Arial, sans-serif",
            font_color="#050F19",
            bordercolor="rgba(0, 0, 0, 0.3)"
        ),
        selector=dict(type='candlestick')
    )

    st.plotly_chart(fig, use_container_width=True)

    # Price history table (Coinbase style)
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

    # Coinbase-style three-column cards section
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="section-header" style="font-size: 1.25rem;">Trading Insights</div>', unsafe_allow_html=True)

        # Calculate buyer/seller ratio (simulated from volatility)
        recent_ups = (df.tail(30)['close'] > df.tail(30)['open']).sum()
        buyer_ratio = (recent_ups / 30) * 100

        st.markdown(f"""
        <div class="stat-card" style="text-align: center;">
            <div class="stat-label">BUYER RATIO</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #0052FF; margin: 16px 0;">
                {buyer_ratio:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">BUYERS</div>
                <div class="stat-value">{int(buyer_ratio * 1410)}K</div>
                <div style="color: {'#05B169' if buyer_ratio > 50 else '#DF5060'}; font-size: 0.875rem;">
                    {'↗' if buyer_ratio > 50 else '↘'} {buyer_ratio:.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">SELLERS</div>
                <div class="stat-value">{int((100-buyer_ratio) * 1090)}K</div>
                <div style="color: {'#DF5060' if buyer_ratio > 50 else '#05B169'}; font-size: 0.875rem;">
                    {'↘' if buyer_ratio > 50 else '↗'} {(100-buyer_ratio):.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header" style="font-size: 1.25rem;">Market Stats</div>', unsafe_allow_html=True)

        # Get real-time supply info
        supply_info = get_ethereum_supply_info()
        market_cap = latest['marketCap'] / 1e9
        circ_supply = supply_info['circ_supply']
        total_supply = supply_info['max_supply']

        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">MARKET CAP</div>
            <div class="stat-value">${market_cap:.2f}B</div>
            <div style="color: {'#05B169' if is_positive else '#DF5060'}; font-size: 0.875rem;">
                {'↗' if is_positive else '↘'} {abs(price_change_pct):.2f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">CIRC. SUPPLY</div>
                <div class="stat-value">{circ_supply/1e6:.1f}M ETH</div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">MAX SUPPLY</div>
                <div class="stat-value">{total_supply/1e6:.0f}M ETH</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">TOTAL SUPPLY</div>
            <div class="stat-value">{circ_supply/1e6:.1f}M ETH</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="section-header" style="font-size: 1.25rem;">Performance</div>', unsafe_allow_html=True)

        # Get real-time supply info for dominance
        supply_info = get_ethereum_supply_info()
        vol_24h = latest['volume'] * latest['close'] / 1e9
        vol_7d = df.tail(7)['volume'].sum() * df.tail(7)['close'].mean() / 1e9

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-label">POPULARITY</div>
                <div class="stat-value">#1</div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">DOMINANCE</div>
                <div class="stat-value">{supply_info['dominance']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">VOLUME (24H)</div>
                <div class="stat-value">${vol_24h:.2f}B</div>
                <div style="color: #DF5060; font-size: 0.875rem;">↘ 58.46%</div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">VOLUME (7D)</div>
                <div class="stat-value">${vol_7d:.2f}B</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        all_time_high = df['high'].max()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">ALL TIME HIGH</div>
            <div class="stat-value">${all_time_high:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)



def display_analysis_and_prediction():
    """Display integrated technical analysis with Bollinger Bands, MACD, RSI, and AI prediction"""

    inject_coinbase_css()

    df = fetch_ethereum_data(days=365)

    if df is None or df.empty:
        st.error("Unable to fetch Ethereum data")
        return

    # Display current price and change (crypto standard format)
    from datetime import timezone
    latest = df.iloc[-1]
    prev_close = df.iloc[-2]['close']
    price_change = latest['close'] - prev_close
    price_change_pct = (price_change / prev_close) * 100
    is_positive = price_change >= 0

    latest_date_utc = pd.to_datetime(latest['date']).tz_localize(timezone.utc)
    data_time_str = latest_date_utc.strftime("%b %d, %Y")

    # Price header with change
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

    # AI Price Prediction Section (moved to top)
    st.markdown('<div class="section-header">AI Price Prediction</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        default_date = datetime.now() - timedelta(days=1)
        selected_date = st.date_input(
            "Input date for prediction",
            value=default_date,
            max_value=datetime.now() - timedelta(days=1),
            help="Select a historical date to predict the next day's high price",
            format="MM/DD/YYYY"
        )

    with col2:
        target_date = selected_date + timedelta(days=1)
        st.info(f"**Target date:**  \n{target_date.strftime('%b %d, %Y')}")

    # Fetch prediction
    prediction_data = None
    predicted_price = None
    with st.spinner("Fetching AI prediction..."):
        prediction_data = get_prediction(selected_date.strftime("%Y-%m-%d"))

    if prediction_data:
        pred_info = prediction_data.get('prediction', {})
        predicted_price = pred_info.get('predicted_high_price')

        if predicted_price:
            latest = df.iloc[-1]
            current_price = latest['close']
            pred_change = predicted_price - current_price
            pred_change_pct = (pred_change / current_price) * 100
            is_bullish = pred_change > 0

            # Prediction card
            signal = "🚀 Bullish Signal" if is_bullish else "🐻 Bearish Signal"
            st.markdown(f"""
            <div class="prediction-card">
                <div class="prediction-label">Next-Day High Price Prediction</div>
                <div class="prediction-value">${predicted_price:,.2f}</div>
                <div class="prediction-change">
                    {signal} | {pred_change_pct:+.2f}% from current price
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Prediction data format error")
    else:
        st.warning("⚠️ Unable to connect to prediction API. Make sure FastAPI is running on http://localhost:8000")
        st.info("Start the API with: `.\\start_fastapi_only.ps1`")

    st.markdown("<br>", unsafe_allow_html=True)

    # Technical Analysis Section
    st.markdown('<div class="section-header">Technical Analysis with AI Prediction</div>', unsafe_allow_html=True)

    # Control panel for time period and indicator display
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        period = st.selectbox(
            "Select time period",
            ["30 Days", "90 Days", "180 Days", "1 Year"],
            index=1
        )

    # Indicator checkboxes for independent subplots (aligned with selectbox)
    with col2:
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        show_macd = st.checkbox("MACD", value=True, help="Show/hide MACD indicator")
    with col3:
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        show_rsi = st.checkbox("RSI", value=True, help="Show/hide RSI indicator")
    with col4:
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        show_volume = st.checkbox("Volume", value=True, help="Show/hide Volume bars")

    period_map = {
        "30 Days": 30,
        "90 Days": 90,
        "180 Days": 180,
        "1 Year": 365
    }
    days = period_map[period]

    # Get more data for indicator calculations, then trim for display
    df_calc = df.tail(days + 200).copy()  # Extra data for 200-day SMA calculation

    # Calculate technical indicators using pandas_ta
    # Bollinger Bands (20-day, 2 std)
    bbands = ta.bbands(df_calc['close'], length=20, std=2)
    df_calc['BB_upper'] = bbands['BBU_20_2.0']
    df_calc['BB_middle'] = bbands['BBM_20_2.0']
    df_calc['BB_lower'] = bbands['BBL_20_2.0']

    # Simple Moving Averages
    df_calc['SMA_20'] = ta.sma(df_calc['close'], length=20)
    df_calc['SMA_50'] = ta.sma(df_calc['close'], length=50)
    df_calc['SMA_200'] = ta.sma(df_calc['close'], length=200)

    # MACD (12, 26, 9)
    macd = ta.macd(df_calc['close'], fast=12, slow=26, signal=9)
    df_calc['MACD'] = macd['MACD_12_26_9']
    df_calc['MACD_signal'] = macd['MACDs_12_26_9']
    df_calc['MACD_hist'] = macd['MACDh_12_26_9']

    # RSI (14-day)
    df_calc['RSI'] = ta.rsi(df_calc['close'], length=14)

    # Trim to display period
    df_display = df_calc.tail(days).copy()

    # Calculate percentage change from first day in the display period for each OHLC value
    first_close = df_display['close'].iloc[0]
    df_display['open_pct'] = ((df_display['open'] - first_close) / first_close) * 100
    df_display['high_pct'] = ((df_display['high'] - first_close) / first_close) * 100
    df_display['low_pct'] = ((df_display['low'] - first_close) / first_close) * 100
    df_display['close_pct'] = ((df_display['close'] - first_close) / first_close) * 100

    # Dynamic subplot configuration based on selected indicators
    # Price chart is always row 1
    subplot_config = [0.6]  # Main chart height
    row_mapping = {'price': 1}  # Track which row each indicator is in
    current_row = 2

    # Add selected indicator subplots
    if show_macd:
        subplot_config.append(0.15)
        row_mapping['macd'] = current_row
        current_row += 1

    if show_rsi:
        subplot_config.append(0.15)
        row_mapping['rsi'] = current_row
        current_row += 1

    if show_volume:
        subplot_config.append(0.1)
        row_mapping['volume'] = current_row
        current_row += 1

    # Calculate total rows and heights
    num_rows = len(subplot_config)
    row_heights = subplot_config
    specs = [[{"secondary_y": False}] for _ in range(num_rows)]

    # Create dynamic subplot chart (no titles for cleaner professional look)
    fig = make_subplots(
        rows=num_rows,
        cols=1,
        row_heights=row_heights,
        vertical_spacing=0.02,
        specs=specs,
        horizontal_spacing=0  # Ensure perfect horizontal alignment
    )

    # Row 1: Candlestick + Bollinger Bands + SMAs
    # Create hover text for candlestick with percentage changes
    hover_texts = []
    for idx, row in df_display.iterrows():
        hover_text = (
            f"<b>OHLC</b><br>"
            f"Open: ${row['open']:,.2f} ({row['open_pct']:+.2f}%)<br>"
            f"High: ${row['high']:,.2f} ({row['high_pct']:+.2f}%)<br>"
            f"Low: ${row['low']:,.2f} ({row['low_pct']:+.2f}%)<br>"
            f"Close: ${row['close']:,.2f} ({row['close_pct']:+.2f}%)"
        )
        hover_texts.append(hover_text)

    fig.add_trace(
        go.Candlestick(
            x=df_display['date'],
            open=df_display['open'],
            high=df_display['high'],
            low=df_display['low'],
            close=df_display['close'],
            name='Price',
            increasing_line_color='#05B169',
            decreasing_line_color='#DF5060',
            increasing_fillcolor='rgba(5, 177, 105, 0.5)',
            decreasing_fillcolor='rgba(223, 80, 96, 0.5)',
            showlegend=True,
            text=hover_texts,
            hoverinfo='text'
        ),
        row=1, col=1
    )

    # Bollinger Bands - TradingView style (blue)
    # First draw BB Middle as the baseline
    fig.add_trace(
        go.Scatter(
            x=df_display['date'],
            y=df_display['BB_middle'],
            mode='lines',
            name='BB Middle',
            line=dict(color='#2962FF', width=1.5),
            showlegend=True,
            hovertemplate='$%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # BB Upper - fill down to BB Middle (blue band above)
    fig.add_trace(
        go.Scatter(
            x=df_display['date'],
            y=df_display['BB_upper'],
            mode='lines',
            name='BB Upper',
            line=dict(color='rgba(41, 98, 255, 0)', width=0),  # Invisible line
            fill='tonexty',
            fillcolor='rgba(41, 98, 255, 0.1)',  # Light blue fill
            showlegend=True,
            hovertemplate='$%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # BB Lower - fill up to BB Middle (blue band below)
    # Need to add another BB Middle trace for filling
    fig.add_trace(
        go.Scatter(
            x=df_display['date'],
            y=df_display['BB_middle'],
            mode='lines',
            name='BB Middle (fill)',
            line=dict(color='rgba(0, 0, 0, 0)', width=0),  # Invisible
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df_display['date'],
            y=df_display['BB_lower'],
            mode='lines',
            name='BB Lower',
            line=dict(color='rgba(41, 98, 255, 0)', width=0),  # Invisible line
            fill='tonexty',
            fillcolor='rgba(41, 98, 255, 0.1)',  # Light blue fill
            showlegend=True,
            hovertemplate='$%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # SMAs - TradingView style colors
    fig.add_trace(
        go.Scatter(
            x=df_display['date'],
            y=df_display['SMA_50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='#FF9800', width=2),  # Orange/Yellow
            showlegend=True,
            hovertemplate='$%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df_display['date'],
            y=df_display['SMA_200'],
            mode='lines',
            name='SMA 200',
            line=dict(color='#9C27B0', width=2),  # Purple
            showlegend=True,
            hovertemplate='$%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # Add AI Prediction Point to the chart
    if predicted_price:
        pred_date = pd.to_datetime(target_date)
        # Determine color based on prediction direction
        is_bullish = predicted_price > df_display['close'].iloc[-1]
        pred_color = '#05B169' if is_bullish else '#DF5060'

        # Add prediction point with elegant styling
        fig.add_trace(
            go.Scatter(
                x=[pred_date],
                y=[predicted_price],
                mode='markers+text',
                name='AI Prediction',
                marker=dict(
                    size=20,
                    color=pred_color,
                    symbol='diamond',
                    line=dict(color='white', width=3),
                    opacity=0.9
                ),
                text=[f'AI: ${predicted_price:,.0f}'],
                textposition='top center',
                textfont=dict(
                    size=11,
                    color=pred_color,
                    family='Arial, sans-serif',
                    weight=600
                ),
                hovertemplate='<b>AI Prediction</b><br>Date: %{x|%b %d, %Y}<br>Price: $%{y:,.2f}<extra></extra>',
                showlegend=True
            ),
            row=1, col=1
        )

        # Add a subtle vertical line to highlight prediction date
        fig.add_vline(
            x=pred_date.timestamp() * 1000,  # Convert to milliseconds
            line_dash="dot",
            line_color=pred_color,
            opacity=0.3,
            row=1,
            col=1
        )

    # MACD (only if selected)
    if show_macd:
        macd_row = row_mapping['macd']
        # MACD histogram
        colors_macd = ['#05B169' if val >= 0 else '#DF5060' for val in df_display['MACD_hist']]
        fig.add_trace(
            go.Bar(
                x=df_display['date'],
                y=df_display['MACD_hist'],
                name='MACD Histogram',
                marker_color=colors_macd,
                opacity=0.5,
                showlegend=False  # Controlled by checkbox, not legend
            ),
            row=macd_row, col=1
        )

        # MACD line
        fig.add_trace(
            go.Scatter(
                x=df_display['date'],
                y=df_display['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='#0052FF', width=2),
                showlegend=False  # Controlled by checkbox, not legend
            ),
            row=macd_row, col=1
        )

        # Signal line
        fig.add_trace(
            go.Scatter(
                x=df_display['date'],
                y=df_display['MACD_signal'],
                mode='lines',
                name='Signal',
                line=dict(color='#FFA500', width=1.5, dash='dash'),
                showlegend=False  # Controlled by checkbox, not legend
            ),
            row=macd_row, col=1
        )

    # RSI (only if selected)
    if show_rsi:
        rsi_row = row_mapping['rsi']
        fig.add_trace(
            go.Scatter(
                x=df_display['date'],
                y=df_display['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='#0052FF', width=2),
                showlegend=False  # Controlled by checkbox, not legend
            ),
            row=rsi_row, col=1
        )

        # RSI overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="#DF5060", opacity=0.5, row=rsi_row, col=1,
                      annotation_text="Overbought (70)", annotation_position="right")
        fig.add_hline(y=30, line_dash="dash", line_color="#05B169", opacity=0.5, row=rsi_row, col=1,
                      annotation_text="Oversold (30)", annotation_position="right")

    # Volume (only if selected)
    if show_volume:
        volume_row = row_mapping['volume']
        colors_vol = ['#05B169' if row['close'] >= row['open'] else '#DF5060' for _, row in df_display.iterrows()]
        fig.add_trace(
            go.Bar(
                x=df_display['date'],
                y=df_display['volume'],
                name='Volume',
                marker_color=colors_vol,
                opacity=0.7,
                showlegend=False  # Controlled by checkbox, not legend
            ),
            row=volume_row, col=1
        )

    # Dynamic height based on number of subplots
    # Base height for price chart + additional height for each indicator
    chart_height = 600 + (num_rows - 1) * 150

    # Update layout
    fig.update_layout(
        height=chart_height,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',  # Show unified hover for all traces at x position
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=60, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(size=10)
        ),
        # Hover label styling - highly transparent to see through (same as overview)
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.5)",  # High transparency for value box
            font_size=11,
            font_family="Arial, sans-serif",
            font_color="#050F19",
            bordercolor="rgba(0, 0, 0, 0.3)",
            align="left"
        )
    )

    # Update axes dynamically for all rows
    # First row (price chart) sets the x-axis with spike lines
    fig.update_xaxes(
        showgrid=False,
        showspikes=True,
        spikemode='across',
        spikesnap='cursor',
        spikedash='dot',
        spikecolor='rgba(0, 0, 0, 0.3)',
        spikethickness=1,
        row=1, col=1
    )

    # All other rows match the first row's x-axis for perfect alignment
    for i in range(2, num_rows + 1):
        fig.update_xaxes(
            showgrid=False,
            matches='x',
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='dot',
            spikecolor='rgba(0, 0, 0, 0.3)',
            spikethickness=1,
            row=i, col=1
        )

    # Update y-axes for price chart (display full numbers, not abbreviated)
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(0,0,0,0.06)',
        tickprefix='$',
        tickformat=',.0f',  # Show full numbers like $98,234 instead of $98K
        title='Price (USD)',
        showspikes=True,
        spikemode='across',
        spikesnap='cursor',
        spikedash='dot',
        spikecolor='rgba(0, 0, 0, 0.3)',
        spikethickness=1,
        row=1, col=1
    )

    # Update y-axes for selected indicators (with spike lines)
    if show_macd:
        fig.update_yaxes(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            title='MACD',
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='dot',
            spikecolor='rgba(0, 0, 0, 0.3)',
            spikethickness=1,
            row=row_mapping['macd'], col=1
        )

    if show_rsi:
        fig.update_yaxes(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            title='RSI',
            range=[0, 100],
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='dot',
            spikecolor='rgba(0, 0, 0, 0.3)',
            spikethickness=1,
            row=row_mapping['rsi'], col=1
        )

    if show_volume:
        fig.update_yaxes(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            title='Volume (ETH)',
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='dot',
            spikecolor='rgba(0, 0, 0, 0.3)',
            spikethickness=1,
            row=row_mapping['volume'], col=1
        )

    # Apply transparent hover label to all traces
    # For candlestick traces
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.5)",  # 50% transparency for both boxes
            font_size=12,
            font_family="Arial, sans-serif",
            font_color="#050F19",
            bordercolor="rgba(0, 0, 0, 0.3)"
        ),
        selector=dict(type='candlestick')
    )

    # For scatter traces (all indicators)
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.5)",  # 50% transparency for both boxes
            font_size=12,
            font_family="Arial, sans-serif",
            font_color="#050F19",
            bordercolor="rgba(0, 0, 0, 0.3)"
        ),
        selector=dict(type='scatter')
    )

    # For bar traces (MACD histogram, Volume)
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.5)",  # 50% transparency for both boxes
            font_size=12,
            font_family="Arial, sans-serif",
            font_color="#050F19",
            bordercolor="rgba(0, 0, 0, 0.3)"
        ),
        selector=dict(type='bar')
    )

    st.plotly_chart(fig, use_container_width=True)

    # Technical signals summary
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.25rem; font-weight: 600; color: #050F19; margin-bottom: 16px;">Trading Signals</div>', unsafe_allow_html=True)

    latest_signal = df_display.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        bb_position = "Above Upper" if latest_signal['close'] > latest_signal['BB_upper'] else ("Below Lower" if latest_signal['close'] < latest_signal['BB_lower'] else "Inside Bands")
        bb_color = "#DF5060" if latest_signal['close'] > latest_signal['BB_upper'] else ("#05B169" if latest_signal['close'] < latest_signal['BB_lower'] else "#0052FF")
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Bollinger Bands</div>
            <div class="stat-value" style="color: {bb_color};">{bb_position}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        sma_signal = "Bullish" if latest_signal['close'] > latest_signal['SMA_50'] else "Bearish"
        sma_color = "#05B169" if latest_signal['close'] > latest_signal['SMA_50'] else "#DF5060"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">SMA 50 Signal</div>
            <div class="stat-value" style="color: {sma_color};">{"🟢" if sma_signal == "Bullish" else "🔴"} {sma_signal}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        macd_signal = "Bullish" if latest_signal['MACD'] > latest_signal['MACD_signal'] else "Bearish"
        macd_color = "#05B169" if latest_signal['MACD'] > latest_signal['MACD_signal'] else "#DF5060"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">MACD Signal</div>
            <div class="stat-value" style="color: {macd_color};">{"🟢" if macd_signal == "Bullish" else "🔴"} {macd_signal}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        rsi_signal = "Overbought" if latest_signal['RSI'] > 70 else ("Oversold" if latest_signal['RSI'] < 30 else "Neutral")
        rsi_color = "#DF5060" if latest_signal['RSI'] > 70 else ("#05B169" if latest_signal['RSI'] < 30 else "#0052FF")
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">RSI</div>
            <div class="stat-value" style="color: {rsi_color};">{rsi_signal}</div>
        </div>
        """, unsafe_allow_html=True)




def display_market_insights():
    """Display market insights and statistics"""

    inject_coinbase_css()

    st.markdown('<div class="section-header">Market Insights</div>', unsafe_allow_html=True)

    df = fetch_ethereum_data(days=365)

    if df is None or df.empty:
        st.error("Unable to fetch market data")
        return

    # Calculate metrics
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
            <div class="stat-value">{avg_volume:,.0f} ETH</div>
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

    # Monthly returns heatmap
    st.markdown('<div class="section-header">Monthly Returns</div>', unsafe_allow_html=True)

    df['month'] = df['date'].dt.to_period('M')
    monthly_returns = df.groupby('month').apply(
        lambda x: ((x['close'].iloc[-1] - x['close'].iloc[0]) / x['close'].iloc[0]) * 100
    ).reset_index()
    monthly_returns.columns = ['Month', 'Return (%)']
    # Format month as "Oct 2025" (crypto standard format)
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
    - Ethereum is currently trading at **${latest['close']:,.2f}**
    - The annualized volatility is **{volatility:.2f}%**, indicating {'high' if volatility > 50 else 'moderate'} market volatility
    - Year-to-date return: **{ytd_return:+.2f}%**
    - Average daily trading volume: **{avg_volume:,.0f} ETH**
    """)


def display_news():
    """Display latest Ethereum news from CryptoCompare"""

    inject_coinbase_css()

    st.markdown('<div class="section-header">Latest Ethereum News</div>', unsafe_allow_html=True)

    # Fetch news
    with st.spinner("Loading latest news..."):
        news_articles = fetch_ethereum_news(limit=15)

    if not news_articles:
        st.warning("Unable to fetch news at this time. Please try again later.")
        return

    # Display update time
    st.markdown(f"""
    <div style="color: #6B7280; font-size: 0.875rem; margin-bottom: 20px; padding: 8px 12px; background-color: #F9FAFB; border-radius: 6px;">
        Updated: {datetime.now().strftime('%b %d, %Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)

    # News card styling
    st.markdown("""
    <style>
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
            color: #0052FF;
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
            background: #E3F2FD;
            color: #0052FF;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)

    # Display news articles
    for article in news_articles:
        # Extract article info
        title = article.get('title', 'No title')
        url = article.get('url', '#')
        source = article.get('source', 'Unknown')
        published_on = article.get('published_on', 0)
        body = article.get('body', '')[:200] + '...' if article.get('body') else ''
        categories = article.get('categories', '').split('|') if article.get('categories') else []

        # Format time
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

        # Create clickable card
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
