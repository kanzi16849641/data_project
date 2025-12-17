import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("🌙 서울 지하철 밤샘 분석기")
st.markdown("**실제 서울시 지하철 데이터로 24시간 패턴 분석**")

# CSV 업로드 (이미 업로드된 파일)
uploaded_file = st.file_uploader("지하철 CSV 업로드", type="csv")

if uploaded_file is not None:
    # 서울시 지하철 데이터 전처리
    df = pd.read_csv(uploaded_file, encoding='cp949')  # 한글 CSV라 cp949
    st.subheader("📊 데이터 구조")
    st.dataframe(df.head())
    
    # 서울시 지하철 데이터 컬럼 예상: '사용일자', '호선명', '역명', '시간대', '승차인원수', '하차인원수'
    st.sidebar.header("🔧 분석 설정")
    
    # 시간대 컬럼 선택
    time_cols = [col for col in df.columns if '시간' in col or 'time' in col.lower()]
    time_col = st.sidebar.selectbox("시간대 컬럼", time_cols, index=0)
    
    up_col = st.sidebar.selectbox("승차인원", [col for col in df.columns if '승차' in col])
    down_col = st.sidebar.selectbox("하차인원", [col for col in df.columns if '하차' in col])
    
    # 호선/역 선택 (사이드바 필터)
    lines = df['호선명'].unique()[:10]  # 상위 10개 호선
    selected_line = st.sidebar.selectbox("호선 선택", lines)
    
    # 데이터 필터링
    filtered_df = df[df['호선명'] == selected_line].copy()
    filtered_df[time_col] = pd.to_numeric(filtered_df[time_col], errors='coerce')
    filtered_df = filtered_df.dropna(subset=[time_col, up_col, down_col])
    
    # 시간대별 평균 집계 (00~23시)
    hourly = filtered_df.groupby(time_col).agg({
        up_col: 'mean',
        down_col: 'mean'
    }).reset_index()
    hourly.columns = ['hour', '승차평균', '하차평균']
    hourly['총합'] = hourly['승차평균'] + hourly['하차평균']
    
    # === 1. 히트맵 ===
    st.subheader(f"🔥 {selected_line} 시간대별 승하차 히트맵")
    heatmap_df = hourly.melt(id_vars='hour', value_vars=['승차평균', '하차평균'], var_name='유형', value_name='인원')
    heatmap_df['hour_label'] = heatmap_df['hour'].astype(int).astype(str).str.zfill(2) + '시'
    
    fig_heatmap = px.imshow(
        hourly[['승차평균', '하차평균']].values,
        x=[f"{int(h):02d}시" for h in hourly['hour']],
        y=['승차', '하차'],
        color_continuous_scale='RdYlBu_r',
        title=f"{selected_line}호선 승하차 패턴"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # === 2. 24시간 라인차트 ===
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 승차 트렌드")
        fig_up = px.line(hourly, x='hour', y='승차평균', 
                        title="시간대별 승차", markers=True)
        st.plotly_chart(fig_up, use_container_width=True)
    
    with col2:
        st.subheader("📉 하차 트렌드") 
        fig_down = px.line(hourly, x='hour', y='하차평균',
                          title="시간대별 하차", markers=True)
        st.plotly_chart(fig_down, use_container_width=True)
    
    # === 3. 밤샘 분석 ===
    night_hours = hourly[(hourly['hour'] >= 22) | (hourly['hour'] <= 6)]
    peak_night = night_hours.loc[night_hours['총합'].idxmax()]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("밤샘 피크", f"{int(peak_night['hour']):02d}시", f"{peak_night['총합']:.0f}")
    with col2:
        st.metric("야간 평균", f"{night_hours['총합'].mean():.0f}")
    with col3:
        st.metric("출근 피크", f"{hourly['총합'].max():.0f}")
    
    # 인사이트
    st.subheader("💡 밤샘 인사이트")
    st.success(f"**{selected_line}호선** {int(peak_night['hour']):02d}시에 밤샘 이용자 {peak_night['총합']:.0f}명!")
    
    st.dataframe(hourly.round(0))
    
else:
    st.info("✅ 업로드된 '서울시 지하철...' CSV 파일을 선택하세요!")
