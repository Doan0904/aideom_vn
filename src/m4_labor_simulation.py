import numpy as np
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
        """Mô phỏng sự dịch chuyển dòng lao động bằng Chuỗi Markov Động (Dynamic Markov Chain)."""
        years = target_year - 2025
        
        # S_0: Trạng thái ban đầu (Số lượng lao động từng ngành)
        initial_state = self.sectors_df['labor_million'].values
        N = len(initial_state) # Tự động nhận diện số lượng ngành (4, 10, hay N ngành)
        
        # Khởi tạo ma trận chuyển trạng thái P kích thước N x N
        P = np.zeros((N, N))
        
        # Trích xuất các biến độc lập
        auto_risk = self.sectors_df['automation_risk_pct'].values
        ai_read = self.sectors_df['ai_readiness_0_100'].values
        dig_mat = self.sectors_df['digital_maturity'].values
        
        # Tính "sức hút" (attractiveness) của từng ngành đối với dòng lao động dịch chuyển
        attractiveness = ai_read + dig_mat
        if scenario in ['S2', 'S3']:
            # Kịch bản công nghệ: Ngành nào điểm AI càng cao càng hút lao động mạnh
            attractiveness = attractiveness * (1.0 + ai_read / 100.0)
        elif scenario == 'S4':
            # Bao trùm số: Ưu tiên kéo lao động về các ngành có độ trưởng thành số thấp (để lấp đầy)
            attractiveness = attractiveness * (1.0 + (100.0 - dig_mat) / 100.0)
            
        # Xây dựng ma trận Markov
        for i in range(N):
            # 1. Tỷ lệ giữ việc: Tỷ lệ nghịch với rủi ro tự động hóa
            stay_prob = 1.0 - auto_risk[i]
            
            # Hiệu chỉnh rủi ro theo kịch bản truyền thống
            if scenario == 'S1':
                stay_prob *= 0.95 
                
            # Đảm bảo không ngành nào mất quá 70% lao động trong 1 năm
            stay_prob = np.clip(stay_prob, 0.3, 0.95)
            P[i, i] = stay_prob
            
            # 2. Lao động dôi dư (rem_prob) sẽ dịch chuyển sang các ngành khác
            rem_prob = 1.0 - stay_prob
            
            # Lọc sức hút của các ngành KHÁC (không tự hút chính mình)
            attr_others = attractiveness.copy()
            attr_others[i] = 0.0 
            
            # Tính phân phối xác suất chuyển dịch
            if np.sum(attr_others) > 0:
                probs_others = (attr_others / np.sum(attr_others)) * rem_prob
            else:
                # Phân phối đều nếu lỗi
                probs_others = np.ones(N) / (N - 1) * rem_prob
                probs_others[i] = 0.0
                
            P[i, :] += probs_others
            
        # Nhân ma trận trạng thái qua t năm: S_t = S_0 * P^t
        current_state = initial_state.copy()
        for _ in range(years):
            current_state = np.dot(current_state, P)
            
        # TÍNH TOÁN CÁC CHỈ SỐ VĨ MÔ
        job_diff = current_state - initial_state
        
        # 1. Tổng việc làm bị thay thế (Chỉ lấy tổng của các ngành bị ÂM lao động)
        total_displaced = np.sum(np.abs(job_diff[job_diff < 0]))
        
        # 2. Việc làm công nghệ mới: Định nghĩa là các việc sinh ra tại nhóm 25% ngành có AI Readiness cao nhất
        tech_threshold = np.percentile(ai_read, 75)
        tech_indices = np.where(ai_read >= tech_threshold)[0]
        new_tech_jobs = np.sum(np.maximum(0, job_diff[tech_indices]))
        
        # 3. Tỷ lệ thất nghiệp: Base (3%) + Hệ số tác động của lao động dôi dư
        unemployment_rate = 3.0 + (total_displaced / initial_state.sum()) * 100 * 0.25
        
        return {
            'Scenario': scenario,
            'Unemployment_Rate_Pct': round(float(unemployment_rate), 2),
            'Jobs_Displaced': int(total_displaced * 1_000_000),
            'New_Tech_Jobs': int(new_tech_jobs * 1_000_000)
        }