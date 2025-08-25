# 📦 Imports
import streamlit as st
import pandas as pd
import yfinance as yf
import random
import time
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
from kite_auth import get_kite_session
from streamlit_autorefresh import st_autorefresh
from signal_logic import get_signal_data

# 🎨 Page Setup
st.set_page_config(page_title="Trade360 Dashboard", layout="wide")
st.title("🚀 Trade360 Market Scanner")

# 🖼️ Iron Man Splash Screen
st.markdown("""
    <style>
    .fade-in {
        animation: fadeIn 2s ease-in forwards;
        opacity: 0;
    }
    @keyframes fadeIn {
        to { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])
with col1:
    st.image("ironman.jpeg", width=350)
with col2:
    st.write("Welcome to your AI-powered intraday dashboard!")

if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    st.markdown('<img src="ironman.jpeg" class="fade-in" width="350">', unsafe_allow_html=True)
    st.markdown("## 🚀 Intraday AI Signal Engine")
    st.markdown("Crafted by Hemanth | Powered by Copilot")
    st.markdown("Loading your trading cockpit...")
    time.sleep(3)
    st.session_state.splash_shown = True
    st.rerun()

# 🎯 Sidebar Branding
st.sidebar.image("https://zerodha.com/static/images/logo.svg", width=150)
max_price = st.sidebar.slider("Max Stock Price ₹", min_value=100, max_value=2000, value=500)
st.sidebar.markdown("## 🚀 Zerodha Signal Engine")
st.sidebar.markdown("Welcome, Hemanth 👋")

# ⚙️ Live Mode Toggle
st.sidebar.header("⚙️ Settings")
live_mode = st.sidebar.toggle("Live Trading Mode", value=False)
mode_status = "🟢 LIVE MODE" if live_mode else "🧪 SIMULATION MODE"
st.sidebar.markdown(f"### {mode_status}")

# 🔁 Auto-refresh
st_autorefresh(interval=300000, limit=100, key="refresh")

# 📊 Scope Toggle
scope_mode = st.sidebar.radio("📊 Select Market Scope:", ["Top 3 Sectors", "NIFTY 50", "All Sectors"])
st.write(f"🔍 Currently analyzing: **{scope_mode}**")

# 🗂️ Sector Lookup
sector_lookup = {
    "NIFTY 50": ["RELIANCE", "INFY", "HDFCBANK", "TCS", "ICICIBANK", "SBIN", "ITC", "HINDUNILVR"],
    "NIFTY BANK": ["ICICIBANK", "KOTAKBANK", "SBIN", "AXISBANK", "HDFCBANK"],
    "NIFTY IT": ["TCS", "INFY", "HCLTECH", "TECHM", "WIPRO"],
    "NIFTY FMCG": ["ITC", "HINDUNILVR", "DABUR", "BRITANNIA", "MARICO"],
    "NIFTY PHARMA": ["SUNPHARMA", "CIPLA", "DIVISLAB", "DRREDDY", "AUROPHARMA"],
    "NIFTY AUTO": ["TATAMOTORS", "HEROMOTOCO", "BAJAJ-AUTO", "EICHERMOT", "MARUTI"]
}

sector_symbols = {
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY AUTO": "^CNXAUTO"
}

# 📊 Sector Performance
def get_sector_performance():
    performance = {}
    for sector, symbol in sector_symbols.items():
        data = yf.download(symbol, period="2d", interval="1d", progress=False)
        if len(data) >= 2:
            today_close = float(data["Close"].iloc[-1])
            yesterday_close = float(data["Close"].iloc[-2])
            change = ((today_close - yesterday_close) / yesterday_close) * 100
            performance[sector] = round(change, 2)
    return performance

st.subheader("📊 Sector Performance Today")
sector_perf = get_sector_performance()
sorted_perf = dict(sorted(sector_perf.items(), key=lambda x: x[1], reverse=True))
#top_sectors = list(sorted_perf.keys())[:3]

st.subheader("📊 Sector Performance Today")
sector_perf = get_sector_performance()
sorted_perf = dict(sorted(sector_perf.items(), key=lambda x: x[1], reverse=True))
top_sectors = list(sorted_perf.keys())[:3]   # <-- FIXED

if scope_mode == "Top 3 Sectors":
    st.write("📌 Scanning stocks from top sectors:")
    for sector in top_sectors:
        st.markdown(f"- **{sector}**")
elif scope_mode == "NIFTY 50":
    st.write("📌 Scanning stocks from: NIFTY 50")
else:
    st.write("📌 Scanning stocks from all defined sectors")

# 🧠 Build Stock Universe
if scope_mode == "NIFTY 50":
    selected_stocks = sector_lookup["NIFTY 50"]
elif scope_mode == "All Sectors":
    selected_stocks = []
    for sector in sector_lookup:
        if sector != "NIFTY 50":
            selected_stocks.extend(sector_lookup[sector])
elif scope_mode == "Top 3 Sectors":
    selected_stocks = []
    for sector in top_sectors:
        if sector in sector_lookup:
            selected_stocks.extend(sector_lookup[sector])

st.write("🧮 Stocks being scanned:")
st.markdown(", ".join(selected_stocks))

# 💰 Live Price Fetcher (Kite API)
def get_latest_price(kite, stock):
    try:
        instrument = f"NSE:{stock}"
        quote = kite.quote(instrument)
        return quote[instrument]["last_price"]
    except Exception as e:
        st.warning(f"⚠️ Price fetch failed for {stock}: {e}")
        return None
    
# 📜 Historical Data Fetcher (Kite API)
def get_historical_data(kite, stock, interval="5minute", days=5):
    try:
        from datetime import datetime, timedelta
        instrument = f"NSE:{stock}"
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        data = kite.historical_data(instrument_token=kite.ltp([instrument])[instrument]['instrument_token'],
                                    from_date=from_date,
                                    to_date=to_date,
                                    interval=interval)
        return pd.DataFrame(data)
    except Exception as e:
        st.warning(f"⚠️ Historical fetch failed for {stock}: {e}")
        return pd.DataFrame()


# 📈 Signal Logic with SMA/EMA
def run_signal_logic(kite, stock):
    df = get_historical_data(kite, stock)
    if df.empty:
        return None, None  # no data

    df["SMA_20"] = df["close"].rolling(20).mean()
    df["EMA_50"] = df["close"].ewm(span=50, adjust=False).mean()

    latest_price = df["close"].iloc[-1]
    sma_20 = df["SMA_20"].iloc[-1]
    ema_50 = df["EMA_50"].iloc[-1]

    if latest_price > sma_20 and sma_20 > ema_50:
        return "BUY", latest_price
    elif latest_price < sma_20 and sma_20 < ema_50:
        return "SELL", latest_price
    else:
        return "HOLD", latest_price



# 📈 Signal Analysis
st.subheader("📈 Signal Analysis")
signals = {}

# Filter stocks based on max price and actionable signals
data = get_signal_data()

affordable_data = data[(data['Close'] < max_price) & (data['Signal'].isin(['BUY', 'SELL']))]

for index, row in affordable_data.iterrows():
    # Skip rows without a valid symbol
    if 'Symbol' not in row or pd.isna(row['Symbol']):
        st.warning(f"⚠️ Skipping row at {index}: No symbol found")
        continue

    symbol = row['Symbol']
    signal = row['Signal']
    price = row['Close']

    st.info(f"{symbol} @ ₹{round(price, 2)} → Signal: {signal}")

    if live_mode and signal in ["BUY", "SELL"]:
        try:
            order = execute_trade(kite, symbol, signal)
            st.success(f"✅ Order placed: {order['order_id']}")
        except Exception as e:
            st.error(f"❌ Trade failed: {e}")


    signals[symbol] = signal

    if signal == "BUY":
        st.success(f"{stock}: Buy Signal (₹{round(price,2)})")
    elif signal == "SELL":
        st.error(f"{stock}: Sell Signal (₹{round(price,2)})")
    else:
        st.info(f"{stock}: Hold (₹{round(price,2)})")


# 📊 Signal Summary Chart
st.subheader("📊 Signal Summary")
st.bar_chart(pd.Series(signals).value_counts())

# 🗂️ Tabs
tab1, tab2, tab3 = st.tabs(["📈 Signals", "📋 Trades", "📊 Strategy Audit"])

# 📈 Tab 1: Signals
with tab1:
    data = get_signal_data()
    st.subheader("🕒 Filter by Time Range")
    start_time = st.slider("Start Time", min_value=data.index.min().time(), max_value=data.index.max().time(), value=data.index.min().time())
    end_time = st.slider("End Time", min_value=data.index.min().time(), max_value=data.index.max().time(), value=data.index.max().time())
    filtered_data = data.between_time(start_time.strftime('%H:%M'), end_time.strftime('%H:%M'))

    st.subheader("🔍 Latest Signals")
    st.dataframe(filtered_data[['Close', 'EMA_20', 'EMA_50', 'RSI', 'Signal']].tail())
    
    kite = get_kite_session()

st.subheader("📈 Signal Execution")
for index, row in filtered_data.iterrows():
    if 'Symbol' not in row or pd.isna(row['Symbol']):
        st.warning(f"⚠️ Skipping row at {index}: No symbol found")
        continue

    symbol = row['Symbol']
    signal = row['Signal']

    if signal == "BUY":
        st.success(f"{symbol} @ {index}: Buy Signal")
        if live_mode:
            try:
                order = execute_trade(kite, symbol, signal)
                st.write(f"🟢 Order placed: {order['order_id']}")
            except Exception as e:
                st.error(f"❌ Trade failed: {e}")

    elif signal == "SELL":
        st.error(f"{symbol} @ {index}: Sell Signal")
        if live_mode:
            try:
                order = execute_trade(kite, symbol, signal)
                st.write(f"🔴 Order placed: {order['order_id']}")
            except Exception as e:
                st.error(f"❌ Trade failed: {e}")

   

    st.subheader("📊 Price Chart with EMA Signals")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=filtered_data.index, open=filtered_data['Open'], high=filtered_data['High'], low=filtered_data['Low'], close=filtered_data['Close'], name='Price'))
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['EMA_20'], line=dict(color='blue'), name='EMA 20'))
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['EMA_50'], line=dict(color='orange'), name='EMA 50'))
    fig.add_trace(go.Scatter(x=filtered_data[filtered_data['Signal'] == 'BUY'].index, y=filtered_data[filtered_data['Signal'] == 'BUY']['Close'], mode='markers', marker=dict(color='green', symbol='triangle-up'), name='BUY'))
    fig.add_trace(go.Scatter(x=filtered_data[filtered_data['Signal'] == 'SELL'].index, y=filtered_data[filtered_data['Signal'] == 'SELL']['Close'], mode='markers', marker=dict(color='red', symbol='triangle-down'), name='SELL'))
    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=False, key=f"price_chart_{index}")

    st.subheader("📉 RSI Indicator")
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['RSI'], line=dict(color='purple'), name='RSI'))
    fig_rsi.update_layout(height=300)
    st.plotly_chart(fig_rsi, use_container_width=False, key=f"rsi_chart_{index}")

# 📋 Tab 2: Trades
with tab2:
    st.subheader("📋 Trade Summary")

    trade_log = [
        {"Time": "2025-08-23 09:20", "Signal": "BUY", "Price": 152.5, "Result": "+₹120"},
        {"Time": "2025-08-23 10:15", "Signal": "SELL", "Price": 154.2, "Result": "-₹80"},
        {"Time": "2025-08-23 11:05", "Signal": "BUY", "Price": 153.0, "Result": "+₹60"}
    ]

    df_trades = pd.DataFrame(trade_log)
    pnl_values = [int(t["Result"].replace("₹", "").replace("+", "").replace("-", "-")) for t in trade_log]
    total_pnl = sum(pnl_values)
    win_rate = round(100 * sum(1 for p in pnl_values if p > 0) / len(pnl_values), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Total PnL", f"₹{total_pnl}", delta=f"{'↑' if total_pnl > 0 else '↓'}₹{abs(total_pnl)}")
    with col2:
        st.metric("✅ Win Rate", f"{win_rate}%", delta=f"{'↑' if win_rate > 50 else '↓'}")

    st.dataframe(df_trades, use_container_width=True)

