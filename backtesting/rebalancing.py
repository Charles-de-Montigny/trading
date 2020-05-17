import pandas as pd
import numpy as np
import sys
import datetime 
import click
import os
from path import Path
from itertools import product

sys.path.append('../')

from kpi import get_cagr, get_volatility, get_sharpe, get_max_drawdown
from data.make_dataset import get_stocks_data

def rebalancing(data: pd.DataFrame, m: int, x: int, verbose: bool = False) -> pd.DataFrame:
    """Returns cumulative portfolio return for the rebalancing strategy.
    
    Args:
        data: pandas DataFrame
            DataFrame with closing price for all stocks.
        m: int
            Number of stock in the portfolio.
        x: int
            Number of underperforming stocks to be removed from portfolio monthly.
        verbose: bool
            Print the stocks in the portfolio at every step.
    """
    # Parse arguments
    assert isinstance(data, pd.DataFrame), "Data must be in a pandas DataFrame."
    assert m > x, f"The number of stocks m: {m} is larger or equal than the number of stocks x: {x} to remove."
    
    # Setup
    df = data.copy(deep=True)
    tickers = df.columns
    # Compute monthly returns
    returns = pd.DataFrame()
    for ticker in tickers:
        returns[ticker] = df[ticker].pct_change()
    returns.dropna(inplace=True)
    T = returns.shape[0]

    # Portfolio
    fill = m - x
    portfolio = []
    m_returns = []
    for i in range(T):
        if portfolio:
            m_returns.append(returns[portfolio].iloc[i, :].mean())
            worst_stocks = returns[portfolio].iloc[i, :].sort_values(ascending=True)[:x].index.to_list()
            portfolio = [t for t in portfolio if t not in worst_stocks]
        new_stocks = returns.iloc[i, :].sort_values(ascending=False)[:fill].index.to_list()
        portfolio += new_stocks
        if verbose:
            print(portfolio)

    return pd.DataFrame({'monthly_return':m_returns})

def _compute_metrics(monthly_return, annualized_const, risk_free_rate):
    metrics = {}
    metrics['cagr'] = get_cagr(monthly_return, "monthly_return", annualized_const)
    metrics['sharpe_ratio'] = get_sharpe(monthly_return, "monthly_return", risk_free_rate, annualized_const)
    metrics['max_dd'] = get_max_drawdown(monthly_return, "monthly_return")
    return metrics

def _print_metrics(metrics: dict, type: str):
    click.secho(f"\nKPIs of the {type}:", bold=True)
    click.secho("--------------------------", bold=True)
    click.secho(f"\nCAGR: {metrics['cagr']}", bold=True)
    click.secho(f"\nSharpe Ratio: {metrics['sharpe_ratio']}", bold=True)
    click.secho(f"\nMax Drawdown: {metrics['max_dd']}", bold=True)

def backtest_strategy(m, x, benchmark_ticker: str, input_path: Path = None, verbose: bool=True):
    """Backtest the rebalancing strategy.
    
    Args:
        m: int
            Number of stock in the portfolio.
        x: int
            Number of underperforming stocks to be removed from portfolio monthly.
        benchmark_ticker: str
            The ticker of the benchmark stock/ETF.
        input_path: Path default = None
            Path to the input dataset, if it exists.
        verbose: bool
            Whether or not to print the metrics.
    """
    # Load data
    if input_path and os.path.exists(input_path): 
        df = pd.read_csv(input_path, index_col = 'Date')
    else:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(3650)
        tickers = ["^DJI", "MMM","AXP","T","BA","CAT","CVX","CSCO","KO", "XOM","GE","GS","HD",
           "IBM","INTC","JNJ","JPM","MCD","MRK","MSFT","NKE","PFE","PG","TRV",
           "UTX","UNH","VZ","V","WMT","DIS"]
        df = get_stocks_data(tickers, start_date, end_date,interval='m', attemps=5, handle_nan = None)
    benchmark = df.pop(benchmark_ticker)
    benchmark = benchmark.to_frame(name = benchmark_ticker)
    benchmark['monthly_return'] = benchmark[[benchmark_ticker]].pct_change()
    benchmark.dropna(inplace=True)
    # Rebalancing Strategy
    monthly_return = rebalancing(df, m, x)
    # Compute metrics
    strategy_metrics = _compute_metrics(monthly_return, 12, 0.0225)
    benchmark_metrics = _compute_metrics(benchmark, 12, 0.0225)
    # Print metrics
    if verbose:
        _print_metrics(strategy_metrics, type="Rebalancing")
        _print_metrics(benchmark_metrics, type="Benchmark (Dow)")

    return strategy_metrics, benchmark_metrics

def grid_search():
    """Grid Search the hyperparameter of the strategy."""
    # setup
    m = range(2, 11)
    x = range(2, 11)
    p = product(m, x)
    hyperparameter = [(m, x) for (m, x) in p if m > x]
    # grid search
    strategies_metrics = {'sharpe_ratio':[], 'm':[], 'x':[]}
    for m, x in hyperparameter:
        tmp_metrics, _ = backtest_strategy(m, x, benchmark_ticker='^DJI', input_path="../stocks.csv", verbose=False)
        strategies_metrics['sharpe_ratio'].append(tmp_metrics['sharpe_ratio'])
        strategies_metrics['m'].append(m)
        strategies_metrics['x'].append(x)
    return pd.DataFrame(strategies_metrics).sort_values(by=['sharpe_ratio'], ascending=False)

if __name__ == '__main__':
    best_params = grid_search()

