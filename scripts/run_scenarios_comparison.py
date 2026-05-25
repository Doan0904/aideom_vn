"""
Script tự động chạy so sánh 3 kịch bản bắt buộc (S1, S3, S5) cho năm 2030
và xuất kết quả ra file CSV để chèn vào báo cáo Word/PDF.
"""
import pandas as pd
import os
import sys

# Thêm thư mục src vào path để import được các module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.m1_economic_forecast import EconomicForecaster
from src.m2_digital_readiness import DigitalReadinessEvaluator
from src.m4_labor_simulation import LaborSimulator
# BỔ SUNG: Import hàm load dữ liệu
from src.data_loader import load_macro, load_sectors

def main():
    # 1. Tải dữ liệu thật (dùng đường dẫn tương đối từ vị trí file script)
    # Vì script nằm trong thư mục scripts/, dữ liệu nằm trong data/ ở thư mục gốc
    macro_df = load_macro()
    sectors_df = load_sectors()

    # 2. Khởi tạo các module với dữ liệu thật
    m1 = EconomicForecaster(macro_df=macro_df)
    m2 = DigitalReadinessEvaluator(sectors_df=sectors_df)
    m4 = LaborSimulator(sectors_df=sectors_df)
    
    scenarios = ['S1', 'S3', 'S5']
    results = []
    
    print("Đang chạy mô phỏng tổng hợp năm 2030 dựa trên dữ liệu thật...")
    
    for s in scenarios:
        # Gọi hàm với tham số đúng cấu trúc mới
        gdp_2030 = m1.forecast_gdp(target_year=2030, scenario=s)['GDP_Billion_USD'].iloc[-1]
        readiness = m2.evaluate_readiness(scenario=s)['Readiness_Score']
        labor = m4.simulate_labor_shift(target_year=2030, scenario=s)['Unemployment_Rate_Pct']
        
        results.append({
            "Kịch bản": s,
            "GDP 2030 (Tỷ USD)": round(gdp_2030, 2),
            "Điểm sẵn sàng số": readiness,
            "Tỷ lệ thất nghiệp (%)": labor
        })
        
    df_results = pd.DataFrame(results)
    
    # Tạo thư mục outputs nếu chưa có
    os.makedirs('outputs', exist_ok=True)
    out_path = 'outputs/kpi_comparison_2030.csv'
    
    df_results.to_csv(out_path, index=False, encoding='utf-8-sig')
    
    print("\n=== BẢNG TỔNG HỢP KPI 2030 ===")
    # Nếu lệnh to_markdown báo lỗi, hãy đảm bảo đã cài tabulate (pip install tabulate)
    print(df_results.to_markdown(index=False))
    print(f"\n Đã xuất file thành công tại: {out_path}")

if __name__ == "__main__":
    main()