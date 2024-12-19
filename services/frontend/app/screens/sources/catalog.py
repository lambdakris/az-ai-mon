import streamlit as st
import pandas as pd
import uuid
import json
from typing import Dict, List, Optional
from pg.sources.state import SourceManager, get_source_type_options

def source_catalog():
    st.header("Browse Sources")
    
    source_manager = SourceManager()
    sources = source_manager.sources
    
    if not sources:
        st.write("No sources found.")
        return
    
    # Create a DataFrame for easier browsing
    df = pd.DataFrame(sources)
    
    # Select columns to display
    display_columns = ['name', 'category', 'type', 'is_active']
    filtered_df = df[display_columns]
    
    '''
    add_source = st.button("Add Source")
    if add_source:
        st.switch_page("pg/sources/display.py")
    '''

    st.page_link("pg/sources/display.py", label="Add Source")

    edit_source = st.dataframe(
        filtered_df, 
        on_select="rerun",
        selection_mode="single-row"
    )

    '''  
    if edit_source:
       st.switch_page("pg/sources/display.py")
    '''

source_catalog()