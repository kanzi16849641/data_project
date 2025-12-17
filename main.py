import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("🌙 서울 지하철 밤샘 분석기")

# 파일 업로드
uploaded_file = st.file_uploader("지하철 CSV 업로드", type="csv")

if uploaded_file is not None:
    try:
        # 안전하게 CSV 로드 (cp949 한글 인코딩)
        df = pd.read_csv(uploaded_file, encoding='cp949', low_memory=False)
        
        st.subheader("📊 데이터 컬럼 확인")
        st.write("컬럼 목록:", df.columns.tolist())
        st.dataframe(df.head(3))
        
        # 서울시 지하철 표준 컬럼 자동 탐지
        time_candidates = [col for col in df.columns if '시간' in str(col)]
        up_candidates = [col for col in df.columns if '승차' in str(col)]
        down_candidates = [col for col in df.columns if '하차' in str(col)]
        line_candidates = [col for col in df.columns if '호선' in str(col)]
        
        st.sidebar.header("🔧 분석 설정")
        
        # 안전한 컬럼 선택 (존재하는 것만)
        if time_candidates:
            time_col = st.sidebar.selectbox("시간대", time_candidates)
        else:
            time_col = None
            
        if up_candidates:
            up_col = st.sidebar.selectbox("승차인원", up_candidates)
        else:
            up_col = None
            
        if line_candidates:
            lines = df[line_candidates[0]].dropna().unique()[:10]
            selected_line = st.sidebar.selectbox("호선", lines)
        else:
            selected_line = None
        
        # 분석 버튼
        if st.button("🚀 밤샘 분석 시작") and time_col and up_col:
            
            with st.spinner("분석 중..."):
                # 데이터 필터링 (안전하게)
                work_df = df.copy()
                
                if selected_line:
                    work_df = work_df[work_df[line_candidates[0]] == selected_line]
                
                # 시간대 숫자 변환 (에러 방지)
                work_df[time_col] = pd.to_numeric(work_df[time_col], errors='coerce')
                work_df = work_df.dropna(subset=[time_col, up_col])
                
                # 시간대별 평균
                hourly = work_df.groupby(time_col)[up_col].mean().reset_index()
                hourly.columns = ['시간대', '승차평균']
                
                # 시각화
                st.subheader("📈 24시간 승차 패턴")
                fig = px.line(hourly, x='시간대', y='승차평균', 
                             title="시간대별 승차 트렌드", markers=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # 밤샘 피크 계산
                night_data = hourly[(hourly['시간대'] >= 22) | (hourly['시간대'] <= 6)]
                if len(night_data) > 0:
                    peak_time = night_data.loc[night_data['승차평균'].idxmax(), '시간대']
                    st.success(f"🌙 밤샘 피크: **{int(peak_time)}시**")
                
                st.dataframe(hourly.round(0))
                
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")
        st.info("컬럼 이름을 다시 확인해주세요!")
        
else:
    st.info("👆 지하철 CSV 파일을 업로드하고 '밤샘 분석 시작' 버튼을 클릭하세요!")
