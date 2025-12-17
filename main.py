import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.title("🌙 서울 지하철 밤샘 분석기")

uploaded_file = st.file_uploader("지하철 CSV 업로드", type="csv")

if uploaded_file is not None:
    st.success("✅ 분석 중...")
    df = pd.read_csv(uploaded_file, encoding='cp949', low_memory=False)
    
    st.subheader("📊 데이터")
    st.dataframe(df.head(2))
    
    line_col = next((col for col in df.columns if '호선' in str(col)), None)
    time_cols = [col for col in df.columns if re.search(r'\d{2}시-\d{2}시', str(col))]
    
    st.info(f"시간대: {len(time_cols)}개")
    
    if len(time_cols) > 0 and line_col and line_col in df.columns:
        st.sidebar.header("호선 선택")
        lines = sorted(df[line_col].dropna().unique())[:15]
        selected_line = st.sidebar.selectbox("선택", lines)
        
        line_df = df[df[line_col] == selected_line]
        hourly_data = []
        
        for time_col in time_cols:
            hour_match = re.search(r'(\d{2})시', time_col)
            if hour_match:
                hour = int(hour_match.group(1))
                avg = line_df[time_col].mean()
                hourly_data.append({'시간': hour, '승차': avg})
        
        hourly_df = pd.DataFrame(hourly_data)
        
        st.subheader(f"📈 {selected_line} 24시간 패턴")
        fig_line = px.line(hourly_df, x='시간', y='승차', title="승차 트렌드", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.subheader("🌙 밤샘 히트맵")
        night_df = hourly_df[(hourly_df['시간'] >= 22) | (hourly_df['시간'] <= 6)]
        if len(night_df) > 0:
            fig_heatmap = px.imshow(
                night_df.pivot(columns='시간', values='승차').fillna(0).T.values,
                x=[f"{h:02d}시" for h in night_df['시간'].values],
                color_continuous_scale='RdYlBu_r',
                title="밤샘 시간대"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        peak_hour = hourly_df.loc[hourly_df['승차'].idxmax(), '시간']
        peak_value = hourly_df['승차'].max()
        
        col1, col2 = st.columns(2)
        col1.metric("🌙 밤샘 피크", f"{int(peak_hour)}시")
        col2.metric("최대 승차", f"{peak_value:.0f}명")
        
        st.dataframe(hourly_df.round(0))
    
    else:
        st.error("시간대/호선 컬럼 없음")
        st.write("컬럼:", list(df.columns[:10]))

else:
    st.info("CSV 업로드하세요!")
