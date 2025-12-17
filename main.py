import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🌙 서울 지하철 밤샘 분석기")

uploaded_file = st.file_uploader("지하철 CSV 업로드", type="csv")

if uploaded_file is not None:
    st.success("✅ 파일 분석 중...")
    
    try:
        df = pd.read_csv(uploaded_file, encoding='cp949', low_memory=False)
        
        st.subheader("📊 데이터 구조")
        st.write("컬럼 (시간대별 승하차):", list(df.columns)[:10])
        st.dataframe(df.head(3))
        
        # 시간대 컬럼 자동 찾기 (00시-01시, 04시-05시 형식)
        time_cols = [col for col in df.columns if '시-' in str(col) or '-' in str(col) and '시' in str(col)]
        
        if len(time_cols) > 0:
            # 첫 번째 시간대 컬럼 선택 (승차인원)
            up_col = time_cols[0]
            st.info(f"자동 선택: {up_col} (승차인원)")
            
            # 호선명 컬럼 찾기
            line_col = next((col for col in df.columns if '호선' in str(col)), None)
            
            # 시간대별 데이터 추출 및 파싱
            hourly_data = []
            for _, row in df.head(10).iterrows():  # 상위 10행만 (속도용)
                for time_col in time_cols[:24]:  # 24시간
                    if pd.notna(row[time_col]):
                        hour_start = int(time_col.split('-')[0].replace('시', ''))
                        hourly_data.append({
                            '시간대': hour_start,
                            '승차인원': row[time_col],
                            '호선': row.get(line_col, 'Unknown')
                        })
            
            hourly_df = pd.DataFrame(hourly_data)
            
            # 전체 평균 계산
            avg_hourly = hourly_df.groupby('시간대')['승차인원'].mean().reset_index()
            
            # 시각화
            st.subheader("📈 24시간 승차 패턴")
            fig = px.line(avg_hourly, x='시간대', y='승차인원', 
                         title="시간대별 평균 승차인원", markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # 밤샘 분석
            night_data = avg_hourly[(avg_hourly['시간대'] >= 22) | (avg_hourly['시간대'] <= 6)]
            if not night_data.empty:
                peak_night = night_data.loc[night_data['승차인원'].idxmax()]
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🌙 밤샘 피크", f"{int(peak_night['시간대'])}시")
                with col2:
                    st.metric("평균 승차", f"{peak_night['승차인원']:.0f}명")
            
            st.dataframe(avg_hourly.round(0))
            
        else:
            st.error("❌ 시간대 컬럼 못찾음. 컬럼명 예시 보여줌:")
            st.write("처음 20개 컬럼:", list(df.columns[:20]))
            
    except Exception as e:
        st.error(f"오류: {str(e)}")

else:
    st.info("👆 CSV 업로드하세요!")
