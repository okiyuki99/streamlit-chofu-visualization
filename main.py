import streamlit as st
from components import population_heatmap, population_time_series

# ページの設定
st.set_page_config(
    page_title='調布市人口可視化',
    page_icon='🗾',
    layout='wide'
)

# ブラウザキャッシュの無効化
st.markdown('''
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
''', unsafe_allow_html=True)

# ナビゲーションの設定
current_page = st.navigation([
    st.Page(population_heatmap.run, title='人口ヒートマップ', url_path='heatmap'),
    st.Page(population_time_series.run, title='人口推移グラフ', url_path='time_series'),
])

current_page.run()
