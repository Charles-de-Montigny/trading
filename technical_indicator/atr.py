import pandas as pd
import numpy as np

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