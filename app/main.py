"""
Cryptocurrency Investment Data Product - AT3 Assignment
Streamlit App for cryptocurrency analysis and price prediction

Group 4 - 36120 Advanced Machine Learning - UTS
"""

import streamlit as st
import sys
from pathlib import Path
import requests

# Add students directory to path
students_path = Path(__file__).parent.parent / "students"
sys.path.insert(0, str(students_path))

# Student ID mapping to cryptocurrencies
STUDENT_MAPPING = {
    "bitcoin": "25605217",
    "ethereum": None,
    "xrp": None,
    "solana": None
}

# Configure page
st.set_page_config(
    page_title="Crypto Investment Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'selected_crypto' not in st.session_state:
    st.session_state.selected_crypto = None


@st.cache_data(ttl=60)
def fetch_crypto_prices():
    """Fetch real-time cryptocurrency prices from CryptoCompare API"""
    try:
        # Fetch multiple crypto prices at once
        response = requests.get(
            "https://min-api.cryptocompare.com/data/pricemultifull",
            params={
                "fsyms": "BTC,ETH,XRP,SOL",
                "tsyms": "USD"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get('Response') == 'Error':
            return None

        return data.get('RAW', {})
    except Exception as e:
        st.error(f"Error fetching prices: {str(e)}")
        return None


# ==================== HOME PAGE (Coinbase-style List) ====================
if st.session_state.selected_crypto is None:
    st.markdown("## Cryptocurrency Prices")

    # Fetch real-time prices
    price_data = fetch_crypto_prices()

    # Crypto configuration
    crypto_configs = [
        {
            "name": "Bitcoin",
            "symbol": "BTC",
            "icon": "https://www.cryptocompare.com/media/37746251/btc.png",
            "key": "bitcoin",
            "student_id": "25605217"
        },
        {
            "name": "Ethereum",
            "symbol": "ETH",
            "icon": "https://www.cryptocompare.com/media/37746238/eth.png",
            "key": "ethereum",
            "student_id": None
        },
        {
            "name": "XRP",
            "symbol": "XRP",
            "icon": "https://www.cryptocompare.com/media/38553096/xrp.png",
            "key": "xrp",
            "student_id": None
        },
        {
            "name": "Solana",
            "symbol": "SOL",
            "icon": "https://www.cryptocompare.com/media/37747734/sol.png",
            "key": "solana",
            "student_id": None
        }
    ]

    # Build crypto data with real-time prices
    crypto_data = []
    for config in crypto_configs:
        symbol = config['symbol']

        if price_data and symbol in price_data and 'USD' in price_data[symbol]:
            usd_data = price_data[symbol]['USD']

            price = usd_data.get('PRICE', 0)
            change_pct = usd_data.get('CHANGEPCT24HOUR', 0)
            mktcap = usd_data.get('MKTCAP', 0)
            volume = usd_data.get('VOLUME24HOURTO', 0)

            # Format values
            if price >= 1000:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:.2f}"

            change_str = f"{change_pct:+.2f}%"

            # Format market cap
            if mktcap >= 1e12:
                mktcap_str = f"${mktcap/1e12:.2f}T"
            elif mktcap >= 1e9:
                mktcap_str = f"${mktcap/1e9:.2f}B"
            else:
                mktcap_str = f"${mktcap/1e6:.2f}M"

            # Format volume
            if volume >= 1e9:
                volume_str = f"${volume/1e9:.2f}B"
            else:
                volume_str = f"${volume/1e6:.2f}M"

            crypto_data.append({
                **config,
                "price": price_str,
                "change": change_str,
                "mkt_cap": mktcap_str,
                "volume": volume_str,
                "change_positive": change_pct >= 0
            })
        else:
            # Fallback if API fails
            crypto_data.append({
                **config,
                "price": "N/A",
                "change": "N/A",
                "mkt_cap": "N/A",
                "volume": "N/A",
                "change_positive": True
            })

    # Coinbase-style table CSS
    st.markdown("""
    <style>
        .crypto-row {
            display: flex;
            align-items: center;
            padding: 24px;
            border-bottom: 1px solid #E7EAED;
            transition: background-color 0.2s;
        }
        .crypto-row:hover {
            background-color: #F7F8FA;
        }
        .crypto-icon {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            margin-right: 20px;
        }
        .crypto-name {
            font-weight: 600;
            font-size: 1.375rem;
        }
        .crypto-symbol {
            color: #5B616E;
            font-size: 1rem;
        }
        .change-positive {
            color: #05B169;
        }
        .change-negative {
            color: #DF5060;
        }
        .table-header {
            display: flex;
            padding: 16px 24px;
            background-color: #F7F8FA;
            font-size: 0.875rem;
            color: #5B616E;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-radius: 8px 8px 0 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # Table header
    st.markdown("""
    <div class="table-header">
        <div style="flex: 1.5; padding-left: 16px;">Asset</div>
        <div style="flex: 1;">Price</div>
        <div style="flex: 1;">Change</div>
        <div style="flex: 1;">Mkt Cap</div>
        <div style="flex: 1;">Volume</div>
        <div style="flex: 0.5;"></div>
    </div>
    """, unsafe_allow_html=True)

    # Display crypto rows with elegant view button
    for crypto in crypto_data:
        change_class = "change-positive" if crypto["change_positive"] else "change-negative"

        if crypto['student_id']:
            # Use columns for layout with small button on right
            cols = st.columns([0.15, 1.35, 1, 1, 1, 1, 0.4])

            with cols[0]:
                st.write("")  # Empty space for alignment

            with cols[1]:
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 8px 0;">
                    <img src="{crypto['icon']}" style="width: 56px; height: 56px; border-radius: 50%; margin-right: 20px;" alt="{crypto['name']}">
                    <div>
                        <div style="font-weight: 600; font-size: 1.375rem; color: #050F19; margin-bottom: 2px;">{crypto['name']}</div>
                        <div style="color: #5B616E; font-size: 1rem;">{crypto['symbol']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with cols[2]:
                st.markdown(f'<div style="font-weight: 600; font-size: 1.125rem; color: #050F19; padding-top: 18px;">{crypto["price"]}</div>', unsafe_allow_html=True)

            with cols[3]:
                st.markdown(f'<div style="font-weight: 600; font-size: 1rem; padding-top: 18px;" class="{change_class}">{crypto["change"]}</div>', unsafe_allow_html=True)

            with cols[4]:
                st.markdown(f'<div style="color: #5B616E; font-size: 1rem; padding-top: 18px;">{crypto["mkt_cap"]}</div>', unsafe_allow_html=True)

            with cols[5]:
                st.markdown(f'<div style="color: #5B616E; font-size: 1rem; padding-top: 18px;">{crypto["volume"]}</div>', unsafe_allow_html=True)

            with cols[6]:
                st.write("")
                # Small elegant button
                if st.button("→", key=f"crypto_{crypto['key']}", help=f"View {crypto['name']}"):
                    st.session_state.selected_crypto = crypto['key']
                    st.rerun()

            st.markdown('<div style="border-bottom: 1px solid #E7EAED; margin: 8px 0 16px 0;"></div>', unsafe_allow_html=True)
        else:
            # Non-clickable row
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 24px; border-bottom: 1px solid #E7EAED; opacity: 0.5;">
                <div style="flex: 0.15;"></div>
                <div style="flex: 1.35; display: flex; align-items: center;">
                    <img src="{crypto['icon']}" style="width: 56px; height: 56px; border-radius: 50%; margin-right: 20px;" alt="{crypto['name']}">
                    <div>
                        <div style="font-weight: 600; font-size: 1.375rem; color: #050F19; margin-bottom: 2px;">{crypto['name']}</div>
                        <div style="color: #5B616E; font-size: 1rem;">{crypto['symbol']}</div>
                    </div>
                </div>
                <div style="flex: 1; font-weight: 600; font-size: 1.125rem; color: #050F19;">{crypto['price']}</div>
                <div style="flex: 1; font-weight: 600; font-size: 1rem;" class="{change_class}">{crypto['change']}</div>
                <div style="flex: 1; color: #5B616E; font-size: 1rem;">{crypto['mkt_cap']}</div>
                <div style="flex: 1; color: #5B616E; font-size: 1rem;">{crypto['volume']}</div>
                <div style="flex: 0.4; text-align: center; color: #999; font-size: 0.875rem; font-style: italic;">Coming Soon</div>
            </div>
            """, unsafe_allow_html=True)

    st.stop()

# ==================== DETAIL PAGE (Selected Crypto) ====================
crypto_symbol = st.session_state.selected_crypto

# Back button at top of page (Coinbase style) - inline
if st.button("← Cryptocurrency List", key="back_button"):
    st.session_state.selected_crypto = None
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Crypto details mapping
crypto_details = {
    "bitcoin": {"name": "Bitcoin", "symbol": "BTC", "icon": "https://www.cryptocompare.com/media/37746251/btc.png"},
    "ethereum": {"name": "Ethereum", "symbol": "ETH", "icon": "https://www.cryptocompare.com/media/37746238/eth.png"},
    "xrp": {"name": "XRP", "symbol": "XRP", "icon": "https://www.cryptocompare.com/media/38553096/xrp.png"},
    "solana": {"name": "Solana", "symbol": "SOL", "icon": "https://www.cryptocompare.com/media/37747734/sol.png"}
}

selected_info = crypto_details.get(crypto_symbol, {"name": "Bitcoin", "symbol": "BTC", "icon": "https://www.cryptocompare.com/media/37746251/btc.png"})

# Display crypto header (Bitcoin icon + name)
st.markdown(f"""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
    <img src="{selected_info['icon']}" style="width: 48px; height: 48px; border-radius: 50%; background: #F7931A; padding: 4px;" alt="{selected_info['name']}">
    <div style="display: flex; flex-direction: column; gap: 2px;">
        <span style="font-size: 1.125rem; font-weight: 600; color: #050F19;">{selected_info['name']} Price</span>
        <span style="font-size: 1.5rem; color: #5B616E; font-weight: 600;">{selected_info['symbol']}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Create tabs
tabs = st.tabs([
    "Overview",
    "Analysis & Prediction",
    "Market Insights"
])

# Tab 1: Overview
with tabs[0]:
    student_id = STUDENT_MAPPING.get(crypto_symbol)

    if student_id:
        try:
            student_module = __import__(student_id)
            student_module.display_overview()
        except ImportError:
            st.warning(f"Module not yet implemented. Please add {student_id}.py to the students/ folder.")
            st.info("This tab will display current price and market data")
    else:
        st.warning(f"No student assigned to {selected_info['name']} yet. Please update STUDENT_MAPPING in main.py.")
        st.info("This tab will display current price and market data")

# Tab 2: Analysis & Prediction
with tabs[1]:
    student_id = STUDENT_MAPPING.get(crypto_symbol)

    if student_id:
        try:
            student_module = __import__(student_id)
            student_module.display_analysis_and_prediction()
        except (ImportError, AttributeError):
            st.info("Historical data, technical analysis, and AI predictions will be displayed here.")
    else:
        st.info("Historical data, technical analysis, and AI predictions will be displayed here.")

# Tab 3: Market Insights
with tabs[2]:
    student_id = STUDENT_MAPPING.get(crypto_symbol)

    if student_id:
        try:
            student_module = __import__(student_id)
            student_module.display_market_insights()
        except (ImportError, AttributeError):
            st.info("Market insights and analysis will be displayed here.")
    else:
        st.info("Market insights and analysis will be displayed here.")
