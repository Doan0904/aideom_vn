import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import 5 module độc lập
from m1_economic_forecast import EconomicForecaster
from m2_digital_readiness import DigitalReadinessEvaluator
from m3_allocation_optimization import ResourceOptimizer
from m4_labor_simulation import LaborSimulator
from m5_risk_assessment import RiskAssessor

# BỔ SUNG: Import hàm load dữ liệu từ data_loader
from data_loader import load_macro, load_sectors

st.set_page_config(page_title="AIDEOM-VN Dashboard", page_icon="📈", layout="wide")

# Custom CSS để làm cho các thẻ metric trông giống card (hộp) hơn
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #f0f2f6;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.title("Hệ thống Hỗ trợ Ra quyết định AIDEOM-VN 🚀")
st.markdown("Dashboard mô phỏng các kịch bản chính sách phát triển kinh tế vĩ mô tích hợp AI.")

# ==========================================
# CẬP NHẬT MỚI: TẢI DỮ LIỆU VÀ KHỞI TẠO MODULE
# ==========================================
# Tải dữ liệu thật (Nếu thiếu file CSV, data_loader sẽ tự động tạo)
macro_df = load_macro()
sectors_df = load_sectors()

# Khởi tạo các module và truyền dữ liệu vào
m1 = EconomicForecaster(macro_df=macro_df)
m2 = DigitalReadinessEvaluator(sectors_df=sectors_df)
m3 = ResourceOptimizer() # M3 tự tối ưu dựa trên ngân sách nhập từ UI
m4 = LaborSimulator(sectors_df=sectors_df)
m5 = RiskAssessor(sectors_df=sectors_df)
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Cài đặt Kịch bản")
    scenario_dict = {
        "S1 - Truyền thống": "S1",
        "S2 - Số hóa nhanh": "S2",
        "S3 - AI dẫn dắt": "S3",
        "S4 - Bao trùm số": "S4",
        "S5 - Tối ưu cân bằng": "S5"
    }
    selected_option = st.selectbox("Chọn kịch bản mô phỏng:", list(scenario_dict.keys()))
    scenario_code = scenario_dict[selected_option]
    
    st.markdown("---")
    st.markdown("**Thông tin thông số:**")
    st.info(f"Kịch bản hiện tại: **{scenario_code}**\nMô hình sẽ cập nhật các chỉ số dựa trên mức độ đầu tư vào công nghệ lõi và mức độ tự động hóa.")

# --- MAIN TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Tổng quan Kinh tế", "💰 Phân bổ Ngân sách", "📈 So sánh Kịch bản", "⚠️ Cảnh báo Rủi ro"])

with tab1:
    st.subheader(f"Chỉ số Vĩ mô - Kịch bản {scenario_code}")
    
    # Chạy M1 & M2
    df_gdp = m1.forecast_gdp(target_year=2030, scenario=scenario_code)
    readiness = m2.evaluate_readiness(scenario=scenario_code)
    
    # Layout thẻ (Cards)
    col1, col2, col3 = st.columns(3)
    col1.metric("GDP Dự kiến 2030", f"{df_gdp['GDP_Billion_USD'].iloc[-1]:.1f} Tỷ USD", f"+{df_gdp['Growth_Rate'].iloc[-1]:.2f}%")
    col2.metric("Điểm sẵn sàng số", f"{readiness['Readiness_Score']}/100", "Điểm đánh giá hạ tầng")
    col3.metric("Tăng trưởng Trung bình", f"{df_gdp['Growth_Rate'].mean():.2f}%", "Giai đoạn 2025-2030")
    
    st.markdown("---")
    
    # Vẽ biểu đồ Plotly Line chuyên nghiệp
    fig_gdp = px.line(
        df_gdp, x='Year', y='GDP_Billion_USD', 
        markers=True, 
        title="Dự báo quỹ đạo tăng trưởng GDP (2025 - 2030)",
        labels={'GDP_Billion_USD': 'GDP (Tỷ USD)', 'Year': 'Năm'},
        color_discrete_sequence=['#1f77b4']
    )
    fig_gdp.update_layout(hovermode="x unified", title_x=0.4)
    st.plotly_chart(fig_gdp, use_container_width=True)

