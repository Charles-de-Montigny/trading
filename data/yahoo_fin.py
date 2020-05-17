import pandas as pd
import datetime as dt

from yahoofinancials import YahooFinancials

def get_stocks(tickers, start_date, end_date, interval='daily'):
    close_prices = pd.DataFrame()
    attempt = 0
    drop = []
    while len(tickers) > 0 and attempt <=5:
        tickers = [j for j in tickers if j not in drop]
        for tick in tickers:
            print(tick)
            try:
                yahoo_fin = YahooFinancials(tick)
                json_data = yahoo_fin.get_historical_price_data(start_date, end_date, interval)
                prices = json_data[tick]['prices']
                tmp = pd.DataFrame(prices)[['formatted_date', 'adjclose']]
                tmp.set_index("formatted_date", inplace=True)
                tmp = tmp[~tmp.index.duplicated(keep='first')]
                close_prices[tick] = tmp['adjclose']
                drop.append(tick)
            except:
                print(f"{tick}: failed to fetch data ... retrying!")
                continue
        attempt += 1
    return(close_prices)

if __name__ == "__main__":
    tickers = ['EFX', 'BRK-B', 'AC.TO', 'MDF.TO', 'VOO', 'AAPL', 'MSFT']
    end_date = (dt.date.today()).strftime("%Y-%m-%d")
    start_date = (dt.date.today() - dt.timedelta(365)).strftime("%Y-%m-%d")
    data = get_stocks(tickers, start_date, end_date)
