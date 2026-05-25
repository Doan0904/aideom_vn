import pandas as pd

class EconomicForecaster:
    def __init__(self, macro_df: pd.DataFrame = None):
        """Khởi tạo với dữ liệu vĩ mô. Nếu không có sẽ tự tạo mock data 2020-2024."""
        if macro_df is None:
            self.macro_df = pd.DataFrame({
                'year': [2020, 2021, 2022, 2023, 2024],
                'K_capital_trillion': [1000, 1100, 1200, 1300, 1400],
                'L_labor_million': [54, 54.5, 55, 55.5, 56],
                'D_digital_index': [10, 12, 15, 20, 25],
                'AI_index': [2, 3, 5, 8, 12],
                'H_human_capital': [50, 52, 54, 56, 58],
                'GDP_trillion_VND': [300, 320, 350, 380, 400] # Quy đổi Tỷ USD trong app.py
            })
        else:
            self.macro_df = macro_df

    def forecast_gdp(self, target_year: int = 2030, scenario: str = 'S1') -> pd.DataFrame:
        """Dự báo GDP bằng hàm Cobb-Douglas."""
        # Trọng số phân bổ [K, D, AI, H] cho 5 kịch bản
        # CODE ĐÚNG CẦN THAY THẾ
        scenario_weights = {
            'S1': [0.70, 0.10, 0.10, 0.10], # S1: 70% K, 10% mỗi loại D/AI/H
            'S2': [0.25, 0.45, 0.15, 0.15], # S2: Số hóa nhanh (45% D)
            'S3': [0.20, 0.20, 0.45, 0.15], # S3: AI dẫn dắt (45% AI)
            'S4': [0.30, 0.20, 0.10, 0.40], # S4: Bao trùm số (40% H)
            'S5': [0.25, 0.25, 0.25, 0.25]  # Tối ưu cân bằng (Có thể giữ nguyên hoặc lấy từ M3)
        }
        weights = scenario_weights.get(scenario, scenario_weights['S1'])
        
        # Thiết lập giả định tăng trưởng dựa trên trọng số đầu tư
        assumptions = {
            'K_growth': 1.0 + (weights[0] * 0.1),
            'D_growth': 1.0 + (weights[1] * 0.5),
            'AI_growth': 1.0 + (weights[2] * 0.8),
            'H_growth': 1.0 + (weights[3] * 0.2),
            'L_growth': 1.01,
            'A_mean': 0.052, 'A_growth': 1.012
        }

        alpha, beta, gamma, delta, theta = 0.33, 0.42, 0.10, 0.08, 0.07
        base = self.macro_df.iloc[-1]
        last_year = int(base['year'])
        
        trajectory = []
        current_state = {
            'year': last_year,
            'K': base['K_capital_trillion'], 'L': base['L_labor_million'],
            'D': base['D_digital_index'], 'AI': base['AI_index'], 'H': base['H_human_capital'],
            'A': assumptions['A_mean']
        }
        
        prev_Y = base['GDP_trillion_VND']
        calibration_factor = 1.0
        
        for y in range(last_year + 1, target_year + 1):
            current_state['year'] = y
            current_state['K'] *= assumptions['K_growth']
            current_state['L'] *= assumptions['L_growth']
            current_state['D'] *= assumptions['D_growth']
            current_state['AI'] *= assumptions['AI_growth']
            current_state['H'] *= assumptions['H_growth']
            current_state['A'] *= assumptions['A_growth']
            
            Y_pred = (current_state['A']) * \
                     (current_state['K']**alpha) * (current_state['L']**beta) * \
                     (current_state['D']**gamma) * (current_state['AI']**delta) * \
                     (current_state['H']**theta)
            
            if y == last_year + 1:
                calibration_factor = prev_Y / Y_pred if Y_pred > 0 else 1.0
            
            Y_pred_calibrated = Y_pred * calibration_factor
            growth_rate = (Y_pred_calibrated / prev_Y - 1) * 100
            
            trajectory.append({
                'Year': y,
                'Scenario': scenario,
                'GDP_Billion_USD': Y_pred_calibrated, # Map với biến ở app.py
                'Growth_Rate': growth_rate
            })
            prev_Y = Y_pred_calibrated
            
        return pd.DataFrame(trajectory)