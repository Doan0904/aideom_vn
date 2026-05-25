import pytest
import pandas as pd
from src.m3_allocation_optimization import ResourceOptimizer

def test_optimize_allocation():
    optimizer = ResourceOptimizer()
    total_budget = 1000
    df_res = optimizer.optimize_allocation(total_budget=total_budget, scenario='S5')
    
    assert isinstance(df_res, pd.DataFrame)
    assert abs(df_res['Allocated_Budget'].sum() - total_budget) < 0.01, "Tổng phân bổ phải bằng tổng ngân sách"