import numpy as np
import pulp

def predict_cobb_douglas(macro_df, target_year=2030, growth_assumptions=None):
    """
    Dự báo GDP dựa trên hàm sản xuất Cobb-Douglas mở rộng (Bài 1)
    """
    alpha, beta, gamma, delta, theta = 0.33, 0.42, 0.10, 0.08, 0.07
    
    # Lấy dữ liệu năm cuối (2025) làm gốc
    base = macro_df.iloc[-1]
    
    if growth_assumptions is None:
        growth_assumptions = {
            'K_growth': 1.06, 'L_growth': 1.06, 
            'D_target': 30, 'AI_target': 100, 'H_target': 35
        }
        
    years_diff = target_year - 2025
    K_future = base['K_capital_trillion'] * (growth_assumptions['K_growth'] ** years_diff)
    L_future = base['L_labor_million'] * (growth_assumptions['L_growth'] ** years_diff)
    D_future = growth_assumptions['D_target']
    AI_future = growth_assumptions['AI_target']
    H_future = growth_assumptions['H_target']
    
    # Giả định TFP không đổi so với trung bình
    A_mean = 0.052 # Ước lượng TFP
    
    Y_future = (A_mean * (1.012**years_diff)) * (K_future**alpha) * (L_future**beta) * (D_future**gamma) * (AI_future**delta) * (H_future**theta)
    return Y_future

def allocate_budget(total_budget, scenario_weights):
    """
    Hàm tính toán phân bổ ngân sách dựa trên Kịch bản (Bài 12)
    scenario_weights = [w_K, w_D, w_AI, w_H]
    """
    allocation = {
        'Hạ tầng (K/I)': total_budget * scenario_weights[0],
        'Chuyển đổi số (D)': total_budget * scenario_weights[1],
        'Trí tuệ nhân tạo (AI)': total_budget * scenario_weights[2],
        'Nhân lực (H)': total_budget * scenario_weights[3]
    }
    return allocation