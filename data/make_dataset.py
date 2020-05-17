
import pandas as pd
import pandas_datareader as pdr
import datetime
import click

from itertools import combinations
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.timeseries import TimeSeries

# Main function
def get_stocks_data(tickers, start_date, end_date,interval='d', attemps=5, handle_nan = None):
    close_prices = pd.DataFrame()
    attempt = 0
    drop = []

    while len(tickers) > 0 and attemps <= 5:
        tickers = [j for j in tickers if j not in drop]
        for tick in tickers:
            print(f"{tick} is being loaded...")
            try:
                tmp = pdr.get_data_yahoo(tick, start_date, end_date, interval=interval)
                tmp.dropna(inplace=True)
                close_prices[tick] = tmp['Adj Close']
                drop.append(tick)
            except:
                print(f"{tick}: failed to fetch data...retrying!")
                continue
        attempt+=1
        if attempt > 0:
            print(f"Attemps: {attempt} for {tick}")
        if handle_nan is not None:
            try:
                close_prices.fillna(method=handle_nan, axis=0, inplace=True)
            except ValueError:
                raise ValueError(f"Invalid fill method. Expecting pad (ffill) or backfill (bfill). Got {handle_nan}")
            
    return(close_prices)

def get_stock_intraday(key, symbols, interval='5min'):
    ohlc_intraday = {}
    ts = TimeSeries(key=key, output_format='pandas')

    attempt = 0
    drop = []
    while len(symbols) != 0 and attempt <= 3:
        symbols = [j for j in symbols if j not in drop]
        for ticker in symbols:
            click.secho(ticker, bold=True)
            try:
                ohlc_intraday[ticker] = ts.get_intraday(symbol=ticker, interval='5min', outputsize='full')[0]
                ohlc_intraday[ticker].columns = ["Open","High","Low","Adj Close","Volume"]
                ohlc_intraday[ticker].sort_values(by='date', inplace=True)
                drop.append(ticker)
            except:
                print(f"{ticker}: failed to fetch data... retrying.")
                continue
        attempt += 1
    return ohlc_intraday

def get_fx(key, symbols, interval='1min', dropna=False):
    pairs = list(combinations(symbols, 2))
    fx = ForeignExchange(key=key, output_format='pandas')
    close_prices = pd.DataFrame()
    attempt = 0
    drop = []
    while len(pairs) > 0 and attempt <= 5:
        pairs = [p for p in pairs if p not in drop]
        for pair in pairs:
            click.secho(f"{pair[0]}/{pair[1]}", bold=True)
            try:
                (data, _) = fx.get_currency_exchange_intraday(from_symbol=pair[0], to_symbol=pair[1], interval=interval, outputsize='full')
                close_prices[pair[0] + "/" + pair[1]] = data['4. close']
                drop.append(pair)
            except:
                print(f"{pair[0]}/{pair[1]}: failed to fetch data ... retrying!")
                continue
        attempt += 1
    if dropna:
        close_prices.dropna(inplace=True)
    return(close_prices)

def get_stats(df: pd.DataFrame):
    #Daily returns
    daily_return = df.pct_change()
    mean = daily_return.mean()
    median = daily_return.median()
    std = daily_return.std()
    # Rolling
    roll_mean = daily_return.rolling(window=10, min_periods=0).mean()
    roll_std = daily_return.rolling(window=10, min_periods=0).std()
    # Exponential moving average
    ewm = daily_return.ewm(span=10, min_periods=0).mean()
    return daily_return


if __name__ == "__main__":
    tickers = ['EFX', 'FB', 'BRK-B', 'AC.TO', 'MDF.TO', 'AAPL', 'MSFT', 'VOO']
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(3650)
    data = get_stocks_data(tickers, start_date, end_date, handle_nan='backfill')
    get_stats(data)
