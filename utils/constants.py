from pathlib import Path

# データファイルのパスを更新
POPULATION_DATA_FILES = {
    'R6': 'data/choufushi_open_data_chouchoubetu1201.xlsx',  # 令和6年のデータ
    'R5': 'data/choufushi_open_data_r5chouchoubetu.xlsx',    # 令和5年のデータ
    'R4': 'data/choufushi_open_data_r4chouchoubetu.xlsx'     # 令和4年のデータを追加
}
SCHOOL_DATA_PATH = Path('data/choufushi_open_data_school.xls')

# 地図の中心座標（佐須町二丁目）
CENTER_LAT = 35.660076
CENTER_LON = 139.554033 

# 駅のマーカーの座標
STATIONS = {
    '仙川駅': {'lat': 35.662307, 'lon': 139.584897},
    'つつじヶ丘駅': {'lat': 35.6579842, 'lon': 139.5750124},
    '柴崎駅': {'lat': 35.6540817, 'lon': 139.5666085},
    '国領駅': {'lat': 35.6501355, 'lon': 139.5583464},
    '布田駅': {'lat': 35.6498499, 'lon': 139.5518261},
    '調布駅': {'lat': 35.651788, 'lon': 139.5447823},
    '西調布駅': {'lat': 35.6570844, 'lon': 139.5300797},
    '飛田給駅': {'lat': 35.6600815, 'lon': 139.5235242}
} 