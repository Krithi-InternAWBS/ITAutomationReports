import pandas as pd

def filter_by_time(df, period):
    if period == "Last 90 Days":
        return df[df['Request time'] >= pd.Timestamp.now() - pd.Timedelta(days=90)]
    elif period == "Last 30 Days":
        return df[df['Request time'] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
    elif period == "Last 7 Days":
        return df[df['Request time'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
    return df
