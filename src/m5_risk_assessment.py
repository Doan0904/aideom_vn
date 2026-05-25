"""
Module M5: Đánh giá và Cảnh báo rủi ro đa chiều
Đầu vào: Kết quả từ M1, M3, M4.
Đầu ra: Cảnh báo nợ công, biến đổi khí hậu, an sinh xã hội.
"""

class RiskAssessor:
    def __init__(self):
        pass

    def assess_risks(self, scenario: str = 'S1') -> dict:
        """
        Đánh giá mức độ rủi ro (Thấp, Trung bình, Cao).
        """
        risks = {
            'S1': {'Debt_Risk': 'Thấp', 'Climate_Risk': 'Cao', 'Social_Risk': 'Trung bình'},
            'S3': {'Debt_Risk': 'Cao', 'Climate_Risk': 'Trung bình', 'Social_Risk': 'Cao'},
            'S5': {'Debt_Risk': 'Trung bình', 'Climate_Risk': 'Thấp', 'Social_Risk': 'Thấp'}
        }
        return risks.get(scenario, {'Debt_Risk': 'N/A', 'Climate_Risk': 'N/A', 'Social_Risk': 'N/A'})