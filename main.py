import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

st.title("🌙 서울 지하철 밤샘 분석기")

uploaded_file = st.file_uploader("지하철 CSV 업로드", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='cp949', low_memory=False)
    
    st.subheader("📊 데이터 미리보기")
    st.dataframe(df.head(2))
    
    # 호선 컬럼 찾기
    line_col = next((col for col in df.columns if '호선' in str(col)), None)
    
    # 시간대 컬럼 찾기
    time_cols = [col for col in df.columns if re.search(r'\d{2}시-\d{2}시', str(col))]
    
    st.info(f"시간대: {len(time_cols)}개")
    
    if len(time_cols) > 0 and line_col and line_col in df.columns:
        # 호선 선택 사이드바
        st.sidebar.header("🔧 분석 설정")
        lines = sorted(df[line_col].dropna().unique())[:10]
        selected_line = st.sidebar.selectbox("호선 선택", lines)
        
        # 선택된 호선 데이터
        line_df = df[df[line_col] == selected_line]
        avg_time_data = line_df[time_cols].mean()
        
        # 시간대 파싱
        hourly_data = []
        for col in time_cols:
            hour = int(re.search(r'(\d{2})시', col).group(1))
            hourly_data.append({'시간': hour, '승차평균': avg_time_data[col]})
        
        hourly_df = pd.DataFrame(hourly_data).sort_values('시간')
        
        # === 1. 업그레이드 선그래프 (호선별) ===
        st.subheader(f"📈 {selected_line} 24시간 승차 패턴")
        fig_line = px.line(hourly_df, x='시간', y='승차평균', 
                          title=f"{selected_line}호선 시간대별 승차",
                          markers=True, line_shape='spline')
        fig_line.update_traces(line=dict(color='#FF6B6B', width=4))
        fig_line.update_layout(
            xaxis_title="시간대", yaxis_title="평균 승차인원",
            font=dict(size=12), hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        # === 2. 밤샘 vs 출퇴근 비교 바차트 ===
        st.subheader("⚡ 밤샘 vs 출퇴근 비교")
        night_data = hourly_df[(hourly_df['시간'] >= 22) | (hourly_df['시간'] <= 6)]
        rush_data = hourly_df[(hourly_df['시간'].between(7,9)) | (hourly_df['시간'].between(17,19))]
        
        col1, col2 = st.columns(2)
        with col1:
            fig_night = px.bar(night_data, x='시간', y='승차평균', 
                              title="🌙 밤샘 (22-06시)", color='승차평균',
                              color_continuous_scale='Reds')
            fig_night.update_layout(showlegend=False, xaxis_title="시간대")
            st.plotly_chart(fig_night, use_container_width=True)
        
        with col2:
            fig_rush = px.bar(rush_data, x='시간', y='승차평균', 
                             title="💼 출퇴근 (07-09,17-19시)", color='승차평균',
                             color_continuous_scale='Blues')
            fig_rush.update_layout(showlegend=False, xaxis_title="시간대")
            st.plotly_chart(fig_rush, use_container_width=True)
        
        # === 3. 화려한 메트릭 ===
        peak_time = hourly_df.loc[hourly_df['승차평균'].idxmax()]
        night_avg = night_data['승차평균'].mean()
        rush_avg = rush_data['승차평균'].mean()
        night_ratio = (night_avg / rush_avg * 100) if rush_avg > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏆 피크시간", f"{int(peak_time['시간'])}시", f"{peak_time['승차평균']:.0f}")
        col2.metric("🌙 밤샘 평균", f"{night_avg:.0f}", f"{night_ratio:.0f}%")
        col3.metric("💼 출퇴근 평균", f"{rush_avg:.0f}")
        col4.metric("총 시간대", f"{len(hourly_df)}개")
        
        # === 4. 테이블 ===
        st.subheader("📋 상세 데이터")
        st.dataframe(hourly_df.round(0))
        
        # === 5. 인사이트 ===
        st.subheader("💡 분석 결과")
        if night_ratio > 25:
            st.success(f"🔥 {selected_line}호선 밤샘 수요 높음 ({night_ratio:.0f}% 수준)")
        else:
            st.info(f"✅ {selected_line}호선 출퇴근 중심 패턴")
            
    else:
        st.error("호선/시간대 컬럼 없음")
        st.write("컬럼:", list(df.columns[:10]))

else:
    st.info("CSV 업로드하세요!")
