import pandas as pd
import geopandas as gpd

def load_data():
    """GeoJSONデータと人口データを読み込み、マージしたデータフレームを返す"""

    # GeoJSONから調布の市区町村データの読み込み
    jp_geo = gpd.read_file('data/r2ka13208.geojson')

    # CSVファイルから都道府県別データを読み込み
    chofu_df = pd.read_csv('data/chofu_jinkou_data.csv', usecols=range(3))
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

    # GeoDataFrameとデータフレームをマージ
    merged_df = pd.merge(jp_geo, chofu_df, left_on='S_NAME', right_on='住所', how='left')
    return merged_df

