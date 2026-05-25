import numpy as np
import pandas as pd

def topsis_digital_readiness(sectors_df: pd.DataFrame, weights: list = None) -> pd.DataFrame:
    """Xếp hạng mức độ sẵn sàng công nghệ số của các ngành kinh tế theo thuật toán TOPSIS.

    Args:
        sectors_df (pd.DataFrame): Dữ liệu các ngành nghề kinh tế.
        weights (list): Trọng số ưu tiên chính sách cho các tiêu chí đánh giá.

    Returns:
        pd.DataFrame: Bảng xếp hạng kèm điểm TOPSIS score và khuyến nghị chiến lược.
    """
    if weights is None:
        weights = [0.4, 0.3, 0.15, 0.15]
        
    data = sectors_df[['ai_readiness_0_100', 'digital_maturity', 'labor_million', 'automation_risk_pct']].copy()
    norm_data = data / (np.sqrt((data**2).sum()) + 1e-12)
    weighted_data = norm_data * weights
    
    ideal_best = [
        weighted_data['ai_readiness_0_100'].max(),
        weighted_data['digital_maturity'].max(),
        weighted_data['labor_million'].min(),
        weighted_data['automation_risk_pct'].min()
    ]
    ideal_worst = [
        weighted_data['ai_readiness_0_100'].min(),
        weighted_data['digital_maturity'].min(),
        weighted_data['labor_million'].max(),
        weighted_data['automation_risk_pct'].max()
    ]
    
    dist_best = np.sqrt(((weighted_data - ideal_best)**2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_data - ideal_worst)**2).sum(axis=1))
    
    sectors_df = sectors_df.copy()
    sectors_df['topsis_score'] = dist_worst / (dist_best + dist_worst + 1e-12)
    sectors_df['rank'] = sectors_df['topsis_score'].rank(ascending=False, method='min')
    sectors_df['recommendation'] = np.where(sectors_df['topsis_score'] > 0.6, 'Ưu tiên Đầu tư', 
                                   np.where(sectors_df['topsis_score'] > 0.4, 'Theo dõi thêm', 'Hạn chế Đầu tư'))
    
    return sectors_df.sort_values('topsis_score', ascending=False)

def simulate_labor_displacement(sectors_df: pd.DataFrame, budget_weights: list, years: int = 5) -> pd.DataFrame:
    """Mô phỏng sự dịch chuyển dòng lao động vĩ mô dưới tác động của AI và chuyển đổi số.

    Args:
        sectors_df (pd.DataFrame): Dữ liệu gốc các ngành kinh tế xã hội.
        budget_weights (list): Mảng trọng số phân bổ đầu tư [K, D, AI, H].
        years (int): Số năm chạy mô phỏng dự báo.

    Returns:
        pd.DataFrame: Kết quả dự báo số việc làm mới, việc làm mất đi và NetJob ròng.
    """
    w_D, w_AI, w_H = budget_weights[1], budget_weights[2], budget_weights[3]
    df = sectors_df.copy()
    
    c1 = 0.5 * w_AI + 0.3 * w_D  
    d1 = 0.8 * w_H               
    new_job_factor = 0.1 * (w_AI + w_D + w_H) 
    
    df['displaced'] = df['labor_million'] * df['automation_risk_pct'] * c1 * years
    df['retrained'] = df['displaced'] * d1
    df['new_jobs'] = df['labor_million'] * new_job_factor * (df['digital_maturity'] + df['ai_readiness_0_100']/100)
    
    df['net_job'] = df['new_jobs'] + df['retrained'] - df['displaced']
    df['net_job_pct'] = (df['net_job'] / (df['labor_million'] + 1e-12)) * 100
    
    return df

def assess_risk(sectors_df: pd.DataFrame, scenario_weights: list) -> tuple:
    """Tính toán chỉ số rủi ro tích hợp hệ thống (ESG & Cyber Risk) dựa trên cấu trúc kịch bản.

    Args:
        sectors_df (pd.DataFrame): Bảng dữ liệu ngành nghề kinh tế.
        scenario_weights (list): Trọng số cấu trúc đầu tư của kịch bản đang chọn.

    Returns:
        tuple: DataFrame chi tiết mức rủi ro của từng ngành và điểm tổng hợp vĩ mô hệ thống.
    """
    df = sectors_df.copy()
    
    df['automation_risk'] = df['automation_risk_pct'] * (scenario_weights[2] * 2 + scenario_weights[1])
    df['cyber_risk'] = df['digital_maturity'] * (scenario_weights[1] + scenario_weights[2])
    df['dependency_risk'] = (1 - df['gdp_contribution_pct']) * scenario_weights[0]
    
    df['total_risk_score'] = (df['automation_risk'] * 0.4 + df['cyber_risk'] * 0.4 + df['dependency_risk'] * 0.2) * 100
    
    def get_warning(score):
        if score > 60: return "🔴 Cao"
        if score > 30: return "🟡 Trung bình"
        return "🟢 Thấp"
        
    df['warning'] = df['total_risk_score'].apply(get_warning)
    total_risk_index = float(df['total_risk_score'].mean())
    
    return df, total_risk_index