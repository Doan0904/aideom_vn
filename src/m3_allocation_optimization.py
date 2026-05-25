import numpy as np
import pandas as pd
import cvxpy as cp

class ResourceOptimizer:
    def __init__(self):
        pass

    def optimize_allocation(self, total_budget: float, scenario: str = 'S1') -> pd.DataFrame:
        """Tối ưu hóa phân bổ ngân sách bằng CVXPY."""
        # Với các kịch bản khác nhau, ta sẽ thiết lập điều kiện ràng buộc khác nhau
        x = cp.Variable(4, nonneg=True)
        returns = np.array([0.08, 0.15, 0.25, 0.10]) # [Hạ tầng, Số hóa, AI, Nhân lực]
        objective = cp.Maximize(returns @ x)
        
        constraints = [cp.sum(x) <= total_budget, x >= 0.05 * total_budget]
        
        # Logic tùy chỉnh theo Kịch bản
        if scenario == 'S3': # AI dẫn dắt
            constraints.append(x[2] >= 0.45 * total_budget)
        elif scenario == 'S4': # Bao trùm
            constraints.append(x[3] >= 0.40 * total_budget)
        else: # Mặc định S1
            constraints.append(x[3] >= 0.10 * total_budget)
            
        prob = cp.Problem(objective, constraints)
        prob.solve(solver=cp.SCS)
        
        if x.value is None:
            alloc_values = np.array([0.40, 0.25, 0.15, 0.20]) * total_budget
        else:
            alloc_values = x.value

        sectors = ['Hạ tầng Cơ bản', 'Chuyển đổi số', 'Trí tuệ nhân tạo (AI)', 'Đào tạo Nhân lực']
        return pd.DataFrame({
            'Sector': sectors,
            'Allocated_Budget': alloc_values,
            'Percentage': (alloc_values / total_budget) * 100
        })