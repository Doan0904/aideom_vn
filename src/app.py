import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_macro, load_sectors, load_regions
from optimization import predict_by_scenario, allocate_budget, compare_scenarios
from modules import topsis_digital_readiness, simulate_labor_displacement, assess_risk

st.set_page_config(page_title="AIDEOM-VN Dashboard", layout="wide")

SCENARIOS = {
    "S1. Truyền thống":    [0.70, 0.10, 0.10, 0.10],
    "S2. Số hóa nhanh":    [0.25, 0.45, 0.15, 0.15],
    "S3. AI dẫn dắt":      [0.20, 0.20, 0.45, 0.15],
    "S4. Bao trùm số":     [0.30, 0.20, 0.10, 0.40],
    "S5. Tối ưu cân bằng": [0.40, 0.25, 0.15, 0.20]
}

# LOAD DATA
macro_df   = load_macro()
sectors_df = load_sectors()
regions_df = load_regions()

# SIDEBAR
st.sidebar.title("🛠️ Cấu hình Kịch bản")
selected_scenario = st.sidebar.selectbox("Chọn kịch bản phân bổ:", list(SCENARIOS.keys()))
total_budget = st.sidebar.slider("Ngân sách (Nghìn tỷ VND):", min_value=10000, max_value=150000, value=80000, step=5000)
show_opt = st.sidebar.checkbox("Hiện kịch bản tối ưu LP trên biểu đồ", value=True)

st.title("📊 AIDEOM-VN: Mô Hình Ra Quyết Định Kinh Tế 2026-2030")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Tổng quan (M1)", "💰 Phân bổ (M3)", "⚖️ Kịch bản so sánh", "⚠️ Cảnh báo (M5)"])

# TÍNH TOÁN DỮ LIỆU DÙNG CHUNG
traj_dict = predict_by_scenario(macro_df, SCENARIOS)
current_traj = traj_dict[selected_scenario]
base_gdp = macro_df.iloc[-1]['GDP_trillion_VND']
target_gdp = current_traj.iloc[-1]['Y_pred']
cagr_val = ((target_gdp / base_gdp) ** (1/5) - 1) * 100

with tab1:
    st.subheader("Dự báo tăng trưởng GDP (Cobb-Douglas)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GDP 2025 (Nghìn tỷ)", f"{base_gdp:,.0f}")
    c2.metric(f"GDP 2030 ({selected_scenario})", f"{target_gdp:,.0f}")
    c3.metric("CAGR 2026-2030", f"{cagr_val:.2f}%")
    c4.metric("TFP Trung bình", f"{macro_df['TFP'].mean():.4f}")
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        hist_df = macro_df[['year', 'GDP_trillion_VND']].rename(columns={'GDP_trillion_VND': 'GDP'})
        hist_df['Type'] = 'Historical'
        pred_df = current_traj[['year', 'Y_pred']].rename(columns={'Y_pred': 'GDP'})
        pred_df['Type'] = 'Forecast'
        combined_df = pd.concat([hist_df, pred_df])
        fig1 = px.line(combined_df, x='year', y='GDP', color='Type', markers=True, title="Lịch sử và Dự báo GDP")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        fig_area = px.area(current_traj, x='year', y=['K', 'D', 'AI', 'H'], title="Đóng góp các yếu tố vào Tăng trưởng")
        st.plotly_chart(fig_area, use_container_width=True)

with tab2:
    st.subheader(f"Cơ cấu Ngân sách: {selected_scenario}")
    weights = SCENARIOS[selected_scenario]
    alloc_df = pd.DataFrame({
        "Hạng mục": ['Hạ tầng (K/I)', 'Chuyển đổi số (D)', 'AI (AI)', 'Nhân lực (H)'],
        "Ngân sách": [total_budget * w for w in weights]
    })
    
    c_alloc1, c_alloc2 = st.columns(2)
    with c_alloc1:
        fig_pie = px.pie(alloc_df, values='Ngân sách', names='Hạng mục', hole=0.4, title="Tỷ trọng phân bổ hiện tại")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c_alloc2:
        lp_result = allocate_budget(total_budget)
        lp_alloc = pd.DataFrame(list(lp_result['allocation'].items()), columns=["Hạng mục", "Ngân sách (LP)"])
        comp_df = alloc_df.merge(lp_alloc, on="Hạng mục")
        fig_bar = px.bar(comp_df, x="Hạng mục", y=["Ngân sách", "Ngân sách (LP)"], barmode="group",
                         title="So sánh kịch bản chọn vs Kịch bản tối ưu LP (CVXPY)")
        st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.subheader("So sánh toàn diện 5 Kịch bản")
    comp_summary = compare_scenarios(macro_df, SCENARIOS)
    
    # Bổ sung cột NetJob estimate (giả lập từ M4)
    comp_summary['NetJob (triệu)'] = comp_summary.apply(
        lambda r: simulate_labor_displacement(sectors_df, r[['K (%)', 'D (%)', 'AI (%)', 'H (%)']].values/100)['net_job'].sum(),
        axis=1
    )
    
    st.dataframe(comp_summary.style.highlight_max(subset=['GDP 2030', 'CAGR (%)', 'NetJob (triệu)']))
    
    c_comp1, c_comp2 = st.columns(2)
    with c_comp1:
        fig_comp_bar = px.bar(comp_summary, x='Kịch bản', y='GDP 2030', color='Kịch bản', title="GDP 2030 theo Kịch bản")
        st.plotly_chart(fig_comp_bar, use_container_width=True)
        
    with c_comp2:
        categories = ['K', 'D', 'AI', 'H']
        fig_radar = go.Figure()
        for idx, row in comp_summary.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row['K (%)'], row['D (%)'], row['AI (%)'], row['H (%)']],
                theta=categories, fill='toself', name=row['Kịch bản']
            ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Radar Phân bổ")
        st.plotly_chart(fig_radar, use_container_width=True)

with tab4:
    st.subheader("Cảnh báo rủi ro Hệ thống (M5)")
    risk_df, total_risk = assess_risk(sectors_df, weights)
    
    c_risk1, c_risk2 = st.columns(2)
    with c_risk1:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = total_risk,
            title = {'text': "Tổng Chỉ Số Rủi Ro (0-100)"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgreen"},
                    {'range': [40, 70], 'color': "gold"},
                    {'range': [70, 100], 'color': "salmon"}
                ]}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with c_risk2:
        # Heatmap rủi ro các ngành
        heat_data = risk_df[['sector_name_vi', 'automation_risk', 'cyber_risk', 'dependency_risk']].set_index('sector_name_vi')
        fig_heat = px.imshow(heat_data.T, text_auto=".2f", aspect="auto", title="Heatmap Rủi ro theo Ngành")
        st.plotly_chart(fig_heat, use_container_width=True)
        
    st.dataframe(risk_df[['sector_name_vi', 'labor_million', 'total_risk_score', 'warning']])