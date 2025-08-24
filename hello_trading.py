import yfinance as yf
import pandas as pd

# Fetch data for a sample stock (e.g., Reliance)
ticker = yf.Ticker("RELIANCE.NS")
data = ticker.history(period="1d", interval="5m")

# Show the latest 5 rows
print("📊 Latest 5-minute data for RELIANCE:")
print(data.tail())
