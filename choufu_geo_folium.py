import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

from utils.data_loader import (
    load_data, load_school_data, get_all_sheet_names,
    ColumnNames
)
from utils.constants import (
    POPULATION_DATA_FILES, SCHOOL_DATA_PATH,
    CENTER_LAT, CENTER_LON, STATIONS
)
from utils.map_components import (
    create_base_map, add_center_label, add_choropleth,
    add_tooltips, add_school_markers, add_station_marker, add_area_labels
)
from streamlit_folium import st_folium

# Streamlitのセットアップ
st.set_page_config(
    page_title="調布市の人口数の可視化サイト",
    page_icon="🗾",
    layout="wide"
)

# キャッシュを無効にするヘッダーを設定
st.markdown("""
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
""", unsafe_allow_html=True)

st.markdown("""
# 調布市の人口ヒートマップ

オープンデータをもとにした調布市の市区町村別の人口をヒートマップで可視化しています
""")

# 設定パネルの作成
with st.sidebar:
    st.header('📊 表示設定')
    
    # 年代選択
    with st.expander('📅 年代の選択', expanded=True):
        sheet_names = get_all_sheet_names()
        display_names, sheet_infos = zip(*sheet_names)
        
        selected_display = st.selectbox(
            "表示する年代を選択してください",
            display_names,
            index=0
        )
        # 表示用の名前から実際のシート情報を取得
        selected_sheet = sheet_infos[display_names.index(selected_display)]
    
    # 学校表示設定
    with st.expander('🏫 学校の表示設定', expanded=True):
        show_elementary_schools = st.checkbox(
            '小学校を表示 🔴',
            value=True,
            help='小学校の位置を赤色のマーカーで表示します'
        )
        show_junior_high_schools = st.checkbox(
            '中学校を表示 🔵',
            value=True,
            help='中学校の位置を青色のマーカーで表示します'
        )
    
    # 駅の表示設定
    with st.expander('🚉 駅の表示設定', expanded=True):
        show_station = st.checkbox(
            '駅を表示 🟢',
            value=True,
            help='京王線の駅を緑色のマーカーで表示します'
        )

# データの読み込みと地図の作成
merged_df = load_data(selected_sheet)

# 1年前のデータを取得
try:
    # 現在の年月を取得
    current_year = int(selected_sheet.split(':')[1][1:].split('.')[0])  # "R6" から "6" を取得
    current_month = int(selected_sheet.split(':')[1].split('.')[1])    # "12.1" から "12" を取得
    
    # 1年前のシート情報を探す
    previous_year_info = None
    for display_name, sheet_info in sheet_names:
        year = int(sheet_info.split(':')[1][1:].split('.')[0])
        month = int(sheet_info.split(':')[1].split('.')[1])
        if year == current_year - 1 and month == current_month:
            previous_year_info = sheet_info
            break
    
    # 1年前のデータを読み込む
    if previous_year_info:
        previous_df = load_data(previous_year_info)
    else:
        previous_df = None
except:
    previous_df = None

# メトリクスの計算と表示
col1, col2, col3, col4 = st.columns(4)

# 人口総数
total_population = merged_df[ColumnNames.POPULATION].sum()
previous_population = previous_df[ColumnNames.POPULATION].sum() if previous_df is not None else None
with col1:
    st.metric(
        label="総人口",
        value=f"{int(total_population):,}人",
        delta=f"1年前から{int(total_population - previous_population):+,}人" if previous_population is not None else None
    )

# 世帯総数
total_households = merged_df[ColumnNames.HOUSEHOLDS].sum()
previous_households = previous_df[ColumnNames.HOUSEHOLDS].sum() if previous_df is not None else None
with col2:
    st.metric(
        label="総世帯数",
        value=f"{int(total_households):,}世帯",
        delta=f"1年前から{int(total_households - previous_households):+,}世帯" if previous_households is not None else None
    )

# 男性総数
total_male = merged_df[ColumnNames.MALE].sum()
previous_male = previous_df[ColumnNames.MALE].sum() if previous_df is not None else None
with col3:
    st.metric(
        label="男性人口",
        value=f"{int(total_male):,}人",
        delta=f"1年前から{int(total_male - previous_male):+,}人" if previous_male is not None else None
    )

# 女性総数
total_female = merged_df[ColumnNames.FEMALE].sum()
previous_female = previous_df[ColumnNames.FEMALE].sum() if previous_df is not None else None
with col4:
    st.metric(
        label="女性人口",
        value=f"{int(total_female):,}人",
        delta=f"1年前から{int(total_female - previous_female):+,}人" if previous_female is not None else None
    )

# 地図の作成と表示
map = create_base_map(CENTER_LAT, CENTER_LON)

# 地図コンポーネントの追加
add_center_label(map, CENTER_LAT, CENTER_LON, '佐須町二丁目')
add_choropleth(map, merged_df, ["住所", "人口数"])
add_tooltips(map, merged_df)
add_area_labels(map, merged_df)

# 学校マーカーの追加
if show_elementary_schools:
    try:
        elementary_df = load_school_data(SCHOOL_DATA_PATH, school_type='小学校')
        add_school_markers(map, elementary_df, 'red')
    except Exception as e:
        st.error(f'小学校データの読み込みに失敗しました: {str(e)}')

if show_junior_high_schools:
    try:
        junior_high_df = load_school_data(SCHOOL_DATA_PATH, school_type='中学校')
        add_school_markers(map, junior_high_df, 'blue')
    except Exception as e:
        st.error(f'中学校データの読み込みに失敗しました: {str(e)}')

# 駅マーカーの追加
if show_station:
    add_station_marker(map)

# 地図の表示
st_folium(map, use_container_width=True, height=800, returned_objects=[])

# 時系列データの準備
def get_population_history():
    """令和4年4月から最新までの人口データを取得"""
    history_data = []
    
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

# 地域選択のマルチセレクト
st.markdown("""
# 人口推移グラフ

オープンデータをもとにした調布市の市区町村別の人口推移を時系列グラフで可視化しています
""")

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
graph_type = st.radio(
    'グラフの種類を選択',
    ['線グラフ', '棒グラフ'],
    horizontal=True
)

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
            autorange=True  # 縦軸を動的に設定
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
* [市立小・中学校に関するデータ](https://www.city.chofu.lg.jp/100010/p054122.html)より市立小・中学校一覧をダウンロード
* [国勢調査町丁・字等別境界データセット](https://geoshape.ex.nii.ac.jp/ka/resource/)より調布市のTopoJSONファイルをダウンロード
""")
