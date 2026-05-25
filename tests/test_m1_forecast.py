import pytest
import pandas as pd
from src.m1_economic_forecast import EconomicForecaster

def test_forecast_gdp():
    forecaster = EconomicForecaster()
    # Sửa lại tham số gọi hàm: đổi thành target_year=2030
    df_res = forecaster.forecast_gdp(target_year=2030, scenario='S3')
    
    assert isinstance(df_res, pd.DataFrame), "Kết quả phải là DataFrame"
    assert len(df_res) == 6, "Phải dự báo đủ 6 năm (2025-2030)"
    assert 'GDP_Billion_USD' in df_res.columns, "Thiếu cột GDP"
    assert df_res['Scenario'].iloc[0] == 'S3', "Sai kịch bản"