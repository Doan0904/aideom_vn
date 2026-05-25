import pandas as pd

class RiskAssessor:
    def __init__(self, sectors_df: pd.DataFrame = None):
        """Module đánh giá rủi ro vĩ mô dựa trên phân bổ nguồn lực."""
        pass 

    def assess_risks(self, scenario: str = 'S1') -> dict:
        """Tính toán ma trận rủi ro hệ thống dựa trên đánh đổi chính sách."""
        # Trọng số đầu tư: [Hạ tầng (K), Số hóa (D), AI, Nhân lực (H)]
        scenario_weights = {
            'S1': [0.40, 0.25, 0.15, 0.20], # Truyền thống
            'S2': [0.20, 0.40, 0.25, 0.15], # Số hóa nhanh
            'S3': [0.15, 0.25, 0.40, 0.20], # AI dẫn dắt
            'S4': [0.25, 0.25, 0.20, 0.30], # Bao trùm
            'S5': [0.25, 0.25, 0.25, 0.25]  # Cân bằng
        }
        weights = scenario_weights.get(scenario, scenario_weights['S1'])
        
        # 1. Rủi ro nợ công: Phụ thuộc tỷ lệ thuận vào đầu tư Hạ tầng vật lý quy mô lớn
        debt_risk_val = weights[0] * 100
        
        # 2. Rủi ro khí hậu: Hạ tầng làm tăng phát thải, Số hóa & AI giúp tối ưu năng lượng
        climate_risk_val = 20 + (weights[0] * 50) - (weights[1] * 10) - (weights[2] * 20)
        
        # 3. Rủi ro xã hội: Thất nghiệp do công nghệ và phân hóa kỹ năng
        social_risk_val = (weights[1] * 30) + (weights[2] * 60)

        # Hàm phân loại dựa trên phổ điểm đã được tinh chỉnh
        def classify(score):
            if score >= 30: return 'Cao'
            if score >= 20: return 'Trung bình'
            return 'Thấp'

        return {
            'Social_Risk': classify(social_risk_val),
            'Climate_Risk': classify(climate_risk_val),
            'Debt_Risk': classify(debt_risk_val)
        }