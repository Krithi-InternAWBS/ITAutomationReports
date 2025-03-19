import pandas as pd
from itautomationreports.filters import filter_by_time

def test_filter_by_time():
    df = pd.DataFrame({
        "Request time": pd.date_range(start="2025-01-01", periods=100, freq='D')
    })

    filtered_df_90 = filter_by_time(df, "Last 90 Days")
    assert len(filtered_df_90) <= 90

    filtered_df_30 = filter_by_time(df, "Last 30 Days")
    assert len(filtered_df_30) <= 30
