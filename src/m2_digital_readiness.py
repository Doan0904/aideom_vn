import numpy as np
import pandas as pd

class DigitalReadinessEvaluator:
    def __init__(self, sectors_df: pd.DataFrame = None):
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

    def calculate_entropy_weights(self, data: np.ndarray, benefit_criteria: list) -> np.ndarray:
        """Tính toán trọng số khách quan bằng phương pháp Entropy (Entropy Weight Method)."""
        # 1. Chuẩn hóa Min-Max
        norm_data = np.zeros_like(data, dtype=float)
        for i in range(data.shape[1]):
            c_max = np.max(data[:, i])
            c_min = np.min(data[:, i])
            if c_max == c_min:
                norm_data[:, i] = 1.0
            elif i in benefit_criteria:
                norm_data[:, i] = (data[:, i] - c_min) / (c_max - c_min) + 1e-6
            else: # Tiêu chí chi phí (Cost - Càng nhỏ càng tốt)
                norm_data[:, i] = (c_max - data[:, i]) / (c_max - c_min) + 1e-6
                
        # 2. Tính tỷ trọng p_ij
        p = norm_data / norm_data.sum(axis=0)
        
        # 3. Tính giá trị Entropy e_j
        n = norm_data.shape[0]
        k = 1.0 / np.log(n)
        e = -k * np.sum(p * np.log(p), axis=0)
        
        # 4. Tính trọng số w_j
        d = 1 - e
        w = d / np.sum(d)
        return w

    def evaluate_readiness(self, scenario: str = 'S1') -> dict:
        """Sử dụng TOPSIS kết hợp Entropy Weight Method."""
        data = self.sectors_df[['ai_readiness_0_100', 'digital_maturity', 'labor_million', 'automation_risk_pct']].values
        
        # Tính trọng số Entropy khách quan (Cột 0, 1 là Benefit; Cột 2, 3 là Cost)
        entropy_weights = self.calculate_entropy_weights(data, benefit_criteria=[0, 1])
        
        # Trọng số chủ quan theo Kịch bản (Điều chỉnh dựa trên Mục 12.2)
        scenario_pref = {
            'S1': np.array([0.1, 0.1, 0.4, 0.4]), # Ưu tiên lao động truyền thống
            'S2': np.array([0.2, 0.5, 0.15, 0.15]), # Ưu tiên Digital Maturity
            'S3': np.array([0.6, 0.2, 0.1, 0.1]), # Ưu tiên AI Readiness
            'S4': np.array([0.2, 0.3, 0.3, 0.2]), # Bao trùm
            'S5': np.array([0.25, 0.25, 0.25, 0.25])
        }
        subj_weights = scenario_pref.get(scenario, scenario_pref['S1'])
        
        # Kết hợp trọng số (Kết hợp tuyến tính 50-50 giữa Khách quan và Chủ quan)
        final_weights = 0.5 * entropy_weights + 0.5 * subj_weights
        final_weights = final_weights / np.sum(final_weights) # Chuẩn hóa lại
            
        norm_data = data / (np.sqrt((data**2).sum(axis=0)) + 1e-12)
        weighted_data = norm_data * final_weights
        
        ideal_best = [weighted_data[:,0].max(), weighted_data[:,1].max(), weighted_data[:,2].min(), weighted_data[:,3].min()]
        ideal_worst = [weighted_data[:,0].min(), weighted_data[:,1].min(), weighted_data[:,2].max(), weighted_data[:,3].max()]
        
        dist_best = np.sqrt(((weighted_data - ideal_best)**2).sum(axis=1))
        dist_worst = np.sqrt(((weighted_data - ideal_worst)**2).sum(axis=1))
        
        topsis_score = dist_worst / (dist_best + dist_worst + 1e-12)
        avg_score = float(topsis_score.mean() * 100) 
        
        return {
            'Scenario': scenario,
            'Readiness_Score': round(avg_score, 1),
            'Details': topsis_score.tolist()
        }