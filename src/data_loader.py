import os
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

def generate_synthetic_data():
    """
    Tạo dữ liệu giả lập sát với thực tế kinh tế Việt Nam nếu chưa tồn tại file CSV.
    Dữ liệu được lưu trực tiếp vào thư mục data/.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Macro data
    macro_data = {
        'year': [2020, 2021, 2022, 2023, 2024, 2025],
        'GDP_trillion_VND': [8000, 8400, 9500, 10200, 11000, 11800],
        'K_capital_trillion': [20000, 21500, 23500, 25000, 26500, 27500],
        'L_labor_million': [50.5, 50.6, 51.2, 51.8, 52.3, 52.8],
        'D_digital_index': [12.0, 14.5, 17.0, 18.5, 20.0, 21.5],
        'AI_index': [45.0, 50.0, 55.0, 65.0, 75.0, 85.0],
        'H_human_capital': [25.0, 26.5, 27.8, 29.0, 30.5, 32.0],
        'TFP': [0.045, 0.046, 0.048, 0.050, 0.051, 0.052]
    }
    pd.DataFrame(macro_data).to_csv(DATA_DIR / 'vietnam_macro_2020_2025.csv', index=False)

    # 2. Sectors data
    sectors_data = {
        'sector_name_vi': [
            'Nông nghiệp', 'Công nghiệp chế biến', 'Khai khoáng', 'Xây dựng', 
            'Bán buôn bán lẻ', 'Vận tải kho bãi', 'Tài chính ngân hàng', 
            'CNTT & Truyền thông', 'Giáo dục', 'Y tế'
        ],
        'labor_million': [13.5, 11.2, 0.5, 4.8, 6.5, 1.8, 0.4, 0.8, 1.5, 0.6],
        'automation_risk_pct': [0.65, 0.75, 0.80, 0.60, 0.50, 0.55, 0.35, 0.20, 0.25, 0.30],
        'ai_readiness_0_100': [20, 45, 30, 35, 60, 50, 85, 95, 70, 75],
        'digital_maturity': [0.3, 0.5, 0.4, 0.45, 0.7, 0.6, 0.9, 0.95, 0.75, 0.8],
        'gdp_contribution_pct': [0.12, 0.25, 0.05, 0.06, 0.10, 0.05, 0.08, 0.09, 0.04, 0.03]
    }
    pd.DataFrame(sectors_data).to_csv(DATA_DIR / 'vietnam_sectors_2024.csv', index=False)

    # 3. Regions data
    regions_data = {
        'region_name': ['ĐBSH', 'TDMNPB', 'BTB & Duyên hải MT', 'Tây Nguyên', 'Đông Nam Bộ', 'ĐBSCL'],
        'gdp_per_capita_usd': [4500, 2800, 3200, 3100, 7500, 3500],
        'digital_index': [8.5, 4.0, 5.5, 4.5, 9.2, 5.0],
        'ai_readiness': [75, 30, 45, 35, 85, 40],
        'population_million': [23.5, 13.0, 20.5, 6.0, 18.5, 17.5],
        'fdi_billion_usd': [15.2, 2.1, 5.4, 0.8, 20.5, 3.2]
    }
    pd.DataFrame(regions_data).to_csv(DATA_DIR / 'vietnam_regions_2024.csv', index=False)

def validate_dataframe(df: pd.DataFrame, required_cols: list) -> None:
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"DataFrame thiếu các cột bắt buộc sau: {missing}")

def load_macro() -> pd.DataFrame:
    """Load dữ liệu vĩ mô, tạo mới nếu thiếu file hoặc file cũ không hợp lệ."""
    file_path = DATA_DIR / 'vietnam_macro_2020_2025.csv'
    
    # Kiểm tra tồn tại và tính hợp lệ, nếu lỗi thì tạo lại
    if file_path.exists():
        df = pd.read_csv(file_path)
        try:
            validate_dataframe(df, ['year', 'GDP_trillion_VND', 'K_capital_trillion', 'L_labor_million'])
        except ValueError:
            generate_synthetic_data()
    else:
        generate_synthetic_data()
        
    df = pd.read_csv(file_path).sort_values('year').reset_index(drop=True)
    return df

def load_sectors() -> pd.DataFrame:
    """Load dữ liệu ngành, tạo mới nếu thiếu file hoặc file cũ không hợp lệ."""
    file_path = DATA_DIR / 'vietnam_sectors_2024.csv'
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        try:
            validate_dataframe(df, ['sector_name_vi', 'labor_million', 'automation_risk_pct', 'ai_readiness_0_100'])
        except ValueError:
            generate_synthetic_data()
    else:
        generate_synthetic_data()
        
    df = pd.read_csv(file_path)
    return df

def load_regions() -> pd.DataFrame:
    """Load dữ liệu vùng, tạo mới nếu thiếu file hoặc file cũ không hợp lệ."""
    file_path = DATA_DIR / 'vietnam_regions_2024.csv'
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        try:
            validate_dataframe(df, ['region_name', 'gdp_per_capita_usd', 'digital_index'])
        except ValueError:
            generate_synthetic_data()
    else:
        generate_synthetic_data()
        
    df = pd.read_csv(file_path)
    return df