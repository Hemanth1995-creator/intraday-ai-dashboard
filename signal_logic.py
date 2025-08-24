import yfinance as yf
import pandas as pd
import ta

def get_signal_data():
    ticker = yf.Ticker("RELIANCE.NS")
    data = ticker.history(period="1d", interval="5m")
    data.dropna(inplace=True)

    data['EMA_20'] = ta.trend.ema_indicator(data['Close'], window=20)
    data['EMA_50'] = ta.trend.ema_indicator(data['Close'], window=50)
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    data['VWAP'] = (data['Volume'] * (data['High'] + data['Low']) / 2).cumsum() / data['Volume'].cumsum()

    def generate_signal(row):
        if row['EMA_20'] > row['EMA_50'] and row['RSI'] > 55:
            return 'BUY'
        elif row['EMA_20'] < row['EMA_50'] and row['RSI'] < 45:
            return 'SELL'
        else:
            return 'HOLD'

    data['Signal'] = data.apply(generate_signal, axis=1)
    return data
