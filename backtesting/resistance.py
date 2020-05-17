import pandas as pd
import numpy as np
import sys
import datetime 
import click
import os
from path import Path
from itertools import product

sys.path.append('../')

from technical_indicator.atr import get_atr
from kpi import get_cagr, get_volatility, get_sharpe, get_max_drawdown
from data.make_dataset import get_fx

if __name__ == '__main__':
    key_path = '../key.txt'
    symbols = ['EUR', 'USD', 'CAD', 'JPY']
    data = get_fx(key = open(key_path, 'r').read(), symbols=symbols, interval='5min', dropna=True)
    import pdb; pdb.set_trace()