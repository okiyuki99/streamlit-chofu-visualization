import streamlit as st
import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Union, List, Dict

# 定数定義
class DataPaths:
    """データファイルのパスを管理するクラス"""
    GEOJSON_PATH: str = 'data/r2ka13208.geojson'

class ColumnNames:
    """カラム名の定数を管理するクラス"""
    ADDRESS = '住所'
    MALE = '男'
    FEMALE = '女'
    POPULATION = '人口数'
    HOUSEHOLDS = '世帯数'
    SCHOOL_NAME = '学校名'
    LATITUDE = '緯度'
    LONGITUDE = '経度'

def load_data(file_path: Union[str, Path], sheet_name: Union[str, int] = 0) -> gpd.GeoDataFrame:
    """GeoJSONデータと人口データを読み込み、マージしたデータフレームを返す"""
    # GeoJSONから調布の市区町村データの読み込み
    jp_geo_df = gpd.read_file(DataPaths.GEOJSON_PATH)

    # Excelファイルから調布市の町別の人口データを読み込み
    chofu_df = read_choufu_population_excel_sheet(file_path, sheet_name)

    # GeoDataFrameとデータフレームをマージ
    merged_df = pd.merge(
        jp_geo_df,
        chofu_df,
        left_on='S_NAME',
        right_on=ColumnNames.ADDRESS,
        how='left'
    )
    return merged_df

def read_choufu_population_excel_sheet(
    file_path: Union[str, Path],
    sheet_name: Union[str, int] = 0
) -> pd.DataFrame:
    """調布市の町別の人口データを読み込む"""
    # Excelファイルの読み込み
    df = pd.read_excel(
        file_path,
        header=1,
        index_col=0,
        usecols=range(5),
        sheet_name=sheet_name
    )
    
    # データのクリーニング
    df = _clean_dataframe(df)
    
    # 数値データの変換
    df = _convert_numeric_columns(df)
    
    # 住所の漢数字変換
    df = _convert_address_numbers(df)
    
    return df

def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """データフレームの基本的なクリーニングを行う"""
    # 空白の削除
    df.columns = df.columns.str.strip()
    df.index = df.index.str.strip()
    
    # 無効なデータの削除
    df = df[~df.index.isnull()]
    df = df.iloc[:-1]  # 合計行の削除
    
    # インデックスをカラムに変換
    df = df.reset_index()
    
    # カラム名の設定
    df.columns = [
        ColumnNames.ADDRESS,
        ColumnNames.MALE,
        ColumnNames.FEMALE,
        ColumnNames.POPULATION,
        ColumnNames.HOUSEHOLDS
    ]
    
    return df

def _convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """数値カラムを適切な型に変換"""
    numeric_columns = [
        ColumnNames.MALE,
        ColumnNames.FEMALE,
        ColumnNames.POPULATION,
        ColumnNames.HOUSEHOLDS
    ]
    
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def _convert_address_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """住所の数字を漢数字に変換"""
    number_mapping = {
        '１': '一', '２': '二', '３': '三', '４': '四', '５': '五',
        '６': '六', '７': '七', '８': '八', '９': '九'
    }
    
    for arabic, kanji in number_mapping.items():
        df[ColumnNames.ADDRESS] = df[ColumnNames.ADDRESS].str.replace(
            arabic, kanji
        )
    
    return df

def get_sheet_names(file_path: Union[str, Path]) -> List[str]:
    """Excelファイルのシート名を取得する"""
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    sheet_names.reverse()
    return sheet_names

def load_school_data(file_path: str, school_type: str = None) -> pd.DataFrame:
    """学校データを読み込む"""
    if not Path(file_path).exists():
        raise FileNotFoundError(f'ファイルが見つかりません: {file_path}')
    
    # データの読み込みと前処理
    df = _load_and_process_school_data(file_path)
    
    # 学校種別でフィルタリング
    if school_type:
        df = df[df[ColumnNames.SCHOOL_NAME].str.contains(school_type, na=False)]
    
    # 欠損値のチェック
    _check_school_data_missing_values(df)
    
    return df

def _load_and_process_school_data(file_path: str) -> pd.DataFrame:
    """学校データの読み込みと前処理を行う"""
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    
    # カラム名の変換
    column_mapping = {
        '名称': ColumnNames.SCHOOL_NAME,
        '緯度（10進法）': ColumnNames.LATITUDE,
        '経度（10進法）': ColumnNames.LONGITUDE,
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    # カラムの存在確認
    required_columns = [
        ColumnNames.SCHOOL_NAME,
        ColumnNames.LATITUDE,
        ColumnNames.LONGITUDE
    ]
    _validate_required_columns(df, required_columns)
    
    # 緯度経度を数値型に変換
    df[ColumnNames.LATITUDE] = pd.to_numeric(df[ColumnNames.LATITUDE], errors='coerce')
    df[ColumnNames.LONGITUDE] = pd.to_numeric(df[ColumnNames.LONGITUDE], errors='coerce')
    
    return df

def _validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
    """必要なカラムが存在するか確認"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f'必要なカラムが不足しています: {", ".join(missing_columns)}\n'
            f'利用可能なカラム: {", ".join(df.columns)}'
        )

def _check_school_data_missing_values(df: pd.DataFrame) -> None:
    """学校データの欠損値をチェック"""
    check_columns = [
        ColumnNames.SCHOOL_NAME,
        ColumnNames.LATITUDE,
        ColumnNames.LONGITUDE
    ]
    if df[check_columns].isna().any().any():
        st.warning('一部の学校データに欠損値が含まれています')
