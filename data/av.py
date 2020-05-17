import click
import pandas as pd

from alpha_vantage.foreignexchange import ForeignExchange
from itertools import combinations



def get_fx(key, symbols, interval='1min'):
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
                data, _ = fx.get_currency_exchange_intraday(from_symbol=pair[0], to_symbol=pair[1], interval=interval)
                close_prices[pair[0] + "/" + pair[1]] = data['4. close']
                drop.append(pair)
            except:
                print(f"{pair[0]}/{pair[1]}: failed to fetch data ... retrying!")
                continue
        attempt += 1
        close_prices.set_index(data.index, inplace=True)
    return(close_prices)
