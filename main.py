import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# 폰트 설정을 위한 Matplotlib 설정 (한글 깨짐 방지 - Streamlit 환경에 따라 필요 없을 수 있음)
# plt.rcParams['font.family'] = 'Malgun Gothic' # Windows 사용자
# plt.rcParams['axes.unicode_minus'] = False 

def analyze_fitness_data(df, target_col='체지방율', top_n=5):
    """
    체지방율과 다른 속성 간의 상관관계를 분석하고 결과를 반환합니다.
    """
    
    # 1. 숫자형 데이터만 추출
    numeric_df = df.select_dtypes(include=np.number)
    
    # 2. 결측치 제거 (상관관계 계산을 위해)
    numeric_df = numeric_df.dropna()
    
    # 3. 목표 컬럼이 데이터프레임에 있는지 확인
    if target_col not in numeric_df.columns:
        return None, f"오류: 데이터에 '{target_col}' 컬럼이 없습니다. 컬럼명을 확인해주세요."
    
    # 4. 상관관계 계산
    correlation_matrix = numeric_df.corr()
    
    # 5. 목표 컬럼과의 상관관계 추출 (자기 자신 제외)
    target_corr = correlation_matrix[target_col].drop(target_col)
    
    # 6. 절대값 기준으로 상위 N개 속성 선택
    top_correlations = target_corr.abs().nlargest(top_n)
    
    # 7. 원래의 상관관계 값과 속성명 추출
    top_features = top_correlations.index.tolist()
    final_corr = target_corr[top_features]
    
    # 히트맵을 위한 상관관계 행렬 (체지방율 + 상위 속성)
    heatmap_cols = [target_col] + top_features
    heatmap_data = numeric_df[heatmap_cols].corr()
    
    return final_corr.sort_values(ascending=False), heatmap_data

def create_heatmap(corr_data):
    """
    상관관계 히트맵을 생성합니다.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr_data, 
        annot=True, 
        cmap='coolwarm', 
        fmt=".2f",
        linewidths=.5,
        cbar_kws={'label': '상관관계 계수'},
        ax=ax
    )
    plt.title('체지방율 및 상위 속성 간 상관관계 히트맵', fontsize=16)
    st.pyplot(fig)

def create_scatterplot(df, target_col, feature):
    """
    체지방율과 특정 속성 간의 산점도 그래프를 생성합니다.
    """
    # Plotly Express를 사용하여 대화형 산점도 생성
    fig = px.scatter(
        df, 
        x=feature, 
        y=target_col,
        title=f'{target_col} vs {feature} 산점도',
        labels={feature: feature, target_col: target_col},
        trendline="ols" # 최소자승법(OLS) 추세선 추가
    )
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(
        page_title="운동 데이터 분석 대시보드",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏃‍♂️ 운동 데이터 분석 웹페이지")
    st.markdown("---")

    # 세션 상태를 사용하여 파일을 저장합니다.
    if 'data' not in st.session_state:
        st.session_state.data = None

    # 파일 업로드 섹션
    st.sidebar.header("📂 파일 업로드")
    uploaded_file = st.sidebar.file_uploader(
        "운동 데이터를 담은 CSV 파일을 업로드해주세요.", 
        type=['csv']
    )

    if uploaded_file is not None:
        try:
            # 파일을 데이터프레임으로 읽기
            df = pd.read_csv(uploaded_file)
            st.session_state.data = df
            st.success("파일 업로드 및 데이터 로드 성공!")
            
            # 사용자에게 데이터 미리보기 제공
            st.subheader("업로드된 데이터 미리보기")
            st.dataframe(df.head())
            st.markdown("---")

        except Exception as e:
            st.error(f"파일을 읽는 도중 오류가 발생했습니다: {e}")
            st.session_state.data = None
            
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # 분석 실행
        st.header("📊 체지방율 상관관계 분석")
        target_col = '체지방율'
        top_n = 5
        
        # 분석 함수 호출
        top_correlations, heatmap_data = analyze_fitness_data(df, target_col, top_n)

        if top_correlations is None:
            st.warning(heatmap_data) # 오류 메시지 출력
            return
            
        st.markdown(f"**'{target_col}'**과 **가장 높은 상관관계**를 보이는 **상위 {top_n}개** 속성입니다.")

        # 상관관계 표 출력
        st.table(top_correlations.rename('상관관계 계수').to_frame().style.format('{:.3f}'))
        st.markdown("---")

        # 1. 히트맵 시각화
        st.subheader("🔥 상관관계 히트맵")
        create_heatmap(heatmap_data)
        st.markdown("---")
        
        # 2. 산점도 시각화
        st.subheader("📈 상위 속성별 산점도")
        
        # 상위 속성을 드롭다운으로 선택
        selected_feature = st.selectbox(
            "산점도를 확인할 속성을 선택하세요:",
            top_correlations.index.tolist()
        )
        
        if selected_feature:
            create_scatterplot(df, target_col, selected_feature)
        
    else:
        st.info("왼쪽 사이드바에서 CSV 파일을 업로드하여 분석을 시작하세요.")

if __name__ == '__main__':
    main()
