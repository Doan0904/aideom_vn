import numpy as np
import pandas as pd

def topsis_digital_readiness(sectors_df: pd.DataFrame, weights: list = None) -> pd.DataFrame:
    """
    Tính điểm TOPSIS cho 10 ngành dựa trên 4 tiêu chí chuẩn hóa.
    
    Args:
        sectors_df: DataFrame ngành nghề.
        weights: List 4 trọng số. Mặc định là [0.4, 0.3, 0.15, 0.15].
        
    Returns:
        DataFrame kèm cột điểm số và xếp hạng.
    """
    if weights is None:
        weights = [0.4, 0.3, 0.15, 0.15]
        
    # Các tiêu chí: 2 thuận, 2 nghịch
    data = sectors_df[['ai_readiness_0_100', 'digital_maturity', 'labor_million', 'automation_risk_pct']].copy()
    
    # 1. Chuẩn hóa vector
    norm_data = data / np.sqrt((data**2).sum())
    
    # 2. Nhân trọng số
    weighted_data = norm_data * weights
    
    # 3. Xác định giải pháp lý tưởng
    ideal_best = [
        weighted_data['ai_readiness_0_100'].max(),
        weighted_data['digital_maturity'].max(),
        weighted_data['labor_million'].min(),       # Ít bị ảnh hưởng quy mô lao động
        weighted_data['automation_risk_pct'].min()  # Rủi ro tự động hóa thấp
    ]
    ideal_worst = [
        weighted_data['ai_readiness_0_100'].min(),
        weighted_data['digital_maturity'].min(),
        weighted_data['labor_million'].max(),
        weighted_data['automation_risk_pct'].max()
    ]
    
    # 4. Khoảng cách Euclid
    dist_best = np.sqrt(((weighted_data - ideal_best)**2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_data - ideal_worst)**2).sum(axis=1))
    
    # 5. Điểm số TOPSIS
    sectors_df = sectors_df.copy()
    sectors_df['topsis_score'] = dist_worst / (dist_best + dist_worst)
    sectors_df['rank'] = sectors_df['topsis_score'].rank(ascending=False, method='min')
    
    # Phân loại khuyến nghị
    sectors_df['recommendation'] = np.where(sectors_df['topsis_score'] > 0.6, 'Ưu tiên Đầu tư', 
                                   np.where(sectors_df['topsis_score'] > 0.4, 'Theo dõi thêm', 'Hạn chế Đầu tư'))
    
    return sectors_df.sort_values('topsis_score', ascending=False)


def simulate_labor_displacement(sectors_df: pd.DataFrame, budget_weights: list, years: int = 5) -> pd.DataFrame:
    """
    Mô phỏng NetJob ròng dựa trên phân bổ K, D, AI, H.
    
    Args:
        sectors_df: DataFrame ngành nghề.
        budget_weights: Phân bổ [K, D, AI, H].
        years: Khung thời gian mô phỏng.
    """
    w_D, w_AI, w_H = budget_weights[1], budget_weights[2], budget_weights[3]
    df = sectors_df.copy()
    
    # Tham số tác động
    c1 = 0.5 * w_AI + 0.3 * w_D   # Động lực sa thải
    d1 = 0.8 * w_H                # Động lực đào tạo lại
    new_job_factor = 0.1 * (w_AI + w_D + w_H) 
    
    df['displaced'] = df['labor_million'] * df['automation_risk_pct'] * c1 * years
    df['retrained'] = df['displaced'] * d1
    df['new_jobs'] = df['labor_million'] * new_job_factor * (df['digital_maturity'] + df['ai_readiness_0_100']/100)
    
    df['net_job'] = df['new_jobs'] + df['retrained'] - df['displaced']
    df['net_job_pct'] = (df['net_job'] / df['labor_million']) * 100
    
    return df


def assess_risk(sectors_df: pd.DataFrame, scenario_weights: list) -> tuple:
    """
    Đánh giá mức độ rủi ro hệ thống.
    
    Returns:
        Tuple (DataFrame chi tiết rủi ro, Total Risk Score 0-100).
    """
    df = sectors_df.copy()
    
    # 1. Rủi ro tự động hoá
    df['automation_risk'] = df['automation_risk_pct'] * (scenario_weights[2] * 2 + scenario_weights[1])
    
    # 2. Rủi ro không gian mạng (cyber risk)
    df['cyber_risk'] = df['digital_maturity'] * (scenario_weights[1] + scenario_weights[2])
    
    # 3. Phụ thuộc bên ngoài (dependency) - Giả định nghịch đảo với GDP contribution
    df['dependency_risk'] = (1 - df['gdp_contribution_pct']) * scenario_weights[0]
    
    # Tính điểm tổng hợp (scale 0-10)
    df['total_risk_score'] = (df['automation_risk'] * 0.4 + df['cyber_risk'] * 0.4 + df['dependency_risk'] * 0.2) * 100
    
    # Phân loại màu cảnh báo
    def get_warning(score):
        if score > 60: return "🔴 Cao"
        if score > 30: return "🟡 Trung bình"
        return "🟢 Thấp"
        
    df['warning'] = df['total_risk_score'].apply(get_warning)
    
    total_risk_index = df['total_risk_score'].mean()
    
    return df, total_risk_index