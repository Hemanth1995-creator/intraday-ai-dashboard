from kiteconnect import KiteConnect

api_key = "570sqm3a3z576zvy"
api_secret = "3f5ch3fpjh1w9ruwdiwu20p4j6t53ize"
request_token = "NPDJ1SBVx5DdnARczDvPUM3HtYtsshIC"  # Paste your token here

kite = KiteConnect(api_key=api_key)
data = kite.generate_session(request_token, api_secret=api_secret)
kite.set_access_token(data["access_token"])

print("✅ Access token generated successfully!")

# order = kite.place_order(
    # variety=kite.VARIETY_REGULAR,
   # exchange=kite.EXCHANGE_NSE,
   # tradingsymbol="RELIANCE",
   # transaction_type=kite.TRANSACTION_TYPE_BUY,
   # quantity=10,
   # order_type=kite.ORDER_TYPE_MARKET,
   # product=kite.PRODUCT_MIS
#)

#print("🟢 Order placed successfully!")
#print(order)

# At the end of kite_auth.py
def get_kite_session():
    return kite


