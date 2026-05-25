import numpy as np
import pandas as pd

class DigitalReadinessEvaluator:
    def __init__(self, sectors_df: pd.DataFrame = None):
        """Khởi tạo đánh giá mức độ sẵn sàng công nghệ của các ngành."""
        if sectors_df is None:
            self.sectors_df = pd.DataFrame({
                'sector': ['Nông nghiệp', 'Công nghiệp', 'Dịch vụ', 'Công nghệ'],
                'ai_readiness_0_100': [20, 50, 70, 90],
                'digital_maturity': [30, 60, 80, 95],
                'labor_million': [15, 12, 20, 2],
                'automation_risk_pct': [0.1, 0.4, 0.3, 0.05]
            })
        else:
            self.sectors_df = sectors_df

    def evaluate_readiness(self, scenario: str = 'S1') -> dict:
        """Sử dụng TOPSIS để đánh giá và trả về điểm tổng hợp hệ thống."""
        # Trọng số TOPSIS thay đổi theo kịch bản (Kịch bản AI sẽ ưu tiên điểm AI cao)
        scenario_weights = {
            'S1': [0.4, 0.3, 0.15, 0.15],
            'S3': [0.6, 0.2, 0.1, 0.1]  # Ưu tiên AI Readiness
        }
        weights = scenario_weights.get(scenario, [0.4, 0.3, 0.15, 0.15])
            
        data = self.sectors_df[['ai_readiness_0_100', 'digital_maturity', 'labor_million', 'automation_risk_pct']].copy()
        norm_data = data / (np.sqrt((data**2).sum()) + 1e-12)
        weighted_data = norm_data * weights
        
        ideal_best = [weighted_data.iloc[:,0].max(), weighted_data.iloc[:,1].max(), weighted_data.iloc[:,2].min(), weighted_data.iloc[:,3].min()]
        ideal_worst = [weighted_data.iloc[:,0].min(), weighted_data.iloc[:,1].min(), weighted_data.iloc[:,2].max(), weighted_data.iloc[:,3].max()]
        
        dist_best = np.sqrt(((weighted_data - ideal_best)**2).sum(axis=1))
        dist_worst = np.sqrt(((weighted_data - ideal_worst)**2).sum(axis=1))
        
        topsis_score = dist_worst / (dist_best + dist_worst + 1e-12)
        avg_score = float(topsis_score.mean() * 100) # Quy ra thang 100 cho app.py
        
        return {
            'Scenario': scenario,
            'Readiness_Score': round(avg_score, 1),
            'Details': topsis_score.tolist()
        }