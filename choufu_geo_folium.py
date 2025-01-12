import streamlit as st
import json
import folium
from streamlit_folium import st_folium
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from data_loader import load_data
from data_loader import get_sheet_names
from data_loader import load_school_data
from pathlib import Path

STYLE_FUNC = lambda x: {
  'fillColor': '#ffffff', 
  'color':'#000000', 
  'fillOpacity': 0.1, 
  'weight': 0.1
}
HIGHLIGHT_FUNC = lambda x: {
  'fillColor': '#000000', 
  'color':'#000000', 
  'fillOpacity': 0.50, 
  'weight': 0.1
}

# Excelファイルのパスを指定してsheet名を取得
CHOUFU_POPULATION_DATA_FILE_PATH = 'data/choufushi_open_data_chouchoubetu1201.xlsx'
sheet_names = get_sheet_names(CHOUFU_POPULATION_DATA_FILE_PATH)

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

# Streamlitのセレクトボックスでシート名を選択
selected_sheet = st.selectbox(
  "表示する年代(シート)を選択してください",
   sheet_names,
   index=0
)

merged_df = load_data(file_path=CHOUFU_POPULATION_DATA_FILE_PATH, sheet_name=selected_sheet)

# mapの用意（佐須町二丁目を中心に）
lat = 35.660076
lon = 139.554033
map = folium.Map(
  location=(lat, lon),
  tiles="cartodbpositron",
  zoom_start=14
)

# 中心地点のラベルを追加（DivIconを使用）
folium.map.Marker(
    [lat, lon],
    icon=folium.DivIcon(
        html='<div style="font-size: 10px; color: #999999; text-align: center;">佐須町二丁目</div>',
        icon_size=(80, 20),
        icon_anchor=(40, 10)
    )
).add_to(map)

# 可視化設定
choropleth = folium.Choropleth(
  geo_data=merged_df,
  data=merged_df,
  columns=["住所", "人口数"],
  key_on="feature.properties.S_NAME",
  fill_color='YlOrRd',
  nan_fill_color='darkgray',
  fill_opacity=0.8,
  nan_fill_opacity=0.8,
  line_opacity=0.2,
  legend_name="人口数",
)
choropleth.add_to(map)

# ツールチップの可視化
choropleth_info = folium.GeoJson(
  data=merged_df,
  style_function=STYLE_FUNC,
  highlight_function=HIGHLIGHT_FUNC,
  control=False,
  tooltip=folium.GeoJsonTooltip(
    fields=["住所", "人口数"],
    aliases=['住所: ', '人口数: '],
    labels=True,
    sticky=True,
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"), 
  )
)
map.add_child(choropleth_info)
map.keep_in_front(choropleth_info)

# 定数定義部分に追加（HIGHLIGHT_FUNCの後あたり）
SCHOOL_DATA_PATH = Path('data/choufushi_open_data_school.xls')

# チェックボックスを横に並べて配置
col1, col2 = st.columns(2)
with col1:
    show_elementary_schools = st.checkbox('小学校の位置を表示', value=False)
with col2:
    show_junior_high_schools = st.checkbox('中学校の位置を表示', value=False)

# 小学校のマーカー追加
if show_elementary_schools:
    try:
        elementary_df = load_school_data(SCHOOL_DATA_PATH, school_type='小学校')
        for _, row in elementary_df.iterrows():
            folium.Marker(
                location=[row['緯度'], row['経度']],
                popup=row['学校名'],
                icon=folium.Icon(
                    color='red',
                    icon='graduation-cap',  # 学校を表すアイコン
                    prefix='fa'  # Font Awesomeを使用することを指定
                ),
                tooltip=row['学校名']
            ).add_to(map)
    except Exception as e:
        st.error(f'小学校データの読み込みに失敗しました: {str(e)}')

# 中学校のマーカー追加
if show_junior_high_schools:
    try:
        junior_high_df = load_school_data(SCHOOL_DATA_PATH, school_type='中学校')
        for _, row in junior_high_df.iterrows():
            folium.Marker(
                location=[row['緯度'], row['経度']],
                popup=row['学校名'],
                icon=folium.Icon(
                    color='blue',
                    icon='graduation-cap',  # 学校を表すアイコン
                    prefix='fa'  # Font Awesomeを使用することを指定
                ),
                tooltip=row['学校名']
            ).add_to(map)
    except Exception as e:
        st.error(f'中学校データの読み込みに失敗しました: {str(e)}')

# 可視化実行
st_folium(map, use_container_width=True, height=800, returned_objects=[])

st.markdown("""
### 利用データについて
このアプリケーションで使われているデータは以下のオープンデータ（CC-BY-4.0ライセンス）を利用して作成しています

* [調布市の世帯と人口に関するデータ](https://www.city.chofu.lg.jp/030040/p017111.html)より調布市の町別の人口データをダウンロード
* [市立小・中学校に関するデータ](https://www.city.chofu.lg.jp/100010/p054122.html)より市立小・中学校一覧をダウンロード
* [国勢調査町丁・字等別境界データセット](https://geoshape.ex.nii.ac.jp/ka/resource/)より調布市のTopoJSONファイルをダウンロード
""")
