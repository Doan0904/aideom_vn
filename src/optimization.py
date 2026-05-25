import numpy as np
import pandas as pd
import cvxpy as cp

def predict_cobb_douglas(macro_df: pd.DataFrame, target_year: int = 2030, growth_assumptions: dict = None) -> pd.DataFrame:
    """
    Dự báo quỹ đạo GDP từ năm sau năm cuối cùng của macro_df đến target_year bằng mô hình Cobb-Douglas.
    
    Args:
        macro_df: DataFrame chứa lịch sử vĩ mô.
        target_year: Năm đích cần dự báo đến.
        growth_assumptions: Dictionary chứa tốc độ tăng trưởng dự kiến của K, L, D, AI, H.
        
    Returns:
        pd.DataFrame: Quỹ đạo từng năm từ 2026-2030 kèm tỷ lệ tăng trưởng.
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
        
        # Scale về đơn vị nghìn tỷ VND (tuỳ vào calibration của A_mean, giả định A_mean đã được calibrate)
        # Sử dụng hệ số nhân để nối tiếp mượt mà với năm gốc
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
    """
    Dự báo quỹ đạo GDP cho nhiều kịch bản (S1-S5) dựa trên trọng số phân bổ.
    
    Args:
        macro_df: DataFrame vĩ mô cơ sở.
        scenarios_dict: Dictionary {Tên kịch bản: [Tỷ lệ K, Tỷ lệ D, Tỷ lệ AI, Tỷ lệ H]}.
        
    Returns:
        dict: Mapping giữa Tên kịch bản và DataFrame trajectory.
    """
    results = {}
    for name, weights in scenarios_dict.items():
        # Nội suy growth assumptions từ weights phân bổ.
        # Đầu tư càng cao thì growth càng lớn.
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
    """
    Sử dụng CVXPY để phân bổ ngân sách tối ưu hóa kỳ vọng GDP (LP).
    
    Args:
        total_budget: Tổng ngân sách.
        
    Returns:
        dict: Chứa phân bổ tối ưu ('allocation') và giá trị mục tiêu ('objective_value').
    """
    # Xây dựng biến quyết định cho: K, D, AI, H
    x = cp.Variable(4, nonneg=True)
    
    # Hàm mục tiêu: Tối đa hóa proxy của GDP. 
    # Giả định hệ số lợi tức biên (đã tuyến tính hóa từ Cobb-Douglas quanh điểm cân bằng)
    returns = np.array([0.08, 0.15, 0.25, 0.10]) 
    objective = cp.Maximize(returns @ x)
    
    # Ràng buộc
    constraints = [
        cp.sum(x) <= total_budget,          # Tổng không vượt quá ngân sách
        x >= 0.05 * total_budget,           # Mỗi hạng mục tối thiểu 5% ngân sách
        x[3] >= 0.15 * total_budget         # Nhân lực (H) tối thiểu 15%
    ]
    
    prob = cp.Problem(objective, constraints)
    prob.solve()
    
    if x.value is None:
        raise ValueError("Không tìm được nghiệm tối ưu LP.")
        
    alloc_values = x.value
    allocation = {
        'Hạ tầng (K/I)': alloc_values[0],
        'Chuyển đổi số (D)': alloc_values[1],
        'Trí tuệ nhân tạo (AI)': alloc_values[2],
        'Nhân lực (H)': alloc_values[3]
    }
    
    return {
        'allocation': allocation,
        'objective_value': prob.value
    }

def compare_scenarios(macro_df: pd.DataFrame, scenarios_dict: dict) -> pd.DataFrame:
    """
    So sánh các kịch bản về GDP, CAGR và các trọng số.
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
            'K (%)': weights[0]*100,
            'D (%)': weights[1]*100,
            'AI (%)': weights[2]*100,
            'H (%)': weights[3]*100,
            'GDP 2030': gdp_2030,
            'CAGR (%)': cagr
        })
        
    return pd.DataFrame(summary)