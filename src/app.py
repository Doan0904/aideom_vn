import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_macro, load_sectors, load_regions
from optimization import predict_cobb_douglas, allocate_budget

# Cấu hình trang
st.set_page_config(page_title="AIDEOM-VN Dashboard", layout="wide")

# Bộ trọng số theo 5 kịch bản (Bảng 12.2)
SCENARIOS = {
    "S1. Truyền thống": [0.70, 0.10, 0.10, 0.10],
    "S2. Số hóa nhanh": [0.25, 0.45, 0.15, 0.15],
    "S3. AI dẫn dắt": [0.20, 0.20, 0.45, 0.15],
    "S4. Bao trùm số": [0.30, 0.20, 0.10, 0.40],
    "S5. Tối ưu cân bằng": [0.40, 0.25, 0.15, 0.20]
}

st.sidebar.title("🛠️ Cấu hình Kịch bản")
selected_scenario = st.sidebar.selectbox("Chọn kịch bản chính sách:", list(SCENARIOS.keys()))
total_budget = st.sidebar.number_input("Ngân sách chuyển đổi số (Nghìn tỷ VND):", min_value=10000, max_value=150000, value=80000)

# Tải dữ liệu
macro_df = load_macro()
sectors_df = load_sectors()
regions_df = load_regions()

st.title("📊 AIDEOM-VN: Mô Hình Ra Quyết Định Kinh Tế 2026-2030")

# 4 Tab chức năng
tab1, tab2, tab3, tab4 = st.tabs(["📈 Tổng quan (M1)", "💰 Phân bổ (M3)", "⚖️ Kịch bản so sánh", "⚠️ Cảnh báo (M5)"])

with tab1:
    st.subheader("Dự báo tăng trưởng GDP (Cobb-Douglas)")
    pred_gdp = predict_cobb_douglas(macro_df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("GDP Dự báo 2030 (Nghìn tỷ)", f"{pred_gdp:,.1f} VND")
    with col2:
        fig = px.line(macro_df, x='year', y='GDP_trillion_VND', title="Lịch sử GDP 2020-2025", markers=True)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader(f"Phân bổ ngân sách theo: {selected_scenario}")
    weights = SCENARIOS[selected_scenario]
    alloc = allocate_budget(total_budget, weights)
    
    alloc_df = pd.DataFrame(list(alloc.items()), columns=["Hạng mục", "Ngân sách (Nghìn tỷ)"])
    fig2 = px.pie(alloc_df, values='Ngân sách (Nghìn tỷ)', names='Hạng mục', title="Cơ cấu phân bổ", hole=0.4)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.dataframe(alloc_df)
    with col_b:
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Đánh giá ngành theo TOPSIS (Giả lập)")
    fig3 = px.bar(sectors_df, x='sector_name_vi', y='ai_readiness_0_100', 
                  title="Mức độ sẵn sàng AI của 10 Ngành (2024)", color='automation_risk_pct')
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("Rủi ro thị trường lao động (M4 & M5)")
    st.warning("Cảnh báo: Ngành Khai khoáng và Chế biến chế tạo có rủi ro tự động hóa cao (trên 40%)!")
    st.dataframe(sectors_df[['sector_name_vi', 'labor_million', 'automation_risk_pct']].sort_values('automation_risk_pct', ascending=False))