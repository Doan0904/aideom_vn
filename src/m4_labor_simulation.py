import pandas as pd

class LaborSimulator:
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

    def simulate_labor_shift(self, target_year: int = 2030, scenario: str = 'S1') -> dict:
        """Mô phỏng sự dịch chuyển dòng lao động vĩ mô."""
        scenario_weights = {
            'S1': [0.40, 0.25, 0.15, 0.20],
            'S2': [0.20, 0.40, 0.25, 0.15],
            'S3': [0.15, 0.25, 0.40, 0.20],
            'S4': [0.25, 0.25, 0.20, 0.30],
            'S5': [0.25, 0.25, 0.25, 0.25]
        }
        weights = scenario_weights.get(scenario, scenario_weights['S1'])
        years = target_year - 2025 # Tính số năm dự báo
        
        w_D, w_AI, w_H = weights[1], weights[2], weights[3]
        df = self.sectors_df.copy()
        
        c1 = 0.5 * w_AI + 0.3 * w_D  
        d1 = 0.8 * w_H               
        new_job_factor = 0.1 * (w_AI + w_D + w_H) 
        
        # Chạy logic như code gốc
        df['displaced'] = df['labor_million'] * df['automation_risk_pct'] * c1 * years
        df['retrained'] = df['displaced'] * d1
        df['new_jobs'] = df['labor_million'] * new_job_factor * (df['digital_maturity']/100 + df['ai_readiness_0_100']/100)
        
        total_labor = df['labor_million'].sum()
        total_displaced = df['displaced'].sum()
        total_new = df['new_jobs'].sum()
        total_net_job = total_new + df['retrained'].sum() - total_displaced
        
        unemployment_rate = max(0, abs(min(0, total_net_job)) / total_labor * 100)
        
        return {
            'Scenario': scenario,
            'Unemployment_Rate_Pct': round(unemployment_rate + 3.0, 2), # Cấp số cơ sở 3%
            'Jobs_Displaced': int(total_displaced * 1_000_000),
            'New_Tech_Jobs': int(total_new * 1_000_000)
        }