import matplotlib.pyplot as plt
import seaborn as sns
from src.data_loader import load_macro, load_sectors
from src.optimization import predict_by_scenario
from src.modules import topsis_digital_readiness, simulate_labor_displacement, assess_risk
import pandas as pd

def run_demo():
    print("Khởi động hệ thống đánh giá tự động AIDEOM-VN...\n")
    
    # 1. Load Data
    macro_df = load_macro()
    sectors_df = load_sectors()
    
    SCENARIOS = {
        "S1": [0.70, 0.10, 0.10, 0.10],
        "S3": [0.20, 0.20, 0.45, 0.15],
        "S5": [0.40, 0.25, 0.15, 0.20]
    }
    
    # 2. Predict Trajectory
    trajectories = predict_by_scenario(macro_df, SCENARIOS)
    
    # 3. Tổng hợp số liệu Terminal
    summary_data = []
    base_gdp = macro_df.iloc[-1]['GDP_trillion_VND']
    
    for name, w in SCENARIOS.items():
        gdp_2030 = trajectories[name].iloc[-1]['Y_pred']
        cagr = ((gdp_2030 / base_gdp) ** (1/5) - 1) * 100
        netjob = simulate_labor_displacement(sectors_df, w)['net_job'].sum()
        _, risk_idx = assess_risk(sectors_df, w)
        
        recommendation = "Khuyên dùng" if name == "S5" else "Cần theo dõi"
        summary_data.append([name, f"{gdp_2030:,.0f}", f"{cagr:.1f}%", f"{netjob:,.2f}", f"{risk_idx:.1f}", recommendation])
    
    summary_df = pd.DataFrame(summary_data, columns=["Kịch bản", "GDP 2030", "CAGR", "NetJob", "Risk Index", "Khuyến nghị"])
    
    print("=== AIDEOM-VN SUMMARY 2030 ===")
    print(summary_df.to_string(index=False))
    print("==============================\n")
    
    # 4. Vẽ Đồ thị Subplots 2x3
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Dashboard Tổng Hợp Phân Tích AIDEOM-VN", fontsize=16, fontweight='bold')
    
    # [0, 0] GDP Forecast
    for name in SCENARIOS:
        axs[0, 0].plot(trajectories[name]['year'], trajectories[name]['Y_pred'], marker='o', label=name)
    axs[0, 0].set_title("1. GDP Forecast (M1)")
    axs[0, 0].legend()
    
    # [0, 1] Phân bổ ngân sách (Pie cho S5)
    axs[0, 1].pie(SCENARIOS['S5'], labels=['K', 'D', 'AI', 'H'], autopct='%1.1f%%', startangle=90)
    axs[0, 1].set_title("2. Cơ cấu phân bổ S5 (M3)")
    
    # [0, 2] TOPSIS Readiness
    topsis_res = topsis_digital_readiness(sectors_df).head(5)
    sns.barplot(data=topsis_res, x='topsis_score', y='sector_name_vi', ax=axs[0, 2], palette='viridis')
    axs[0, 2].set_title("3. Top 5 Ngành TOPSIS (M2)")
    
    # [1, 0] NetJob Simulation (S5)
    net_jobs = simulate_labor_displacement(sectors_df, SCENARIOS['S5'])
    sns.barplot(data=net_jobs, x='net_job', y='sector_name_vi', ax=axs[1, 0], palette='coolwarm')
    axs[1, 0].set_title("4. NetJob thay đổi (M4)")
    
    # [1, 1] Risk Heatmap
    risk_df, _ = assess_risk(sectors_df, SCENARIOS['S5'])
    sns.heatmap(risk_df[['automation_risk', 'cyber_risk', 'dependency_risk']].set_index(risk_df['sector_name_vi']), 
                cmap="YlOrRd", annot=True, fmt=".1f", ax=axs[1, 1])
    axs[1, 1].set_title("5. Heatmap Rủi ro (M5)")
    
    # [1, 2] So sánh 3 kịch bản chính
    comp_plot_data = pd.DataFrame({
        'Kịch bản': ['S1', 'S3', 'S5'],
        'GDP': [trajectories['S1'].iloc[-1]['Y_pred'], trajectories['S3'].iloc[-1]['Y_pred'], trajectories['S5'].iloc[-1]['Y_pred']]
    })
    sns.barplot(data=comp_plot_data, x='Kịch bản', y='GDP', ax=axs[1, 2], palette='pastel')
    axs[1, 2].set_title("6. GDP 2030 (So Sánh)")
    
    plt.tight_layout()
    print("-> Đang mở cửa sổ biểu đồ matplotlib...")
    plt.show()

if __name__ == "__main__":
    run_demo()