import streamlit as st

def display_metrics(current_df, previous_df):
    """メトリクスを表示
    
    Args:
        current_df (pd.DataFrame): 現在の人口データ
        previous_df (pd.DataFrame): 1年前の人口データ（Noneの場合もある）
    """
    from utils.data_loader import ColumnNames
    
    col1, col2, col3, col4 = st.columns(4)

    # 人口総数
    total_population = current_df[ColumnNames.POPULATION].sum()
    previous_population = previous_df[ColumnNames.POPULATION].sum() if previous_df is not None else None
    with col1:
        st.metric(
            label="総人口",
            value=f"{int(total_population):,}人",
            delta=f"1年前から{int(total_population - previous_population):+,}人" if previous_population is not None else None
        )

    # 世帯総数
    total_households = current_df[ColumnNames.HOUSEHOLDS].sum()
    previous_households = previous_df[ColumnNames.HOUSEHOLDS].sum() if previous_df is not None else None
    with col2:
        st.metric(
            label="総世帯数",
            value=f"{int(total_households):,}世帯",
            delta=f"1年前から{int(total_households - previous_households):+,}世帯" if previous_households is not None else None
        )

    # 男性総数
    total_male = current_df[ColumnNames.MALE].sum()
    previous_male = previous_df[ColumnNames.MALE].sum() if previous_df is not None else None
    with col3:
        st.metric(
            label="男性人口",
            value=f"{int(total_male):,}人",
            delta=f"1年前から{int(total_male - previous_male):+,}人" if previous_male is not None else None
        )

    # 女性総数
    total_female = current_df[ColumnNames.FEMALE].sum()
    previous_female = previous_df[ColumnNames.FEMALE].sum() if previous_df is not None else None
    with col4:
        st.metric(
            label="女性人口",
            value=f"{int(total_female):,}人",
            delta=f"1年前から{int(total_female - previous_female):+,}人" if previous_female is not None else None
        ) 