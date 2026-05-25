import numpy as np
import pandas as pd
import cvxpy as cp

def predict_cobb_douglas(macro_df: pd.DataFrame, target_year: int = 2030, growth_assumptions: dict = None) -> pd.DataFrame:
    """Dự báo quỹ đạo tăng trưởng GDP của Việt Nam đến năm target_year bằng hàm Cobb-Douglas.

    Args:
        macro_df (pd.DataFrame): Dữ liệu vĩ mô lịch sử chứa các cột vốn, lao động, số hóa, AI, con người.
        target_year (int): Năm đích cần dự báo đến (mặc định là 2030).
        growth_assumptions (dict): Giả định tốc độ tăng trưởng của các yếu tố đầu vào.

    Returns:
        pd.DataFrame: Bảng quỹ đạo tăng trưởng từng năm từ năm gốc đến năm mục tiêu.
    """
    alpha, beta, gamma, delta, theta = 0.33, 0.42, 0.10, 0.08, 0.07
    base = macro_df.iloc[-1]
    last_year = int(base['year'])
    
    if growth_assumptions is None:
        growth_assumptions = {
            'K_growth': 1.06, 'L_growth': 1.01,
            'D_growth': 1.15, 'AI_growth': 1.20, 'H_growth': 1.05,
            'A_mean': 0.052, 'A_growth': 1.012
        }
    
    trajectory = []
    current_state = {
        'year': last_year,
        'K': base['K_capital_trillion'], 'L': base['L_labor_million'],
        'D': base['D_digital_index'], 'AI': base['AI_index'], 'H': base['H_human_capital'],
        'A': growth_assumptions.get('A_mean', 0.052)
    }
    
    prev_Y = base['GDP_trillion_VND']
    calibration_factor = 1.0
    
    for y in range(last_year + 1, target_year + 1):
        current_state['year'] = y
        current_state['K'] *= growth_assumptions['K_growth']
        current_state['L'] *= growth_assumptions['L_growth']
        current_state['D'] *= growth_assumptions['D_growth']
        current_state['AI'] *= growth_assumptions['AI_growth']
        current_state['H'] *= growth_assumptions['H_growth']
        current_state['A'] *= growth_assumptions.get('A_growth', 1.012)
        
        Y_pred = (current_state['A']) * \
                 (current_state['K']**alpha) * (current_state['L']**beta) * \
                 (current_state['D']**gamma) * (current_state['AI']**delta) * \
                 (current_state['H']**theta)
        
        if y == last_year + 1:
            calibration_factor = prev_Y / Y_pred if Y_pred > 0 else 1.0
        
        Y_pred_calibrated = Y_pred * calibration_factor
        growth_rate = (Y_pred_calibrated / prev_Y - 1) * 100
        
        trajectory.append({
            'year': y,
            'K': current_state['K'], 'L': current_state['L'],
            'D': current_state['D'], 'AI': current_state['AI'], 'H': current_state['H'],
            'Y_pred': Y_pred_calibrated,
            'growth_rate_pct': growth_rate
        })
        prev_Y = Y_pred_calibrated
        
    return pd.DataFrame(trajectory)

def predict_by_scenario(macro_df: pd.DataFrame, scenarios_dict: dict) -> dict:
    """Tính toán quỹ đạo tăng trưởng GDP cho tất cả các kịch bản đầu tư vĩ mô.

    Args:
        macro_df (pd.DataFrame): Dữ liệu kinh tế vĩ mô nền tảng.
        scenarios_dict (dict): Dictionary chứa tên kịch bản và mảng tỷ lệ phân bổ ngân sách.

    Returns:
        dict: Bản đồ map giữa tên kịch bản và DataFrame chứa quỹ đạo tăng trưởng tương ứng.
    """
    results = {}
    for name, weights in scenarios_dict.items():
        assumptions = {
            'K_growth': 1.0 + (weights[0] * 0.1),
            'D_growth': 1.0 + (weights[1] * 0.5),
            'AI_growth': 1.0 + (weights[2] * 0.8),
            'H_growth': 1.0 + (weights[3] * 0.2),
            'L_growth': 1.01,
            'A_mean': 0.052, 'A_growth': 1.012
        }
        results[name] = predict_cobb_douglas(macro_df, target_year=2030, growth_assumptions=assumptions)
    return results

def allocate_budget(total_budget: float) -> dict:
    """Tối ưu hóa phân bổ ngân sách nhà nước sử dụng CVXPY để đạt lợi ích kinh tế lớn nhất.

    Args:
        total_budget (float): Tổng ngân sách phân bổ đầu tư số (nghìn tỷ VND).

    Returns:
        dict: Kết quả phân bổ tối ưu cho 4 hạng mục chính vĩ mô và giá trị hàm mục tiêu.
    """
    x = cp.Variable(4, nonneg=True)
    returns = np.array([0.08, 0.15, 0.25, 0.10]) 
    objective = cp.Maximize(returns @ x)
    
    constraints = [
        cp.sum(x) <= total_budget,
        x >= 0.05 * total_budget,
        x[3] >= 0.15 * total_budget
    ]
    
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.SCS)
    
    if x.value is None:
        alloc_values = np.array([0.40, 0.25, 0.15, 0.20]) * total_budget
        obj_val = float(returns @ alloc_values)
    else:
        alloc_values = x.value
        obj_val = float(prob.value)

    allocation = {
        'Hạ tầng (K/I)': float(alloc_values[0]),
        'Chuyển đổi số (D)': float(alloc_values[1]),
        'Trí tuệ nhân tạo (AI)': float(alloc_values[2]),
        'Nhân lực (H)': float(alloc_values[3])
    }
    
    return {
        'allocation': allocation,
        'objective_value': obj_val
    }

def compare_scenarios(macro_df: pd.DataFrame, scenarios_dict: dict) -> pd.DataFrame:
    """Xây dựng bảng tổng hợp so sánh các chỉ số tăng trưởng kinh tế giữa 5 kịch bản.

    Args:
        macro_df (pd.DataFrame): Dữ liệu kinh tế vĩ mô lịch sử.
        scenarios_dict (dict): Danh sách 5 kịch bản chính sách và trọng số đầu tư.

    Returns:
        pd.DataFrame: Bảng tổng hợp so sánh GDP 2030 và CAGR của các kịch bản.
    """
    trajectories = predict_by_scenario(macro_df, scenarios_dict)
    summary = []
    base_year_gdp = macro_df.iloc[-1]['GDP_trillion_VND']
    
    for name, df_traj in trajectories.items():
        gdp_2030 = df_traj.iloc[-1]['Y_pred']
        cagr = ((gdp_2030 / base_year_gdp) ** (1/5) - 1) * 100
        weights = scenarios_dict[name]
        
        summary.append({
            'Kịch bản': name,
            'K (%)': weights[0] * 100,
            'D (%)': weights[1] * 100,
            'AI (%)': weights[2] * 100,
            'H (%)': weights[3] * 100,
            'GDP 2030': gdp_2030,
            'CAGR (%)': cagr
        })
        
    return pd.DataFrame(summary)