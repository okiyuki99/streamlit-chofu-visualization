import streamlit as st
import pandas as pd
from datetime import datetime

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
from utils.ui_components import display_metrics
from streamlit_folium import st_folium

# セッションステートの初期化
if 'map_data' not in st.session_state:
    st.session_state.map_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now().isoformat()

# ページが再読み込みされたときにタイムスタンプを更新
if st.session_state.get('page_reloaded', True):
    st.session_state.last_update = datetime.now().isoformat()
    st.session_state.page_reloaded = False

@st.cache_data(ttl=3600)
def load_cached_data(sheet_info):
    """データを読み込んでキャッシュする"""
    return load_data(sheet_info)

@st.cache_data(ttl=3600)
def load_cached_school_data(file_path, school_type):
    """学校データを読み込んでキャッシュする"""
    return load_school_data(file_path, school_type)

@st.cache_data(ttl=3600)
def get_previous_year_data(selected_sheet, sheet_names):
    """1年前のデータを取得"""
    try:
        # 現在の年月を取得
        current_year = int(selected_sheet.split(':')[1][1:].split('.')[0])  # "R6" から "6" を取得
        current_month = int(selected_sheet.split(':')[1].split('.')[1])    # "12.1" から "12" を取得
        
        # 1年前のシート情報を探す
        for display_name, sheet_info in sheet_names:
            year = int(sheet_info.split(':')[1][1:].split('.')[0])
            month = int(sheet_info.split(':')[1].split('.')[1])
            if year == current_year - 1 and month == current_month:
                return load_cached_data(sheet_info)
    except:
        pass
    return None

def run():
    """人口ヒートマップページを表示する"""
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
                index=0,
                key='year_selector'
            )
            # 表示用の名前から実際のシート情報を取得
            selected_sheet = sheet_infos[display_names.index(selected_display)]
        
        # 学校表示設定
        with st.expander('🏫 学校の表示設定', expanded=True):
            show_elementary_schools = st.checkbox(
                '小学校を表示 🔴',
                value=True,
                help='小学校の位置を赤色のマーカーで表示します',
                key='elementary_schools'
            )
            show_junior_high_schools = st.checkbox(
                '中学校を表示 🔵',
                value=True,
                help='中学校の位置を青色のマーカーで表示します',
                key='junior_high_schools'
            )
        
        # 駅の表示設定
        with st.expander('🚉 駅の表示設定', expanded=True):
            show_station = st.checkbox(
                '駅を表示 🟢',
                value=True,
                help='京王線の駅を緑色のマーカーで表示します',
                key='stations'
            )
    
    # データの読み込みと表示
    try:

        # データの読み込み
        merged_df = load_cached_data(selected_sheet)
        previous_df = get_previous_year_data(selected_sheet, sheet_names)
        
        # メトリクスの表示
        display_metrics(merged_df, previous_df)

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
                elementary_df = load_cached_school_data(SCHOOL_DATA_PATH, '小学校')
                add_school_markers(map, elementary_df, 'red')
            except Exception as e:
                st.error(f'小学校データの読み込みに失敗しました: {str(e)}')

        if show_junior_high_schools:
            try:
                junior_high_df = load_cached_school_data(SCHOOL_DATA_PATH, '中学校')
                add_school_markers(map, junior_high_df, 'blue')
            except Exception as e:
                st.error(f'中学校データの読み込みに失敗しました: {str(e)}')

        # 駅マーカーの追加
        if show_station:
            try:
                add_station_marker(map)
            except Exception as e:
                st.error(f'駅データの読み込みに失敗しました: {str(e)}')

        # 地図の表示
        st_folium(
            map,
            use_container_width=True,
            height=800,
            key=f'main_map_{selected_sheet}_{st.session_state.last_update}'
        )

    except Exception as e:
        st.error(f'データの表示に失敗しました: {str(e)}')
        st.write('エラーの詳細:', str(e))

    # 利用データについてのmarkdown
    st.markdown("""
    ### 利用データについて
    このアプリケーションで使われているデータは以下のオープンデータ（CC-BY-4.0ライセンス）を利用して作成しています

    * [調布市の世帯と人口に関するデータ](https://www.city.chofu.lg.jp/030040/p017111.html)より調布市の町別の人口データをダウンロード
    * [市立小・中学校に関するデータ](https://www.city.chofu.lg.jp/100010/p054122.html)より市立小・中学校一覧をダウンロード
    * [国勢調査町丁・字等別境界データセット](https://geoshape.ex.nii.ac.jp/ka/resource/)より調布市のTopoJSONファイルをダウンロード
    """)
