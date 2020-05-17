import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import sys

def get_cagr(data, col, annualized_const):
    df = data.copy(deep=True)
    df['cum_return'] = (1 + df[col]).cumprod()
    n_year = len(df) / annualized_const
    cagr = df['cum_return'][-2:-1] ** (1/n_year) - 1
    return np.round(cagr.tolist()[0], 3)

def get_volatility(data, col, annualized_const):
    df = data.copy(deep=True)
    vol = df[col].std() * np.sqrt(annualized_const)
    return vol

def get_sharpe(data, col, rf_rate, annualized_const):
    df = data.copy(deep=True)
    sharpe = (get_cagr(df, col, annualized_const) - rf_rate) / get_volatility(df, col, annualized_const)
    return np.round(sharpe, 3)

def get_sortino(data, col, rf_rate, annualized_const):
    df = data.copy(deep=True)
    vol = df[df[col] < 0][col].std() * np.sqrt(annualized_const)
    sortino = (get_cagr(df, col, annualized_const) - rf_rate) / vol
    return sortino

def get_max_drawdown(data, col):
    df = data.copy(deep=True)
    df['cum_return'] = (1 + df[col]).cumprod()
    df['cum_roll_max'] = df['cum_return'].cummax()
    df['drawdown'] = df['cum_roll_max'] - df['cum_return']
    df['drawdown_pct'] = df['drawdown'] / df['cum_roll_max']
    max_drawdown = df['drawdown_pct'].max()
    return np.round(max_drawdown, 3)

def get_calmar(data, col, annualized_const):
    df = data.copy(deep=True)
    calmar = get_cagr(df, col, annualized_const) / get_max_drawdown(df, col)
    return calmar
