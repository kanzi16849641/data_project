import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.title("🌙 서울 지하철 밤샘 분석기 - 호선별 히트맵")

uploaded_file = st.file_uploader("지하철 CSV 업로드", type="csv")

if uploaded_file is not None:
    st.success("✅ 자동 분석 시작...")
    
    try:
        df = pd.read_csv(uploaded_file, encoding='cp949', low_memory=False)
        
        st.subheader("📊 데이터 구조")
        st.dataframe(df.head(2))
        
        # 호선 컬럼 찾기
        line_col = next((col for col in df.columns if '호선' in str(col)), None)
        if not line_col:
            line_col = '호선명'  # 기본값
            
        # 시간대 컬럼들 찾기 (00시-01시, 04시-05시 등)
        time_cols = [col for col in df.columns if re.search(r'\d{2}시-\d{2}시', str(col))]
        st.info(f"발견된 시간대 컬럼: {len(time_cols)}개")
        
        if len(time_cols) > 0 and line_col in df.columns:
            # 호선 선택 (사이드바)
            st.sidebar.header("🔧 호선 선택")
            lines = sorted(df[line_col].dropna().unique())[:20]
            selected_line = st.sidebar.selectbox("호선", lines)
            
            # 선택된 호선 데이터
            line_df = df[df[line_col] == selected_line]
            
            # 시간대별 데이터 재구성
            time_data = []
            for time_col in time_cols:
                hour_start = int(re.search(r'(\d{2})시', time_col).group(1))
                avg_passengers = line_df[time_col].mean()
                time_data.append({'시간대': hour_start, '승차인원': avg_passengers})
            
            hourly_df = pd.DataFrame(time_data)
            
            # === 1. 호선별 24시간 라인차트 ===
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"📈 {selected_line} 24시간 패턴")
                fig_line = px.line(hourly_df, x='시간대', y='승차인원', 
                                  title=f"{selected_line} 승차 트렌드", markers=True)
                st.plotly_chart(fig_line, use
