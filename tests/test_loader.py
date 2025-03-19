import pytest
import pandas as pd
from io import BytesIO
from itautomationreports.data_loader import load_data, clean_data

@pytest.fixture
def sample_excel():
    data = {"Request time": ["2025-01-01", "2025-02-01"], "SLA Met": [1, 0]}
    df = pd.DataFrame(data)
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    return excel_buffer

def test_load_data(sample_excel):
    df, file_names = load_data([sample_excel])
    assert not df.empty
    assert "Source" in df.columns

def test_clean_data():
    raw_data = {"Request time": ["2025-01-01", None], "SLA Met": ["1", "0"]}
    df = pd.DataFrame(raw_data)
    cleaned_df = clean_data(df)
    assert cleaned_df["Request time"].isna().sum() == 1
    assert cleaned_df["SLA Met"].dtype == float
