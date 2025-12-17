import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.title("🌙 서울 지하철 밤샘 분석기")

uploaded_file = st.file_uploader("지하철 CSV 업로드", type="csv")

if uploaded_file is not None:
    st.success("✅ 분석 중...")
    
    try:
        df = pd.read_csv(uploaded_file, encoding='cp949', low_memory=False)
        st.subheader("📊 데이터")
        st.dataframe(df.head(2))
        
        # 호선 컬럼
        line_col = next((col for col in df.columns if '호선' in str(col)), None)
        
        # 시간대 컬럼 (00시-01시 형식)
        time_cols = [col for col in df.columns if re.search(r'\d{2}시-\d{2}시', str(col))]
        
        st.info(f"시간대 컬럼: {len(time_cols)}개")
        
        if len(time_cols) > 0 and line_col:
            # 사이드바 호선 선택
            st.sidebar.header("호선 선택")
            lines = sorted(df[line_col].dropna().unique())[:15]
            selected_line = st.sidebar.selectbox("선택", lines)
            
            # 선택된 호선 데이터
            line_df = df[df[line_col] == selected_line]
            
            # 시간대별 평균 계산
            hourly_data = []
            for time_col in time_cols:
                hour_match = re.search(r'(\d{2})시', time_col)
                if hour_match:
                    hour = int(hour_match.group(1))
                    avg = line_df[time_col].mean()
                    hourly_data.append({'시간': hour, '승차': avg})
            
            hourly_df = pd.DataFrame(hourly_data)
            
            # === 라인 차트 ===
            st.subheader(f"📈 {selected_line} 24시간 패턴")
            fig_line = px.line(hourly_df, x='시간', y='승차', 
                              title="시간대별 승차", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
            
            #
