import pandas as pd
from itautomationreports.comparisons import compare_reports

def test_compare_reports():
    df = pd.DataFrame({
        "Source": ["Report A", "Report B", "Report A", "Report B"],
        "SLA Compliance": [0.9, 0.8, 0.85, 0.82]
    })
    result = compare_reports(df, ["Report A", "Report B"], "SLA Compliance")
    assert not result.empty
    assert "SLA Compliance" in result.columns
