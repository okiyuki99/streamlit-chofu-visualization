import streamlit as st
import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Union, List, Dict
from utils.constants import POPULATION_DATA_FILES

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

def load_data(sheet_info: str) -> gpd.GeoDataFrame:
    """GeoJSONデータと人口データを読み込み、マージしたデータフレームを返す
    
    Args:
        sheet_info: "年度:シート名" の形式の文字列（例: "R6:R6.12.1"）
    """
    # ファイル識別子とシート名を分離
    year, sheet_name = sheet_info.split(':')
    file_path = POPULATION_DATA_FILES[year]
    
    # R4ファイルのR3.5.1シートをR4.5.1として扱う
    if year == 'R4' and sheet_name == 'R4.5.1':
        sheet_name = 'R3.5.1'
    
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
    # シート名から古いフォーマットかどうかを判定
    is_old_format = False
    if isinstance(sheet_name, str):
        try:
            year = int(sheet_name[1:].split('.')[0])  # "R3" から "3" を取得
            month = int(sheet_name.split('.')[1])     # "3.1" から "3" を取得
            # R6.3.1までは古いフォーマット
            if year < 6 or (year == 6 and month <= 3):
                is_old_format = True
        except:
            pass
    
    try:
        if is_old_format:
            # 古いフォーマット: 必要な列のみを明示的に指定
            # B列（インデックス1）を除外し、A列とC列以降を使用
            df = pd.read_excel(
                file_path,
                header=1,
                sheet_name=sheet_name,
                usecols=[0, 2, 3, 4, 5]  # A列とC列以降を使用
            )
            # 最初の列を住所列として設定し、NULLを削除してからインデックスに設定
            df = df.rename(columns={df.columns[0]: ColumnNames.ADDRESS})
            df = df[df[ColumnNames.ADDRESS].notna()]  # NULLの行を削除
            df = df.set_index(ColumnNames.ADDRESS)
        else:
            # 新しいフォーマット: 従来通り
            df = pd.read_excel(
                file_path,
                header=1,
                index_col=0,
                usecols=[0, 1, 2, 3, 4],
                sheet_name=sheet_name
            )

        # データのクリーニング以降は変更なし
        df = _clean_dataframe(df)
        df = _convert_numeric_columns(df)
        df = _convert_address_numbers(df)
        
        return df
        
    except Exception as e:
        st.error(f'データの読み込みに失敗しました: {str(e)}')
        st.error(f'ファイル: {file_path}, シート: {sheet_name}, フォーマット: {"旧" if is_old_format else "新"}')
        raise e

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

def convert_to_readable_date(sheet_name: str) -> str:
    """シート名を読みやすい形式に変換（例：R6.12.1 → 令和6年12月）"""
    try:
        if not sheet_name.startswith('R'):
            return sheet_name
        
        # R6.12.1 形式を分解
        year = sheet_name[1:].split('.')[0]
        month = sheet_name.split('.')[1]
        
        # 全角数字を半角数字に変換するマッピング
        zen_to_han = str.maketrans('０１２３４５６７８９', '0123456789')
        month = month.translate(zen_to_han)
        
        return f'令和{year}年{month}月'
    except:
        return sheet_name

def get_all_sheet_names() -> List[tuple[str, str]]:
    """全ての利用可能なシート名を取得する
    
    Returns:
        List[tuple[str, str]]: (表示用シート名, 実際のシート名とファイルの組み合わせ)のリスト
    """
    all_sheets = []
    
    for year, file_path in POPULATION_DATA_FILES.items():
        try:
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            
            # (表示用シート名, "ファイル識別子:シート名")の形式で保存
            for name in sheet_names:
                # R4ファイルのR3.5.1を表示上R4.5.1として扱う
                display_name = 'R4.5.1' if (year == 'R4' and name == 'R3.5.1') else name
                
                # R4.3.1より前のデータは除外（データのフォーマットが違うため
                try:
                    sheet_year = int(display_name[1:].split('.')[0])
                    sheet_month = int(display_name.split('.')[1])
                    
                    if sheet_year < 4 or (sheet_year == 4 and sheet_month <= 3):
                        continue
                    
                    all_sheets.append((
                        convert_to_readable_date(display_name),
                        f"{year}:{display_name}"
                    ))
                except:
                    # 日付の解析に失敗した場合はスキップ
                    continue
                
        except Exception as e:
            st.error(f'{file_path}の読み込みに失敗しました: {str(e)}')
    
    # シート名から年月を抽出してソート用のキーを作成
    def sort_key(sheet_tuple):
        sheet_name = sheet_tuple[1].split(':')[1]  # "R6:R6.12.1" から "R6.12.1" を取得
        try:
            year = int(sheet_name[1:].split('.')[0])  # "6" を取得
            month = int(sheet_name.split('.')[1])     # "12" を取得
            return (-year, -month)  # 降順にするためにマイナスをつける
        except:
            return (0, 0)  # 解析できない場合は最後に
    
    # 年月の降順でソート
    all_sheets.sort(key=sort_key)
    return all_sheets

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
