"""
Module M3: Tối ưu phân bổ nguồn lực (Linear/Integer Programming)
Đầu vào: Ngân sách, mục tiêu KPI.
Đầu ra: Phương án phân bổ vốn và nhân lực tối ưu.
"""
import pandas as pd

class ResourceOptimizer:
    def __init__(self):
        pass

    def optimize_allocation(self, total_budget: float, scenario: str = 'S1') -> pd.DataFrame:
        """
        Tối ưu phân bổ ngân sách cho các ngành/vùng (Dùng Scipy, PuLP hoặc Pyomo).
        """
        # Logic giả lập
        sectors = ['Nông nghiệp', 'Công nghiệp', 'Dịch vụ', 'Công nghệ lõi']
        if scenario in ['S2', 'S3']:
            allocations = [0.1, 0.3, 0.2, 0.4] # Ưu tiên công nghệ
        elif scenario == 'S4':
            allocations = [0.25, 0.25, 0.3, 0.2] # Bao trùm
        else:
            allocations = [0.2, 0.4, 0.3, 0.1] # Truyền thống
            
        allocated_funds = [total_budget * a for a in allocations]
        
        return pd.DataFrame({
            'Sector': sectors,
            'Allocated_Budget': allocated_funds,
            'Percentage': [a * 100 for a in allocations]
        })