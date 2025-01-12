import streamlit as st

from utils.data_loader import (
    load_data, get_sheet_names, load_school_data
)
from utils.constants import (
    CHOUFU_POPULATION_DATA_FILE_PATH, SCHOOL_DATA_PATH,
    CENTER_LAT, CENTER_LON
)
from utils.map_components import (
    create_base_map, add_center_label, add_choropleth,
    add_tooltips, add_school_markers
)
from streamlit_folium import st_folium

# Streamlitのセットアップ
st.set_page_config(
    page_title="調布市の人口ヒートマップ",
    page_icon="🗾",
    layout="wide"
)

st.markdown("""
# 調布市の人口ヒートマップ

オープンデータをもとにした調布市の市区町村別の人口をヒートマップで可視化したアプリケーションです
""")

# シート名の取得と選択
sheet_names = get_sheet_names(CHOUFU_POPULATION_DATA_FILE_PATH)
selected_sheet = st.selectbox(
    "表示する年代(シート)を選択してください",
    sheet_names,
    index=0
)

# データの読み込みと地図の作成
merged_df = load_data(file_path=CHOUFU_POPULATION_DATA_FILE_PATH, sheet_name=selected_sheet)
map = create_base_map(CENTER_LAT, CENTER_LON)

# 地図コンポーネントの追加
add_center_label(map, CENTER_LAT, CENTER_LON, '佐須町二丁目')
add_choropleth(map, merged_df, ["住所", "人口数"])
add_tooltips(map, merged_df)

# 学校表示のチェックボックス
col1, col2 = st.columns(2)
with col1:
    show_elementary_schools = st.checkbox('小学校の位置を表示', value=False)
with col2:
    show_junior_high_schools = st.checkbox('中学校の位置を表示', value=False)

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

# 地図の表示
st_folium(map, use_container_width=True, height=800, returned_objects=[])

# 利用データについてのmarkdown
st.markdown("""
### 利用データについて
このアプリケーションで使われているデータは以下のオープンデータ（CC-BY-4.0ライセンス）を利用して作成しています

* [調布市の世帯と人口に関するデータ](https://www.city.chofu.lg.jp/030040/p017111.html)より調布市の町別の人口データをダウンロード
* [市立小・中学校に関するデータ](https://www.city.chofu.lg.jp/100010/p054122.html)より市立小・中学校一覧をダウンロード
* [国勢調査町丁・字等別境界データセット](https://geoshape.ex.nii.ac.jp/ka/resource/)より調布市のTopoJSONファイルをダウンロード
""")
