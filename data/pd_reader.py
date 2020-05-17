import pandas as pd
import pandas_datareader as pdr
import datetime as dt


def get_stocks(tickers, start_date, end_date, interval='d', attemps=5):
    stock_cp = pd.DataFrame()
    attemps = 0
    drop = []

    while len(tickers) != 0 and attemps <= 5:
        tickers = [j for j in tickers if j not in drop]
        for tick in tickers:
            print(tick)
            try:
                temp =  
                temp.dropna(inplace=True)
                stock_cp[tick] = temp["Adj Close"]
                drop.append(tick)
            except:
                print(tick, ":failed to fetch data from API...retrying")
                continue
        attemps += 1
    return(stock_cp)

if __name__ == "__main__":
    tickers = ['EFX', 'BRK-B', 'AC.TO', 'MDF.TO', 'VOO', 'AAPL', 'MSFT']
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(365)
    data = get_stocks(tickers, start_date, end_date)
