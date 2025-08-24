import yfinance as yf
import pandas as pd
import ta  # Technical Analysis library

from kite_auth import get_kite_session
kite = get_kite_session()

# Toggle live trading
live_mode = False  # Set to True on market days

# Step 1: Fetch intraday data
ticker = yf.Ticker("RELIANCE.NS")
data = ticker.history(period="1d", interval="5m")
data.dropna(inplace=True)

# Step 2: Add indicators
data['EMA_20'] = ta.trend.ema_indicator(data['Close'], window=20)
data['EMA_50'] = ta.trend.ema_indicator(data['Close'], window=50)
data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
data['VWAP'] = (data['Volume'] * (data['High'] + data['Low']) / 2).cumsum() / data['Volume'].cumsum()

# Step 3: Define signal logic
def generate_signal(row):
    if row['EMA_20'] > row['EMA_50'] and row['RSI'] > 55:
        return 'BUY'
    elif row['EMA_20'] < row['EMA_50'] and row['RSI'] < 45:
        return 'SELL'
    else:
        return 'HOLD'

# Step 4: Apply signal logic
data['Signal'] = data.apply(generate_signal, axis=1)

# Step 5: Risk management and trade logging
capital = 100000  # Starting capital ₹1,00,000
risk_per_trade = 0.02  # Risk 2% of capital per trade
sl_buffer = 0.005  # 0.5% Stop Loss
tp_buffer = 0.01   # 1% Target Profit

trades = []

for i in range(1, len(data)):
    current = data.iloc[i]
    previous = data.iloc[i - 1]

    if previous['Signal'] == 'BUY' and current['Signal'] == 'SELL':
        entry_price = previous['Close']
        exit_price = current['Close']
        sl = entry_price * (1 - sl_buffer)
        tp = entry_price * (1 + tp_buffer)

        risk_amount = capital * risk_per_trade
        sl_distance = abs(entry_price - sl)
        qty = int(risk_amount / sl_distance)

        pnl = (exit_price - entry_price) * qty

        trades.append({
            'Entry Time': previous.name,
            'Exit Time': current.name,
            'Entry Price': round(entry_price, 2),
            'Exit Price': round(exit_price, 2),
            'SL': round(sl, 2),
            'TP': round(tp, 2),
            'Qty': qty,
            'PnL': round(pnl, 2)
        })

        if live_mode:
            order = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NSE,
                tradingsymbol="RELIANCE",
                transaction_type=kite.TRANSACTION_TYPE_BUY,
                quantity=qty,
                order_type=kite.ORDER_TYPE_MARKET,
                product=kite.PRODUCT_MIS
            )
            print("🟢 Live order placed:", order)
        else:
            print(f"🧪 Simulated order: BUY {qty} RELIANCE at ₹{entry_price}")

# Step 6: Display latest signals
print("📍 Latest signals:")
print(data[['Close', 'EMA_20', 'EMA_50', 'RSI', 'Signal']].tail())

# Step 7: Trade summary
print("\n📊 Trade Summary:")
for trade in trades:
    print(trade)

# Step 8: End-of-Day Summary
if trades:
    df_trades = pd.DataFrame(trades)
    total_trades = len(df_trades)
    wins = df_trades[df_trades['PnL'] > 0]
    losses = df_trades[df_trades['PnL'] <= 0]
    total_pnl = df_trades['PnL'].sum()

    print("\n📌 End-of-Day Summary:")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {len(wins)}")
    print(f"Losing Trades: {len(losses)}")
    print(f"Win Rate: {round(len(wins)/total_trades*100, 2)}%")
    print(f"Total PnL: ₹{round(total_pnl, 2)}")
    print(f"Best Trade: ₹{df_trades['PnL'].max()}")
    print(f"Worst Trade: ₹{df_trades['PnL'].min()}")
else:
    print("\n📌 No trades executed today. Market may have lacked clear signals.")
