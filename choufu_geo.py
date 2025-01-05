import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# 日本地図データの読み込み (GeoJSON形式を想定)
jp_geo = gpd.read_file('r2ka13208.topojson')
#jp_geo = gpd.read_file('chofu.geojson')
#jp_geo = gpd.read_file('13208__9_r_2024.geojson')
# print(jp_geo)

# CSVファイルから都道府県別データを読み込み
chofu_df = pd.read_csv('chofu_jinkou_data.csv', usecols=range(3))
chofu_df['住所'] = chofu_df['住所'].str.replace('１', '一')
chofu_df['住所'] = chofu_df['住所'].str.replace('２', '二')
chofu_df['住所'] = chofu_df['住所'].str.replace('３', '三')
chofu_df['住所'] = chofu_df['住所'].str.replace('４', '四')
chofu_df['住所'] = chofu_df['住所'].str.replace('５', '五')
chofu_df['住所'] = chofu_df['住所'].str.replace('６', '六')
chofu_df['住所'] = chofu_df['住所'].str.replace('７', '七')
chofu_df['住所'] = chofu_df['住所'].str.replace('８', '八')
chofu_df['住所'] = chofu_df['住所'].str.replace('９', '九')
chofu_df['住所'] = chofu_df['住所'].str.strip()
chofu_df['人口数'] = pd.to_numeric(chofu_df['人口数'], errors='coerce')
chofu_df['世帯数'] = pd.to_numeric(chofu_df['世帯数'], errors='coerce')
# print(chofu_df)

# GeoDataFrameとデータフレームをマージ
# ここから
merged_df = pd.merge(jp_geo, chofu_df, left_on='S_NAME', right_on='住所', how='left')
#print(merged_df.dtypes)

# ランダムな数値データを生成
# np.random.seed(42)  # 再現性のためシードを設定
# jp_geo['random_value'] = np.random.rand(len(jp_geo))

# Streamlit アプリケーション
st.title('都道府県別ヒートマップ')

# スライダーで数値の範囲を調整
max_value = merged_df['人口数'].max()
vmin, vmax = st.slider('値の範囲', 0.0, max_value, (0.0, max_value))

# Matplotlib でヒートマップを作成
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
merged_df.plot(column='人口数', cmap='coolwarm', linewidth=0.5, ax=ax, vmin=vmin, vmax=vmax, legend=True)
ax.set_axis_off()

# Streamlit に表示
st.pyplot(fig)
