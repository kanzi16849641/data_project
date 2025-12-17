import streamlit as st
import pandas as pd
import plotly.express as px
import re
import numpy as np

st.title("🌙 서울 지하철 밤샘 분석기 (호선별 + 전처리 포함)")

# 1. 파일 업로드
uploaded_file = st.file_uploader("서울시 지하철 시간대별 승차 CSV 업로드", type="csv")

if uploaded_file is not None:
    # 2. CSV 로드
    df = pd.read_csv(uploaded_file, encoding="cp949", low_memory=False)

    st.subheader("📊 원본 데이터 미리보기")
    st.dataframe(df.head(3))
    st.write("컬럼:", list(df.columns))

    # 3. 호선 컬럼, 시간대 컬럼 자동 탐지
    line_col = next((col for col in df.columns if "호선" in str(col)), None)
    time_cols = [col for col in df.columns if re.search(r"\d{2}시-\d{2}시", str(col))]

    if (line_col is None) or len(time_cols) == 0:
        st.error("❌ '호선' 또는 '00시-01시' 형식의 시간대 컬럼을 찾을 수 없습니다.")
    else:
        st.info(f"감지된 시간대 컬럼 수: {len(time_cols)}개")

        # 4. 전처리 옵션 (사이드바)
        st.sidebar.header("🧹 전처리 옵션")

        na_method = st.sidebar.selectbox(
            "결측치 처리 방식",
            ["0으로 채우기", "해당 시간대 평균으로 채우기"],
            index=0,
        )

        outlier_method = st.sidebar.selectbox(
            "이상치 처리 방식",
            ["처리하지 않음", "IQR 기반 클리핑"],
            index=1,
        )

        # 5. 결측치 처리
        work_df = df.copy()

        if na_method == "0으로 채우기":
            work_df[time_cols] = work_df[time_cols].fillna(0)
        else:  # 평균으로 채우기
            work_df[time_cols] = work_df[time_cols].apply(
                lambda s: s.fillna(s.mean())
            )

        # 6. 이상치 처리 (IQR 클리핑)
        if outlier_method == "IQR 기반 클리핑":
            Q1 = work_df[time_cols].quantile(0.25)
            Q3 = work_df[time_cols].quantile(0.75)
            IQR = Q3 - Q1

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            # 넘파이 where를 쓰면 브로드캐스팅 때문에 경고가 뜰 수 있어서,
            # clip을 컬럼 단위로 적용하는 방식이 더 안전함.
            for col in time_cols:
                work_df[col] = work_df[col].clip(lower[col], upper[col])

        st.subheader("🧾 전처리된 데이터 예시")
        st.dataframe(work_df[time_cols].head(3).round(0))

        # 7. 호선 선택
        st.sidebar.header("🚇 호선 선택")
        lines = sorted(work_df[line_col].dropna().unique().tolist())
        selected_line = st.sidebar.selectbox("호선", lines)

        # 선택된 호선만 필터
        line_df = work_df[work_df[line_col] == selected_line]

        # 8. 시간대별 평균 승차 계산
        avg_time_data = line_df[time_cols].mean()

        hourly_data = []
        for col in time_cols:
            # "04시-05시 승차인원" → 4
            hour_match = re.search(r"(\d{2})시", col)
            if hour_match:
                hour = int(hour_match.group(1))
                hourly_data.append({"시간": hour, "승차평균": avg_time_data[col]})

        hourly_df = pd.DataFrame(hourly_data).sort_values("시간")

        # 9. 24시간 선 그래프 (깔끔 버전)
        st.subheader(f"📈 {selected_line} 24시간 승차 패턴")

        fig_line = px.line(
            hourly_df,
            x="시간",
            y="승차평균",
            title=f"{selected_line} 시간대별 평균 승차인원",
            markers=True,
            line_shape="linear",  # 직선
        )

        fig_line.update_traces(
            line=dict(color="#FF6B6B", width=3),
            marker=dict(size=6),
        )

        fig_line.update_layout(
            xaxis=dict(title="시간대", tickmode="linear", dtick=1),
            yaxis=dict(title="평균 승차인원"),
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        st.plotly_chart(fig_line, use_container_width=True)

        # 10. 밤샘 vs 출퇴근 바차트
        st.subheader("⚡ 밤샘 vs 출퇴근 시간대 비교")

        night_mask = (hourly_df["시간"] >= 22) | (hourly_df["시간"] <= 6)
        rush_mask = (hourly_df["시간"].between(7, 9)) | (hourly_df["시간"].between(17, 19))

        night_data = hourly_df[night_mask]
        rush_data = hourly_df[rush_mask]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("🌙 **밤샘 (22–06시)**")
            if len(night_data) > 0:
                fig_night = px.bar(
                    night_data,
                    x="시간",
                    y="승차평균",
                    color="승차평균",
                    color_continuous_scale="Reds",
                )
                fig_night.update_layout(showlegend=False, xaxis_title="시간대", yaxis_title="평균 승차인원")
                st.plotly_chart(fig_night, use_container_width=True)
            else:
                st.write("해당 구간 데이터 없음")

        with col2:
            st.markdown("💼 **출퇴근 (07–09, 17–19시)**")
            if len(rush_data) > 0:
                fig_rush = px.bar(
                    rush_data,
                    x="시간",
                    y="승차평균",
                    color="승차평균",
                    color_continuous_scale="Blues",
                )
                fig_rush.update_layout(showlegend=False, xaxis_title="시간대", yaxis_title="평균 승차인원")
                st.plotly_chart(fig_rush, use_container_width=True)
            else:
                st.write("해당 구간 데이터 없음")

        # 11. 핵심 메트릭
        peak_row = hourly_df.loc[hourly_df["승차평균"].idxmax()]
        night_avg = night_data["승차평균"].mean() if len(night_data) > 0 else 0
        rush_avg = rush_data["승차평균"].mean() if len(rush_data) > 0 else 0
        night_ratio = (night_avg / rush_avg * 100) if rush_avg > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏆 피크 시간", f"{int(peak_row['시간'])}시", f"{peak_row['승차평균']:.0f}")
        c2.metric("🌙 밤샘 평균", f"{night_avg:.0f}")
        c3.metric("💼 출퇴근 평균", f"{rush_avg:.0f}")
        c4.metric("밤샘/출퇴근 비율", f"{night_ratio:.0f}%")

        # 12. 상세 테이블
        st.subheader("📋 시간대별 상세 데이터")
        st.dataframe(hourly_df.round(0))

else:
    st.info("👆 서울시 지하철 시간대별 승차 CSV를 업로드해주세요.")