with tab2:
    st.subheader("Tối ưu Phân bổ Nguồn lực")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        total_budget = st.number_input("Nhập tổng ngân sách đầu tư (Tỷ USD):", value=1000.0, step=100.0)
        df_alloc = m3.optimize_allocation(total_budget=total_budget, scenario=scenario_code)
        st.dataframe(df_alloc.style.format({'Allocated_Budget': '{:.1f}', 'Percentage': '{:.1f}%'}), hide_index=True)
    
    with col2:
        # Vẽ biểu đồ Plotly Donut (Bánh khuyết)
        fig_alloc = px.pie(
            df_alloc, values='Allocated_Budget', names='Sector', 
            hole=0.4, title=f"Cơ cấu Ngân sách ({total_budget} Tỷ USD)",
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_alloc.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_alloc, use_container_width=True)

with tab3:
    st.subheader("Bàn làm việc So sánh Đa kịch bản")
    st.markdown("Đối chiếu trực quan kết quả giữa các hướng tiếp cận chính sách tại mốc **2030**.")
    
    comp_data = []
    for s in ['S1', 'S3', 'S5']:
        gdp = m1.forecast_gdp(target_year=2030, scenario=s)['GDP_Billion_USD'].iloc[-1]
        unemp = m4.simulate_labor_shift(target_year=2030, scenario=s)['Unemployment_Rate_Pct']
        comp_data.append({"Kịch bản": s, "GDP 2030 (Tỷ USD)": gdp, "Thất nghiệp (%)": unemp})
    
    df_comp = pd.DataFrame(comp_data)
    
    col1, col2 = st.columns(2)
    with col1:
        # Biểu đồ cột so sánh GDP
        fig_comp_gdp = px.bar(
            df_comp, x='Kịch bản', y='GDP 2030 (Tỷ USD)',
            text_auto='.1f', title='So sánh GDP năm 2030',
            color='Kịch bản', color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_comp_gdp, use_container_width=True)
        
    with col2:
        # Biểu đồ cột so sánh Thất nghiệp
        fig_comp_unemp = px.bar(
            df_comp, x='Kịch bản', y='Thất nghiệp (%)',
            text_auto='.1f', title='So sánh Tỷ lệ Thất nghiệp',
            color='Kịch bản', color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_comp_unemp, use_container_width=True)

with tab4:
    st.subheader("Cảnh báo Hệ thống & Rủi ro")
    
    labor = m4.simulate_labor_shift(target_year=2030, scenario=scenario_code)
    risks = m5.assess_risks(scenario=scenario_code)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.error(f"🚨 **Dự báo Thất nghiệp:** {labor['Unemployment_Rate_Pct']}%")
        st.warning(f"🔄 **Việc làm bị thay thế do AI:** {labor['Jobs_Displaced']:,} người")
        st.success(f"🌱 **Việc làm công nghệ mới:** {labor['New_Tech_Jobs']:,} người")
        
        st.markdown("##### Ma trận Rủi ro Chi tiết")
        st.write(f"- Rủi ro Nợ công: **{risks['Debt_Risk']}**")
        st.write(f"- Rủi ro Khí hậu: **{risks['Climate_Risk']}**")
        st.write(f"- Rủi ro Xã hội: **{risks['Social_Risk']}**")

    with col2:
        # Vẽ Radar Chart để biểu diễn mức độ rủi ro (Chuyển text thành số)
        risk_map = {'Thấp': 1, 'Trung bình': 2, 'Cao': 3, 'N/A': 0}
        risk_values = [risk_map.get(risks['Debt_Risk'], 0), risk_map.get(risks['Climate_Risk'], 0), risk_map.get(risks['Social_Risk'], 0)]
        categories = ['Nợ công', 'Biến đổi Khí hậu', 'An sinh Xã hội']
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=risk_values + [risk_values[0]], # Khép kín mảng
            theta=categories + [categories[0]],
            fill='toself',
            line_color='rgba(255, 99, 71, 0.8)',
            fillcolor='rgba(255, 99, 71, 0.4)'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 3], tickvals=[1, 2, 3], ticktext=['Thấp', 'Trung bình', 'Cao'])),
            showlegend=False,
            title="Sơ đồ Phân bố Rủi ro"
        )
        st.plotly_chart(fig_radar, use_container_width=True)