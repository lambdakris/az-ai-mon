import streamlit as st
import uuid
import json
from typing import Dict, List, Optional
from pg.sources.state import SourceManager, get_source_type_options

def source_display():
    source_id = st.session_state.source_id
    
    st.header("Source Display")
    
    # Source type selection
    source_types = get_source_type_options()
    category = st.selectbox("Source Category", list(source_types.keys()))
    source_type = st.selectbox("Source Type", source_types[category])
    
    name = st.text_input("Source Name")
    description = st.text_area("Source Description")
    
    # Conditional fields based on source type
    additional_config = {}
    
    if category == 'Provider':
        if source_type == 'Retrieval API':
            additional_config['endpoint'] = st.text_input("API Endpoint")
            additional_config['auth_type'] = st.selectbox("Authentication Type", 
                ["None", "API Key", "OAuth", "Basic"])
        
        elif source_type.startswith('Generation API'):
            additional_config['model'] = st.text_input("Model Name")
            additional_config['max_tokens'] = st.number_input("Max Tokens", min_value=1, value=1024)
    
    elif category == 'Repository':
        if source_type.startswith('DB Pull'):
            additional_config['connection_string'] = st.text_input("Connection String")
            additional_config['query'] = st.text_area("Query/Collection")
        
        elif source_type.startswith('API Pull'):
            additional_config['base_url'] = st.text_input("Base URL")
            additional_config['query_type'] = source_type.split()[-1]
        
        elif source_type == 'Web Crawl':
            additional_config['start_url'] = st.text_input("Starting URL")
            additional_config['depth'] = st.number_input("Crawl Depth", min_value=1, max_value=5, value=2)
        
        elif source_type == 'File Share':
            additional_config['file_path'] = st.text_input("File Path/Directory")
        
        elif source_type == 'Data Stream':
            additional_config['stream_type'] = st.selectbox("Stream Type", 
                ["Kafka", "Azure Event Hubs"])

    additional_config['is_active'] = st.checkbox("Active", value=True)

    # Submit button
    if st.button("Save"):
        source_data = {
            "name": name,
            "description": description,
            "category": category,
            "type": source_type,
            **additional_config
        }
        
        source_manager = SourceManager()

        if source_id:
            source_id = source_manager.update_source(source_data)
            st.success("Source updated successfully")
        else:
            source_id = source_manager.create_source(source_data)
            st.success("Source created successfully")

source_display()