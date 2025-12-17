import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.title("🌙 지하철 밤샘 분석기")
st.markdown("**지하철 시간대 CSV 업로드 → 자동 밤샘 패턴 시각화**")

# 1. CSV 업로드
uploaded_file = st.file_uploader("지하철 시간대 CSV 업로드 (승하차 컬럼 필요)", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 데이터 미리보기")
    st.dataframe(df.head())
    
    # 2. 시간 컬럼 자동 찾기
    st.sidebar.header("🔧 분석 설정")
    time_col = st.sidebar.selectbox("시간 컬럼", df.select_dtypes(include='number').columns.tolist())
    up_col = st.sidebar.selectbox("승차 컬럼", [col for col in df.columns if '승차' in col or 'up' in col.lower()] or df.columns.tolist())
    down_col = st.sidebar.selectbox("하차 컬럼", [col for col in df.columns if '하차' in col or 'down' in col.lower()] or df.columns.tolist())
    
    # 3. 시간대별 집계 (24시간 평균)
    df['hour'] = df[time_col] % 24  # 24시간 형식
    hourly = df.groupby('hour')[up_col].mean().reset_index()
    hourly.columns = ['hour', 'avg_up']
    
    # 피크 시간 찾기
    peak_hour = hourly.loc[hourly['avg_up'].idxmax(), 'hour']
    peak_value = hourly['avg_up'].max()
    
    # === 시각화 1: 히트맵 (시간대별 승하차 강도) ===
    st.subheader("🔥 시간대별 승하차 히트맵")
    heatmap_data = pd.DataFrame({
        '시간': [f"{int(h):02d}시" for h in hourly['hour']],
        '승차': hourly['avg_up'].values,
        '하차': df.groupby('hour')[down_col].mean().values
    })
    fig_heatmap = px.imshow(heatmap_data.set_index('시간').T.values,
                           labels=dict(x="시간대", y="활동", color="승하차 인원"),
                           x=heatmap_data['시간'], y=['승차', '하차'],
                           color_continuous_scale="Viridis")
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # === 시각화 2: 24시간 라인차트 ===
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 24시간 승차 패턴")
        fig_line = px.line(hourly, x='hour', y='avg_up', 
                          title="승차 트렌드", markers=True)
        fig_line.update_xaxes(tickvals=list(range(0,24,2)), ticktext=[f"{h:02d}" for h in range(0,24,2)])
        st.plotly_chart(fig_line, use_container_width=True)
    
    # === 핵심 메트릭 ===
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("밤샘 피크", f"{int(peak_hour):02d}시", f"{peak_value:.0f}")
    with col2:
        night_avg = hourly[(hourly['hour'] >= 22) | (hourly['hour'] <= 6)]['avg_up'].mean()
        st.metric("야간 평균", f"{night_avg:.0f}", "📊")
    with col3:
        rush_avg = hourly[(hourly['hour'] >= 7) & (hourly['hour'] <= 9)]['avg_up'].mean()
        st.metric("출근 피크", f"{rush_avg:.0f}", f"{night_avg/rush_avg:.0%}↓")
    
    # === 밤샘 인사이트 ===
    st.subheader("💡 밤샘 분석 결과")
    if peak_hour >= 22 or peak_hour <= 6:
        st.success(f"✅ **{int(peak_hour):02d}시**가 가장 붐빕니다! 새벽/늦은 밤 지하철 이용자가 많아요.")
    else:
        st.warning(f"⚠️ 출퇴근 중심 ({int(peak_hour):02d}시 피크)")
    
    st.dataframe(hourly.round(0))
    
else:
    st.info("""
    **지하철 CSV 예시 형식:**
    ```
    시간, 승차인원, 하차인원
    5, 1234, 567
    6, 2345, 890
    ...
    ```
    공공데이터포털에서 "지하철 시간대" 검색 → CSV 다운로드!
    """)
