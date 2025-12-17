import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

st.title("🌙 지구인 밤샘 레이더 - 한국 버전")
st.markdown("**시간대별 CSV 데이터를 업로드하면 자동으로 밤샘 패턴 분석**")

# 1. 사용자 데이터 업로드
uploaded_file = st.file_uploader("CSV 파일 선택 (컬럼: 시간, 택배/유동인구/전력 등)", type="csv")

if uploaded_file is not None:
    # 데이터 로드 & 미리보기
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 업로드된 데이터 미리보기")
    st.dataframe(df.head(10), use_container_width=True)
    
    # 2. 사이드바에서 분석 설정
    st.sidebar.header("🔧 분석 설정")
    time_col = st.sidebar.selectbox("시간 컬럼", df.columns)
    activity_cols = st.sidebar.multiselect("활동 컬럼 선택", df.columns[1:], default=df.columns[1:5])
    
    # 시간대별 평균 계산
    df['hour'] = pd.to_datetime(df[time_col]).dt.hour
    activity_means = df.groupby('hour')[activity_cols].mean()
    
    # 3. 메인 분석 결과
    col1, col2, col3 = st.columns(3)
    with col1:
        peak_hour = activity_means.mean(axis=1).idxmax()
        st.metric("밤샘 피크", f"{peak_hour:02d}시", "📈")
    with col2:
        total_activity = activity_means.sum().max()
        st.metric("최대 활동량", f"{total_activity:.0f}", "🔥")
    
    # 레이더 차트
    fig = go.Figure()
    for col in activity_cols:
        fig.add_trace(go.Scatterpolar(r=activity_means[col], 
                                     theta=[f"{h:02d}시" for h in range(24)],
                                     fill='toself', name=col))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(activity_means.max())*1.1])),
                      showlegend=True, title="24시간 밤샘 패턴 레이더")
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. 자동 인사이트 생성
    st.subheader("💡 밤샘 인사이트")
    peak_activities = activity_means.iloc[peak_hour][activity_cols].sort_values(ascending=False)
    top_activity = peak_activities.index[0]
    st.success(f"**{peak_hour:02d}시**에 **{top_activity}**이 가장 활발합니다!")
    st.info(f"데이터 기반 분석: {activity_cols[0]} 상관계수 {activity_means.corr().iloc[0,1]:.2f}")
    
    # 상세 테이블
    st.dataframe(activity_means.round(1))
    
else:
    st.info("👆 공공데이터포털에서 '시간대 택배', 'S-DoT 유동인구' CSV를 다운로드해 업로드하세요!")
