import numpy as np
import pandas as pd

class RiskAssessor:
    def __init__(self, sectors_df: pd.DataFrame = None):
        pass 

    def assess_risks(self, scenario: str = 'S1', n_simulations: int = 1000) -> dict:
        """Đánh giá rủi ro hệ thống bằng mô phỏng Monte Carlo (Stochastic)."""
        # Trọng số đúng theo Mục 12.2 của đề bài
        scenario_weights = {
            'S1': [0.70, 0.10, 0.10, 0.10], # Truyền thống
            'S2': [0.25, 0.45, 0.15, 0.15], # Số hóa nhanh
            'S3': [0.20, 0.20, 0.45, 0.15], # AI dẫn dắt
            'S4': [0.30, 0.20, 0.10, 0.40], # Bao trùm
            'S5': [0.25, 0.25, 0.25, 0.25]  # Cân bằng
        }
        w = scenario_weights.get(scenario, scenario_weights['S1'])
        
        # Xác định các giá trị cơ sở (Base Values)
        debt_base = w[0] * 100
        climate_base = 20 + (w[0] * 50) - (w[1] * 10) - (w[2] * 20)
        social_base = (w[1] * 30) + (w[2] * 60) - (w[3] * 40)
        
        # Chạy Monte Carlo Simulation giả lập sự nhiễu loạn của ngoại cảnh
        np.random.seed(42) # Cố định seed để dễ test, thực tế có thể bỏ
        
        # Phân phối chuẩn np.random.normal(loc=mean, scale=std_dev, size)
        debt_sim = np.random.normal(loc=debt_base, scale=15.0, size=n_simulations)
        climate_sim = np.random.normal(loc=climate_base, scale=10.0, size=n_simulations)
        social_sim = np.random.normal(loc=social_base, scale=12.0, size=n_simulations)
        
        # Sử dụng Value at Risk (VaR 95%) làm chỉ số quyết định cảnh báo rủi ro
        debt_p95 = np.percentile(debt_sim, 95)
        climate_p95 = np.percentile(climate_sim, 95)
        social_p95 = np.percentile(social_sim, 95)

        def classify(score):
            if score >= 40: return 'Cao'
            if score >= 20: return 'Trung bình'
            return 'Thấp'

        return {
            'Debt_Risk': classify(debt_p95),
            'Climate_Risk': classify(climate_p95),
            'Social_Risk': classify(social_p95),
            'Raw_95th_Percentile': {
                'Debt': round(debt_p95, 2),
                'Climate': round(climate_p95, 2),
                'Social': round(social_p95, 2)
            }
        }