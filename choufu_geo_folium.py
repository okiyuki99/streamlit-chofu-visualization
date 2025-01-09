import streamlit as st
import json
import folium
from streamlit_folium import st_folium
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from data_loader import load_data
from data_loader import get_sheet_names

# Excelファイルのパスを指定してsheet名を取得
CHOUFU_POPULATION_DATA_FILE_PATH = 'data/chouchoubetu1201.xlsx'
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

# セレクトボックスの選択をもとにGeoDataFrameを取得
print(selected_sheet)
merged_df = load_data(file_path=CHOUFU_POPULATION_DATA_FILE_PATH, sheet_name=selected_sheet)

# mapの用意（佐須町二丁目を中心に）
lat = 35.660076
lon = 139.554033
map = folium.Map(
    location=(lat, lon),
    tiles="cartodbpositron",
    zoom_start=14
)

STYLE_FUNC = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
HIGHLIGHT_FUNC = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}

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

# 可視化実行
st_folium(map, use_container_width=True, height=800, returned_objects=[])

st.markdown("""
### 利用データについて
このアプリケーションで使われているデータは以下のオープンデータ（CC-BY-4.0ライセンス）を利用して作成しています

* [調布市の世帯と人口に関するデータ](https://www.city.chofu.lg.jp/030040/p017111.html)より調布市の町別の人口データをダウンロード
* [国勢調査町丁・字等別境界データセット](https://geoshape.ex.nii.ac.jp/ka/resource/)より調布市のTopoJSONファイルをダウンロード
""")
