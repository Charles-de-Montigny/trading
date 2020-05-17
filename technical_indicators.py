import pandas as pd
import numpy as np
import datetime
import statsmodels.api as sm

from stocktrends import Renko
from sklearn.linear_model import LinearRegression


def get_bolling_bands(data, n):
    """This function compute the Bollinger Bands"""
    df = data.copy()
    df['MA'] = df['Adj Close'].rolling(n).mean()
    df["upper_band"] = df['MA'] + 1.96 * df['Adj Close'].rolling(n).std()
    df["lower_band"] = df['MA'] - 1.96 * df['Adj Close'].rolling(n).std()
    df['range'] = df['upper_band'] - df['lower_band']
    df.dropna(axis=0, inplace=True)
    return df


def get_atr(data, n=20):
    """Function to compute the Average True Range"""
    df = data.copy()
    df['HL'] = np.abs(df['High'] - df['Low'])
    df['HPC'] = np.abs(df['High'] - df['Adj Close'].shift(1))
    df['LPC'] = np.abs(df['Low'] - df['Adj Close'].shift(1))
    df['TR'] = df[['HL', 'HPC', 'LPC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    atr = df['ATR'].values
    return atr


def get_macd(df, col, fast_span=12, slow_span=26, signal_span=9):
    df['ma_fast'] = df[col].ewm(span=fast_span, min_periods=fast_span).mean()
    df['ma_slow'] = df[col].ewm(span=slow_span, min_periods=slow_span).mean()
    df['macd'] = df['ma_fast'] - df['ma_slow']
    df['signal'] = df['macd'].ewm(span=signal_span, min_periods=signal_span).mean()
    df.dropna(inplace=True)
    return df['macd'].tolist(), df['signal'].tolist()


def get_adx(data, n):
    """Function to calculate ADX."""
    def get_true_range(data):
        if isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise TypeError("Data must be a Pandas DataFrame.")
        df['HL'] = np.abs(df['High'] - df['Low'])
        df['HPC'] = np.abs(df['High'] - df['Adj Close'].shift(1))
        df['LPC'] = np.abs(df['Low'] - df['Adj Close'].shift(1))
        df['TR'] = df[['HL', 'HPC', 'LPC']].max(axis=1, skipna=False)
        return df
    
    # True Range
    df = get_true_range(data)
    # DM plus & minus
    high_diff = df['High']-df['High'].shift(1)
    low_diff = df['Low'].shift(1)-df['Low']
    df['DM+'] = np.where(high_diff > low_diff, high_diff, 0)
    df['DM+'] = np.where(df['DM+'] < 0, 0, df['DM+'])
    df['DM-'] = np.where(low_diff > high_diff, low_diff, 0)
    df['DM-'] = np.where(df['DM-'] < 0, 0, df['DM-'])
    # Populate TR_{n}, DM+_{n} & DM-_{n}
    TR_n, DMplus_n, DMminus_n = [], [], []
    TR = df['TR'].values
    DMplus = df['DM+'].values
    DMminus = df['DM-'].values
    for i in range(df.shape[0]):
        if i < n:
            TR_n.append(np.nan)
            DMplus_n.append(np.nan)
            DMminus_n.append(np.nan)
        elif i == n:
            TR_n.append(df['TR'].rolling(n).sum().tolist()[n])
            DMplus_n.append(df['DM+'].rolling(n).sum().tolist()[n])
            DMminus_n.append(df['DM-'].rolling(n).sum().tolist()[n])
        elif i > n:
            TR_n.append(TR_n[i-1] - (TR_n[i-1]/14) + TR[i])
            DMplus_n.append(DMplus_n[i-1] - (DMplus_n[i-1]/n) + DMplus[i])
            DMminus_n.append(DMminus_n[i-1] - (DMminus_n[i-1]/n) + DMminus[i])
        else:
            raise ValueError(f"i ({i}) was not ><= relative to n ({n})")
    df['TR_n'] = TR_n
    df['DM+_n'] = DMplus_n
    df['DM-_n'] = DMminus_n
    
    df['DI+_n'] = 100 * (df['DM+_n'] / df['TR_n'])
    df['DI-_n'] = 100 * (df['DM-_n'] / df['TR_n'])
    df['DIdiff'] = np.abs(df['DI+_n'] - df['DI-_n'])
    df['DIsum'] = df['DI+_n'] + df['DI-_n']
    df['DX'] = 100 * (df['DIdiff'] / df['DIsum'])
    ADX = []
    DX = df['DX'].values
    for j in range(df.shape[0]):
        if j < 2 * n - 1:
            ADX.append(np.nan)
        elif j == 2 * n - 1:
            ADX.append(df['DX'][j - n + 1: j+1].mean())
        elif j > 2 * n - 1:
            ADX.append(((n-1) * ADX[j - 1] + DX[j]) / n)
    return ADX


def get_renko(data):
    """Compute renko bars"""
    df = data.copy()
    df.reset_index(inplace=True)
    df.columns = ["date", "open", 'high', "low", "close", "volume"]
    renko = Renko(df)
    renko.brick_size = max(0.5, round(get_atr(data,n=120)[-1], 0))
    renko_df = renko.get_ohlc_data()
    renko_df['bar_num'] = np.where(renko_df['uptrend']==True, 1, \
        np.where(renko_df['uptrend']==False, -1, 0))
    renko_df['renko_bar'] = 1
    for i in range(1, len(renko_df)):
        if renko_df['bar_num'][i] > 0 and renko_df['bar_num'][i-1] > 0:
            renko_df['renko_bar'][i] += renko_df['renko_bar'][i-1]
        elif renko_df['renko_bar'][i] < 0 and renko_df['renko_bar'][i-1] < 0:
            renko_df['renko_bar'][i] += renko_df['renko_bar'][i-1]
    renko_df.drop_duplicates(subset='date', keep='last', inplace=True)
    return renko_df


def get_obv(data):
    """Function to compute On Balance Volume"""
    df = data.copy(deep=True)
    df['daily_returns'] = df['Adj Close'].pct_change()
    df['direction'] = np.where(df['daily_returns'] >= 0, 1, -1)
    df['direction'][0] = 0
    df['vol_adj'] = df['Volume'] * df['direction']
    obv = df['vol_adj'].cumsum()
    return obv.to_list()


def get_slopes(data, n=5, degree=False):
    """Function to compute the slope of every points."""
    if isinstance(data, pd.DataFrame):
        var = data['Adj Close']
    elif isinstance(data, pd.Series):
        var = data.copy(deep=True)
    else:
        raise TypeError("data must be a pandas DataFrame or Series.")
    slopes = [0 for i in range(n-1)]
    for i in range(n, len(var)+1):
        y = var[i-n:i]
        X = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        X_scaled = (X - X.min())/(X.max() - X.min())
        X_scaled = sm.add_constant(X_scaled)
        ols = LinearRegression()
        ols.fit(X_scaled, y_scaled)
        slopes.append(ols.coef_[-1])
    if degree:
        slopes = (np.rad2deg(np.arctan(np.array(slopes))))
    return slopes