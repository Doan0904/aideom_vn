import pandas as pd
from pathlib import Path

# Xác định đường dẫn thư mục data (nằm ngang hàng với thư mục src)
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

def load_macro():
    """Tải dữ liệu kinh tế vĩ mô 2020-2025"""
    df = pd.read_csv(DATA_DIR / 'vietnam_macro_2020_2025.csv')
    df = df.sort_values('year').reset_index(drop=True)
    return df

def load_sectors():
    """Tải dữ liệu 10 ngành kinh tế 2024"""
    return pd.read_csv(DATA_DIR / 'vietnam_sectors_2024.csv')

def load_regions():
    """Tải dữ liệu 6 vùng kinh tế 2024"""
    return pd.read_csv(DATA_DIR / 'vietnam_regions_2024.csv')

if __name__ == '__main__':
    macro = load_macro()
    print('Macro shape:', macro.shape)
    print(macro.head())