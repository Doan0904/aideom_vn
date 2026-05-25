"""
Script tự động chạy so sánh 3 kịch bản bắt buộc (S1, S3, S5) cho năm 2030
và xuất kết quả ra file CSV để chèn vào báo cáo Word/PDF.
"""
import pandas as pd
import os
import sys

# Thêm thư mục src vào path để import được các module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from m1_economic_forecast import EconomicForecaster
from m2_digital_readiness import DigitalReadinessEvaluator
from m4_labor_simulation import LaborSimulator

def main():
    m1 = EconomicForecaster()
    m2 = DigitalReadinessEvaluator()
    m4 = LaborSimulator()
    
    scenarios = ['S1', 'S3', 'S5']
    results = []
    
    print("Đang chạy mô phỏng tổng hợp năm 2030...")
    
    for s in scenarios:
        gdp_2030 = m1.forecast_gdp(start_year=2030, end_year=2030, scenario=s)['GDP_Billion_USD'].iloc[0]
        readiness = m2.evaluate_readiness(target_year=2030, scenario=s)['Readiness_Score']
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
    print(df_results.to_markdown(index=False))
    print(f"\n Đã xuất file thành công tại: {out_path}")

if __name__ == "__main__":
    main()