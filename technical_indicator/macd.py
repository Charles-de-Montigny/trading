import pandas as pd
import datetime

def get_macd(df, ticker, fast_span=12, slow_span=26, signal_span=9):
    df['ma_fast'] = df[ticker].ewm(span=fast_span, min_periods=fast_span).mean()
    df['ma_slow'] = df[ticker].ewm(span=slow_span, min_periods=slow_span).mean()
    df['macd'] = df['ma_fast'] - df['ma_slow']
    df['signal'] = df['macd'].ewm(span=signal_span, min_periods=signal_span).mean()
    df.dropna(inplace=True)
    return df
