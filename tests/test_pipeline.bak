import pytest
from src.optimization import solve_regional_lp_with_fairness
from src.modules import solve_project_selection_mip

def test_lp_solvability():
    x, val = solve_regional_lp_with_fairness(50000)
    assert val > 0
    assert x.shape == (6, 4)

def test_mip_constraints():
    selected, val, cost = solve_project_selection_mip(80000)
    assert "P14. An ninh mạng SOC" in selected  # Kiểm tra ràng buộc bắt buộc
    assert not ("P1. Trung tâm dữ liệu Hoà Lạc" in selected and "P2. Trung tâm dữ liệu phía Nam" in selected)