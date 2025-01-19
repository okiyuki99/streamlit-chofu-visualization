import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from utils.data_loader import (
    load_data, get_all_sheet_names,
    ColumnNames
)

# Streamlitのセットアップ
st.set_page_config(
    page_title="人口推移グラフ",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
# 調布市の人口推移グラフ

オープンデータをもとにした調布市の市区町村別の人口推移を時系列グラフで可視化しています
""")

# 時系列データの準備
def get_population_history():
    """令和4年4月から最新までの人口データを取得"""
    history_data = []
    sheet_names = get_all_sheet_names()
    
    for display_name, sheet_info in sheet_names:
        year = int(sheet_info.split(':')[1][1:].split('.')[0])
        month = int(sheet_info.split(':')[1].split('.')[1])
        
        # R4.4.1以降のデータのみを使用
        if year < 4 or (year == 4 and month < 4):
            continue
            
        df = load_data(sheet_info)
        
        # 各地域の人口データを取得
        for _, row in df.iterrows():
            if not pd.isna(row[ColumnNames.POPULATION]) and not pd.isna(row['S_NAME']):
                history_data.append({
                    '年月': f'令和{year}年{month}月',
                    '地域': row['S_NAME'],
                    '人口': row[ColumnNames.POPULATION]
                })
        
        # 全人口のデータを追加
        total = df[ColumnNames.POPULATION].sum()
        history_data.append({
            '年月': f'令和{year}年{month}月',
            '地域': '全人口',
            '人口': total
        })
    
    return pd.DataFrame(history_data)

# 時系列データの取得
history_df = get_population_history()

# サイドバーの設定
with st.sidebar:
    st.header('📊 表示設定')
    
    # 地域選択の設定
    with st.expander('📍 地域の選択', expanded=True):
        # 利用可能な地域のリストを取得（全人口を先頭に）
        available_areas = ['全人口'] + sorted(
            [area for area in history_df['地域'].unique() if area != '全人口']
        )
        
        # デフォルトで全人口を選択
        selected_areas = st.multiselect(
            '表示する地域を選択',
            available_areas,
            default=['全人口']
        )
    
    # グラフタイプの選択
    with st.expander('📈 グラフの種類', expanded=True):
        graph_type = st.radio(
            'グラフの種類を選択',
            ['線グラフ', '棒グラフ'],
            horizontal=True
        )
    
    # Y軸のスケール設定
    with st.expander('📏 Y軸の設定', expanded=True):
        y_scale = st.radio(
            'Y軸のスケールを選択',
            ['自動', '固定'],
            horizontal=True
        )
        
        y_min = y_max = None
        if y_scale == '固定':
            col1, col2 = st.columns(2)
            with col1:
                y_min = st.number_input('最小値', value=0, step=1000)
            with col2:
                # 初期最大値を全人口の最大値に設定
                default_max = int(history_df[history_df['地域'] == '全人口']['人口'].max())
                y_max = st.number_input('最大値', value=default_max, step=1000)

if selected_areas:
    # 選択された地域のデータでグラフを作成
    fig = go.Figure()
    
    for area in selected_areas:
        # データのコピーを作成
        area_data = history_df[history_df['地域'] == area].copy()
        
        # 年月を日付型に変換してソート
        def convert_to_date(x):
            # 令和から数字を抽出
            year = int(x.replace('令和', '').split('年')[0])
            # 月を抽出
            month = int(x.split('年')[1].replace('月', ''))
            # 令和を西暦に変換（令和1年 = 2019年）
            year = year + 2018
            return pd.to_datetime(f'{year}-{month:02d}-01')
            
        area_data.loc[:, 'date'] = area_data['年月'].apply(convert_to_date)
        area_data = area_data.sort_values('date')
        
        if graph_type == '線グラフ':
            fig.add_trace(go.Scatter(
                x=area_data['年月'],
                y=area_data['人口'],
                name=area,
                mode='lines+markers',
                hovertemplate='%{x}<br>%{y:,}人<extra></extra>'
            ))
        else:  # 棒グラフ
            fig.add_trace(go.Bar(
                x=area_data['年月'],
                y=area_data['人口'],
                name=area,
                hovertemplate='%{x}<br>%{y:,}人<extra></extra>'
            ))
    
    # グラフのレイアウト設定
    fig.update_layout(
        title='人口推移',
        xaxis_title='年月',
        yaxis_title='人口数',
        height=600,
        hovermode='x unified',
        yaxis=dict(
            title='人口数',
            tickformat=',d',
            range=[y_min, y_max] if y_scale == '固定' else None,
            autorange=True if y_scale == '自動' else False
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # グラフの表示
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning('地域を選択してください')

# 利用データについてのmarkdown
st.markdown("""
### 利用データについて
このアプリケーションで使われているデータは以下のオープンデータ（CC-BY-4.0ライセンス）を利用して作成しています

* [調布市の世帯と人口に関するデータ](https://www.city.chofu.lg.jp/030040/p017111.html)より調布市の町別の人口データをダウンロード
""") 