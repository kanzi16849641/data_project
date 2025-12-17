import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🌙 서울 지하철 밤샘 분석기")

# 파일 업로드 (버튼 없이 즉시 처리)
uploaded_file = st.file_uploader("지하철 CSV 업로드", type="csv")

if uploaded_file is not None:
    st.success("✅ 파일 업로드 완료! 자동 분석 중...")
    
    try:
        # 데이터 로드
        df = pd.read_csv(uploaded_file, encoding='cp949', low_memory=False)
        
        st.subheader("📊 데이터 확인")
        st.write("컬럼:", list(df.columns))
        st.dataframe(df.head(3))
        
        # 자동 컬럼 탐지
        time_col = next((col for col in df.columns if '시간' in str(col)), None)
        up_col = next((col for col in df.columns if '승차' in str(col)), None)
        down_col = next((col for col in df.columns if '하차' in str(col)), None)
        line_col = next((col for col in df.columns if '호선' in str(col)), None)
        
        st.info(f"자동 탐지: 시간={time_col}, 승차={up_col}, 하차={down_col}")
        
        if time_col and up_col:
            # 시간대별 분석 (안전하게)
            df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
            df_clean = df.dropna(subset=[time_col, up_col])
            
            hourly = df_clean.groupby(time_col)[up_col].agg(['mean', 'sum']).reset_index()
            hourly.columns = ['시간대', '승차평균', '승차합계']
            
            # 1. 라인 차트
            st.subheader("📈 24시간 승차 패턴")
            fig = px.line(hourly, x='시간대', y='승차평균', 
                         title="시간대별 승차 평균", markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # 2. 밤샘 분석
            night_hours = hourly[(hourly['시간대'] >= 22) | (hourly['시간대'] <= 6)]
            if not night_hours.empty:
                peak_night = night_hours.loc[night_hours['승차평균'].idxmax()]
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🌙 밤샘 피크", f"{int(peak_night['시간대'])}시")
                with col2:
                    st.metric("최대 승차", f"{peak_night['승차평균']:.0f}명")
            
            # 3. 테이블
            st.subheader("📋 시간대별 상세")
            st.dataframe(hourly.round(0))
            
        else:
            st.error("❌ '시간대' 또는 '승차인원수' 컬럼을 찾을 수 없음")
            
    except Exception
