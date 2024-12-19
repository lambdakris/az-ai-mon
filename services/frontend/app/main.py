import streamlit as st
from screens import screens

pg = st.navigation(
    pages=[
        st.Page(screens.chats, url_path="chats"),
        st.Page(screens.source_catalog, url_path="source-catalog"),
        st.Page(screens.source_display, url_path="source-display"),
    ], 
    position="hidden"
)

pg.run()