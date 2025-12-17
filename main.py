import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.title("🌙 서울 지하철 밤샘 분석기")

uploaded_file = st.file_uploader("지하철 CSV 업로드", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='cp949', low_memory=False)
    
    st.subheader("📊 데이터 미리보기")
    st.dataframe(df.head(2))
    
    # 호선 컬럼 찾기
    line_col = next((col for col in df.columns if '호선' in str(col)), None)
    
    # 시간대 컬럼 찾기 (00시-01시 형식)
    time_cols = [col for col in df.columns if re.search(r'\d{2}시-\d{2}시', str(col))]
    
    st.info(f"발견된 시간대: {len(time_cols)}개")
    
    if len(time_cols) > 0:
        # 시간대별 평균 승차 계산
        avg_time_data = df[time_cols].mean()
        
        # 시간대 파싱
        hourly_data = []
        for col in time_cols:
            hour = int(re.search(r'(\d{2})시', col).group(1))
            hourly_data.append({'시간': hour, '승차평균': avg_time_data[col]})
        
        hourly_df = pd.DataFrame(hourly_data).sort_values('시간')
        
        # === 1. 24시간 라인 차트 ===
        st.subheader("📈 24시간 승하차 패턴")
        fig_line = px.line(hourly_df, x='시간', y='승차평균', 
                          title="시간대별 평균 승차인원", markers=True,
                          labels={'승차평균': '평균 승차인원'})
        fig_line.update_layout(xaxis_title="시간대", yaxis_title="승차인원")
        st.plotly_chart(fig_line, use_container_width=True)
        
        # === 2. 밤샘 vs 출퇴근 바 차트 ===
        st.subheader("⚡ 시간대별 비교")
        night_data = hourly_df[(hourly_df['시간'] >= 22) | (hourly_df['시간'] <= 6)]
        rush_data = hourly_df[(hourly_df['시간'] >= 7) & (hourly_df['시간'] <= 9)]
        
        col1, col2 = st.columns(2)
        with col1:
            fig_night = px.bar(night_data, x='시간', y='승차평균', 
                              title="🌙 밤샘 시간대", color='승차평균',
                              color_continuous_scale='Reds')
            st.plotly_chart(fig_night, use_container_width=True)
        
        with col2:
            fig_rush = px.bar(rush_data, x='시간', y='승차평균', 
                             title="💼 출퇴근 시간대", color='승차평균',
                             color_continuous_scale='Blues')
            st.plotly_chart(fig_rush, use_container_width=True)
        
        # === 3. 핵심 메트릭 ===
        peak_time = hourly_df.loc[hourly_df['승차평균'].idxmax()]
        night_avg = night_data['승차평균'].mean()
        rush_avg = rush_data['승차평균'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏆 피크 시간", f"{int(peak_time['시간'])}시")
        col2.metric("최대 승차", f"{peak_time['승차평균']:.0f}")
        col3.metric("🌙 밤샘 평균", f"{night_avg:.0f}")
        col4.metric("💼 출근 평균", f"{rush_avg:.0f}")
        
        # === 4. 상세 테이블 ===
        st.subheader("📋 시간대별 데이터")
        st.dataframe(hourly_df.round(0))
        
        # === 5. 밤샘 인사이트 ===
        st.subheader("💡 분석 인사이트")
        if night_avg > rush_avg * 0.3:
            st.success("🌙 밤샘 이용률이 출퇴근의 30% 이상! 야간 수요 높음")
        else:
            st.info("💼 출퇴근 중심 이용 패턴")
        
    else:
        st.error("시간대 컬럼을 찾을 수 없음")
        st.write("처음 10개 컬럼:", list(df.columns[:10]))

else:
    st.info("👆 지하철 CSV 파일 업로드하세요!")
