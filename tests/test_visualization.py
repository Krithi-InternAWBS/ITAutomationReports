import pytest
import pandas as pd
from itautomationreports.visualizations import plot_sla_compliance

@pytest.fixture
def sample_df():
    return pd.DataFrame({"SLA Met": [0.8, 0.9, 1.0]})

def test_plot_sla_compliance(sample_df):
    try:
        plot_sla_compliance(sample_df)  # Should run without errors
    except Exception as e:
        pytest.fail(f"plot_sla_compliance failed: {e}")
