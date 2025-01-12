import folium
from folium import Map, Choropleth, GeoJson, Marker, DivIcon, Icon
from utils.map_styles import STYLE_FUNC, HIGHLIGHT_FUNC, TOOLTIP_STYLE, CENTER_LABEL_STYLE
from utils.constants import STATIONS

def create_base_map(lat: float, lon: float, zoom: int = 14) -> Map:
    """ベースとなる地図を作成"""
    return Map(
        location=(lat, lon),
        tiles="cartodbpositron",
        zoom_start=zoom
    )

def add_center_label(map_obj: Map, lat: float, lon: float, label: str) -> None:
    """中心地点のラベルを追加"""
    Marker(
        [lat, lon],
        icon=DivIcon(
            html=f'<div style="{CENTER_LABEL_STYLE}">{label}</div>',
            icon_size=(80, 20),
            icon_anchor=(40, 10)
        )
    ).add_to(map_obj)

def add_choropleth(map_obj: Map, data: dict, columns: list) -> None:
    """人口ヒートマップを追加"""
    choropleth = Choropleth(
        geo_data=data,
        data=data,
        columns=columns,
        key_on="feature.properties.S_NAME",
        fill_color='YlOrRd',
        nan_fill_color='darkgray',
        fill_opacity=0.8,
        nan_fill_opacity=0.8,
        line_opacity=0.2,
        legend_name="人口数",
    )
    choropleth.add_to(map_obj)

def add_tooltips(map_obj: Map, data: dict) -> None:
    """ツールチップを追加"""
    choropleth_info = GeoJson(
        data=data,
        style_function=STYLE_FUNC,
        highlight_function=HIGHLIGHT_FUNC,
        control=False,
        tooltip=folium.GeoJsonTooltip(
            fields=["住所", "人口数"],
            aliases=['住所: ', '人口数: '],
            labels=True,
            sticky=True,
            style=TOOLTIP_STYLE,
        )
    )
    map_obj.add_child(choropleth_info)
    map_obj.keep_in_front(choropleth_info)

def add_school_markers(map_obj: Map, school_df: dict, color: str) -> None:
    """学校のマーカーを追加"""
    for _, row in school_df.iterrows():
        Marker(
            location=[row['緯度'], row['経度']],
            popup=row['学校名'],
            icon=Icon(
                color=color,
                icon='graduation-cap',
                prefix='fa'
            ),
            tooltip=row['学校名']
        ).add_to(map_obj) 

def add_station_marker(map_obj: Map) -> None:
    """駅のマーカーを追加"""
    for station_name, coords in STATIONS.items():
        Marker(
            location=[coords['lat'], coords['lon']],
            popup=station_name,
            icon=Icon(
                color='green',
                icon='train',
                prefix='fa'
            ),
            tooltip=station_name
        ).add_to(map_obj) 

def add_area_labels(map_obj: Map, data: dict) -> None:
    """各エリアの中心にラベルを表示"""
    for idx, row in data.iterrows():
        centroid = row.geometry.centroid
        lat = centroid.y
        lon = centroid.x
        name = row['S_NAME']
        
        if lat and lon and name:
            Marker(
                [lat, lon],
                icon=DivIcon(
                    html=f'<div style="{CENTER_LABEL_STYLE}">{name}</div>',
                    icon_size=(60, 15),
                    icon_anchor=(30, 7)
                )
            ).add_to(map_obj) 