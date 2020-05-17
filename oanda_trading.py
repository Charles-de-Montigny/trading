import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import pandas as pd

token_path = "oanda_key.txt"
client = oandapyV20.API(access_token=open(token_path, 'r').read(), environment='practice')
