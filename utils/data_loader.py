import pandas as pd
import geopandas as gpd
# pd.set_option('display.max_rows', None)

def load_data():
    """GeoJSONデータと人口データを読み込み、マージしたデータフレームを返す"""

    # GeoJSONから調布の市区町村データの読み込み
    jp_geo = gpd.read_file('data/r2ka13208.geojson')

    # CSVファイルから都道府県別データを読み込み
    # chofu_df = pd.read_csv('data/chofu_jinkou_data.csv', usecols=range(3))
    # chofu_df['住所'] = chofu_df['住所'].str.replace('１', '一')
    # chofu_df['住所'] = chofu_df['住所'].str.replace('２', '二')
    # chofu_df['住所'] = chofu_df['住所'].str.replace('３', '三')
    # chofu_df['住所'] = chofu_df['住所'].str.replace('４', '四')
    # chofu_df['住所'] = chofu_df['住所'].str.replace('５', '五')
    # chofu_df['住所'] = chofu_df['住所'].str.replace('６', '六')
    # chofu_df['住所'] = chofu_df['住所'].str.replace('７', '七')
    # chofu_df['住所'] = chofu_df['住所'].str.replace('８', '八')
    # chofu_df['住所'] = chofu_df['住所'].str.replace('９', '九')
    # chofu_df['住所'] = chofu_df['住所'].str.strip()
    # chofu_df['人口数'] = pd.to_numeric(chofu_df['人口数'], errors='coerce')
    # chofu_df['世帯数'] = pd.to_numeric(chofu_df['世帯数'], errors='coerce')
    
    # Excelファイルから調布市の町別の人口データを読み込み
    chofu_df = read_choufu_population_excel_sheet(file_path='data/chouchoubetu1201.xlsx', sheet_name='R6.12.1')

    # GeoDataFrameとデータフレームをマージ
    merged_df = pd.merge(jp_geo, chofu_df, left_on='S_NAME', right_on='住所', how='left')
    return merged_df

def read_choufu_population_excel_sheet(file_path, sheet_name=0):
    """
    調布市の世帯と人口に関するデータより調布市の町別の人口データのエクセルファイルのシートを読み込み、pandas DataFrameとして返す関数
    https://www.city.chofu.lg.jp/030040/p017111.html
    
    Args:
        file_path (str): エクセルファイルのパス
        sheet_name (int or str, optional): シート名またはシート番号. Defaults to 0.

    Returns:
        pandas.DataFrame: 読み込んだデータフレーム
    """

    # headerを2行目、indexを1列目に設定して読み込み
    df = pd.read_excel(file_path, header=1, index_col=0, usecols=range(5), sheet_name=sheet_name)

    # 不要な空白を削除
    df.columns = df.columns.str.strip()
    df.index = df.index.str.strip()

    # indexが"NaN"な行を削除
    df = df[~df.index.isnull()]

    # 最終行は合計の行になってるので削除
    df = df.iloc[:-1]

    # 数値に変換
    df['男'] = pd.to_numeric(df['男'], errors='coerce')
    df['女'] = pd.to_numeric(df['女'], errors='coerce')
    df['人口数'] = pd.to_numeric(df['人口数'], errors='coerce')
    df['世帯数'] = pd.to_numeric(df['世帯数'], errors='coerce')

    # indexをカラムに戻す
    df = df.reset_index()

    # カラム名を変更
    df.columns = ['住所', '男', '女', '人口数', '世帯数']

    # 漢数字に直す
    df['住所'] = df['住所'].str.replace('１', '一')
    df['住所'] = df['住所'].str.replace('２', '二')
    df['住所'] = df['住所'].str.replace('３', '三')
    df['住所'] = df['住所'].str.replace('４', '四')
    df['住所'] = df['住所'].str.replace('５', '五')
    df['住所'] = df['住所'].str.replace('６', '六')
    df['住所'] = df['住所'].str.replace('７', '七')
    df['住所'] = df['住所'].str.replace('８', '八')
    df['住所'] = df['住所'].str.replace('９', '九')

    return df
