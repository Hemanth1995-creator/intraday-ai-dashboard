import streamlit as st
st.markdown("""
    <style>
    .fade-in {
        animation: fadeIn 2s ease-in forwards;
        opacity: 0;
    }

    @keyframes fadeIn {
        to {
            opacity: 1;
        }
    }
    </style>
""", unsafe_allow_html=True)
st.markdown('<img src="ironman.jpeg" class="fade-in" width="300">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.image("ironman.jpeg", width=150)

with col2:
    st.write("Welcome to your AI-powered intraday dashboard!")


import time
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

import pandas as pd
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
from signal_logic import get_signal_data

# 📊 Load signal data early
data = get_signal_data()

# 🎨 Custom Styling
st.set_page_config(page_title="Zerodha Signal Dashboard", layout="wide")

# Inject CSS for background and font
st.markdown("""
    <style>
        body {
            background-color: #f5f7fa;
            font-family: 'Segoe UI', sans-serif;
        }
        .stApp {
            background-color: #f5f7fa;
        }
        .metric {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 10px;
            margin: 5px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            color: #0a3d62;
        }
    </style>
""", unsafe_allow_html=True)

# 🎯 Branded Sidebar
st.sidebar.image("https://zerodha.com/static/images/logo.svg", width=150)
st.sidebar.markdown("## 🚀 Zerodha Signal Engine")
st.sidebar.markdown("Welcome, Hemanth 👋")

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json"
lottie_json = load_lottieurl(lottie_url)

st_lottie(lottie_json, speed=1, height=150, key="hello")
st.markdown("## 🚀 Welcome to Zerodha Signal Engine")



# 🎨 Styling
st.markdown("""
    <style>
    .main {background-color: #f5f5f5;}
    h1, h2, h3 {color: #2E86C1;}
    .stMetric {background-color: #eaf2f8; border-radius: 10px;}
    div[data-testid="stMetric"] > div {background-color: #eaf2f8; padding: 10px; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

# 🖼️ Branding
st.image("ironman.jpeg", width=150)
st.markdown("### Powered by IntradayAI 🚀")

# 🔄 Lottie Animation
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_trading = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_1pxqjqps.json")
st_lottie(lottie_trading, height=300)

# 🔁 Auto-refresh every 5 minutes
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=300000, limit=100, key="refresh")

# 🚦 Live Mode Toggle
st.sidebar.header("⚙️ Settings")
live_mode = st.sidebar.toggle("Live Trading Mode", value=False)

# 🧠 Display Current Mode
mode_status = "🟢 LIVE MODE" if live_mode else "🧪 SIMULATION MODE"
st.sidebar.markdown(f"### {mode_status}")


# 🗂️ Tabs
tab1, tab2, tab3 = st.tabs(["📈 Signals", "📋 Trades", "📊 Strategy Audit"])


with tab1:
    # 📅 Time Filter
    st.subheader("🕒 Filter by Time Range")
    start_time = st.slider("Start Time", min_value=data.index.min().time(), max_value=data.index.max().time(), value=data.index.min().time())
    end_time = st.slider("End Time", min_value=data.index.min().time(), max_value=data.index.max().time(), value=data.index.max().time())

    filtered_data = data.between_time(start_time.strftime('%H:%M'), end_time.strftime('%H:%M'))

    # 🔍 Signal Table
    st.subheader("🔍 Latest Signals")
    st.dataframe(filtered_data[['Close', 'EMA_20', 'EMA_50', 'RSI', 'Signal']].tail())

    # 📈 Candlestick Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=filtered_data.index,
        open=filtered_data['Open'],
        high=filtered_data['High'],
        low=filtered_data['Low'],
        close=filtered_data['Close'],
        name='Price'
    ))
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['EMA_20'], line=dict(color='blue'), name='EMA 20'))
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['EMA_50'], line=dict(color='orange'), name='EMA 50'))

    buy_signals = filtered_data[filtered_data['Signal'] == 'BUY']
    sell_signals = filtered_data[filtered_data['Signal'] == 'SELL']
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', marker=dict(color='green', symbol='triangle-up'), name='BUY'))
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', marker=dict(color='red', symbol='triangle-down'), name='SELL'))

    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=False)

    # 📉 RSI Chart
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['RSI'], line=dict(color='purple'), name='RSI'))
    fig_rsi.update_layout(height=300)
    st.plotly_chart(fig_rsi, use_container_width=False)


with tab2:
    st.subheader("📋 Trade Summary")

    # Simulated trade log
    trade_log = [
        {"Time": "2025-08-23 09:20", "Signal": "BUY", "Price": 152.5, "Result": "+₹120"},
        {"Time": "2025-08-23 10:15", "Signal": "SELL", "Price": 154.2, "Result": "-₹80"},
        {"Time": "2025-08-23 11:05", "Signal": "BUY", "Price": 153.0, "Result": "+₹60"},
    ]

    df_trades = pd.DataFrame(trade_log)

    # Calculate metrics
    pnl_values = [int(t["Result"].replace("₹", "").replace("+", "").replace("-", "-")) for t in trade_log]
    total_pnl = sum(pnl_values)
    win_rate = round(100 * sum(1 for p in pnl_values if p > 0) / len(pnl_values), 2)

    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Total PnL", f"₹{total_pnl}", delta=f"{'↑' if total_pnl > 0 else '↓'}₹{abs(total_pnl)}")
    with col2:
        st.metric("✅ Win Rate", f"{win_rate}%", delta=f"{'↑' if win_rate > 50 else '↓'}")

    # Display trade log
    st.dataframe(df_trades, use_container_width=True)

with tab3:
    st.subheader("📊 Strategy Audit Panel")

    audit_data = filtered_data.copy() if 'filtered_data' in locals() else data.copy()

    audit_data['Hour'] = audit_data.index.hour
    signal_counts = audit_data.groupby(['Hour', 'Signal']).size().unstack(fill_value=0)
    st.markdown("#### 🔥 Signal Distribution by Hour")
    st.dataframe(signal_counts)

    audit_data['Combo'] = audit_data.apply(
        lambda row: f"EMA{int(row['EMA_20'] > row['EMA_50'])}_RSI{int(row['RSI'] > 50)}", axis=1
    )
    combo_perf = audit_data.groupby('Combo')['Signal'].value_counts().unstack(fill_value=0)
    st.markdown("#### 🧠 Indicator Combo Breakdown")
    st.dataframe(combo_perf)

    total_signals = len(audit_data)
    buy_signals = len(audit_data[audit_data['Signal'] == 'BUY'])
    sell_signals = len(audit_data[audit_data['Signal'] == 'SELL'])
    signal_score = round((buy_signals + sell_signals) / total_signals * 100, 2)

    st.metric("📈 Signal Coverage", f"{signal_score}%")
    st.metric("🟢 BUY Signals", f"{buy_signals}")
    st.metric("🔴 SELL Signals", f"{sell_signals}")


with col1:
    st.metric("💰 Total PnL", f"₹{total_pnl}", delta=f"{'↑' if total_pnl > 0 else '↓'}₹{abs(total_pnl)}")
with col2:
    st.metric("✅ Win Rate", f"{win_rate}%", delta=f"{'↑' if win_rate > 50 else '↓'}")


    # Use filtered_data from tab1 if available
    audit_data = filtered_data.copy() if 'filtered_data' in locals() else data.copy()

    # Time-based signal heatmap
    audit_data['Hour'] = audit_data.index.hour
    signal_counts = audit_data.groupby(['Hour', 'Signal']).size().unstack(fill_value=0)

    st.markdown("#### 🔥 Signal Distribution by Hour")
    st.dataframe(signal_counts)

    # Indicator combo performance (simplified)
    audit_data['Combo'] = audit_data.apply(
        lambda row: f"EMA{int(row['EMA_20'] > row['EMA_50'])}_RSI{int(row['RSI'] > 50)}", axis=1
    )
    combo_perf = audit_data.groupby('Combo')['Signal'].value_counts().unstack(fill_value=0)

    st.markdown("#### 🧠 Indicator Combo Breakdown")
    st.dataframe(combo_perf)

    # Adaptive scoring (mocked for now)
    total_signals = len(audit_data)
    buy_signals = len(audit_data[audit_data['Signal'] == 'BUY'])
    sell_signals = len(audit_data[audit_data['Signal'] == 'SELL'])
    signal_score = round((buy_signals + sell_signals) / total_signals * 100, 2)

    st.metric("📈 Signal Coverage", f"{signal_score}%")
    st.metric("🟢 BUY Signals", f"{buy_signals}")
    st.metric("🔴 SELL Signals", f"{sell_signals}")

    # Simulated trade log (replace with real trades if live_mode is True)
    trade_log = [
        {"Time": "2025-08-23 09:20", "Signal": "BUY", "Price": 152.5, "Result": "+₹120"},
        {"Time": "2025-08-23 10:15", "Signal": "SELL", "Price": 154.2, "Result": "-₹80"},
        {"Time": "2025-08-23 11:05", "Signal": "BUY", "Price": 153.0, "Result": "+₹60"},
    ]

    df_trades = pd.DataFrame(trade_log)

    # Calculate metrics
    pnl_values = [int(t["Result"].replace("₹", "").replace("+", "").replace("-", "-")) for t in trade_log]
    total_pnl = sum(pnl_values)
    win_rate = round(100 * sum(1 for p in pnl_values if p > 0) / len(pnl_values), 2)

    # Display metrics
    st.metric("💰 Total PnL", f"₹{total_pnl}")
    st.metric("✅ Win Rate", f"{win_rate}%")

    # Display trade log
    st.dataframe(df_trades, use_container_width=True)

# Page setup
st.set_page_config(page_title="Intraday AI Dashboard", layout="wide")
st.title("📈 Intraday AI Trading Dashboard")

from signal_logic import get_signal_data
# Load signal data
data = get_signal_data()

# 📍 Latest Signals Table
st.subheader("🔍 Latest Signals")
st.dataframe(data[['Close', 'EMA_20', 'EMA_50', 'RSI', 'Signal']].tail())

# 📈 Candlestick Chart with EMA and Signal Markers
st.subheader("📊 Price Chart with EMA Signals")

fig = go.Figure()

# Candlestick
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name='Price'
))

# EMA Overlays
fig.add_trace(go.Scatter(
    x=data.index,
    y=data['EMA_20'],
    line=dict(color='blue', width=1),
    name='EMA 20'
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data['EMA_50'],
    line=dict(color='orange', width=1),
    name='EMA 50'
))

# Signal Markers
buy_signals = data[data['Signal'] == 'BUY']
sell_signals = data[data['Signal'] == 'SELL']

fig.add_trace(go.Scatter(
    x=buy_signals.index,
    y=buy_signals['Close'],
    mode='markers',
    marker=dict(color='green', size=8, symbol='triangle-up'),
    name='BUY'
))

fig.add_trace(go.Scatter(
    x=sell_signals.index,
    y=sell_signals['Close'],
    mode='markers',
    marker=dict(color='red', size=8, symbol='triangle-down'),
    name='SELL'
))

fig.update_layout(
    xaxis_rangeslider_visible=False,
    height=600,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig, use_container_width=False)

# 📊 RSI Chart
st.subheader("📉 RSI Indicator")

fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(
    x=data.index,
    y=data['RSI'],
    line=dict(color='purple'),
    name='RSI'
))
fig_rsi.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig_rsi, use_container_width=False)

st.markdown("---")
st.markdown("Made with ❤️ by Hemanth | Powered by Copilot | Version 1.0", unsafe_allow_html=True)
