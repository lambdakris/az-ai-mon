import streamlit as st
import uuid
import json
from typing import Dict, List, Optional

class SourceManager:
    def __init__(self, storage_file='sources.json'):
        self.storage_file = storage_file
        self.sources = self.load_sources()

    def load_sources(self) -> List[Dict]:
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_sources(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.sources, f, indent=2)

    def create_source(self, source_data: Dict):
        # Add a unique identifier
        source_data['id'] = str(uuid.uuid4())
        self.sources.append(source_data)
        self.save_sources()
        return source_data['id']

    def update_source(self, source_id: str, updated_data: Dict):
        for i, source in enumerate(self.sources):
            if source['id'] == source_id:
                # Preserve the original ID
                updated_data['id'] = source_id
                self.sources[i] = updated_data
                self.save_sources()
                return True
        return False

    def delete_source(self, source_id: str):
        self.sources = [source for source in self.sources if source['id'] != source_id]
        self.save_sources()

    def get_source(self, source_id: str) -> Optional[Dict]:
        return next((source for source in self.sources if source['id'] == source_id), None)

def get_source_type_options():
    return {
        'Source Service': [
            'Retrieval API',
            'Generation API (Grounded)',
            'Generation API (Ungrounded)'
        ],
        'Source Repository': [
            'DB Pull (SQL)',
            'DB Pull (NoSQL)', 
            'API Pull (HTTP)',
            'API Pull (GraphQL)', 
            'Web Crawl',
            'File Share',
            'Data Stream'
        ]
    }

def create_source_form():
    st.header("Create New Source")
    
    # Source type selection
    source_types = get_source_type_options()
    category = st.selectbox("Source Category", list(source_types.keys()))
    source_type = st.selectbox("Source Type", source_types[category])
    
    # Common fields
    name = st.text_input("Source Name")
    description = st.text_area("Description")
    
    # Conditional fields based on source type
    additional_config = {}
    
    if category == 'Source Service':
        if source_type == 'Retrieval API':
            additional_config['endpoint'] = st.text_input("API Endpoint")
            additional_config['auth_type'] = st.selectbox("Authentication Type", 
                ["None", "API Key", "OAuth", "Basic"])
        
        elif source_type.startswith('Generation API'):
            additional_config['model'] = st.text_input("Model Name")
            additional_config['max_tokens'] = st.number_input("Max Tokens", min_value=1, value=1024)
    
    elif category == 'Source Repository':
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
                ["Kafka", "RabbitMQ", "AWS Kinesis", "Azure Event Hubs"])

    # Sensitivity and access controls
    additional_config['is_active'] = st.checkbox("Active", value=True)
    additional_config['access_level'] = st.selectbox("Access Level", 
        ["Public", "Private", "Restricted"])

    # Submit button
    if st.button("Create Source"):
        if name and source_type:
            source_data = {
                "name": name,
                "description": description,
                "category": category,
                "type": source_type,
                **additional_config
            }
            
            source_manager = SourceManager()
            new_source_id = source_manager.create_source(source_data)
            st.success(f"Source created successfully with ID: {new_source_id}")
        else:
            st.error("Please provide a name and select a source type")

def browse_sources():
    st.header("Browse Sources")
    
    source_manager = SourceManager()
    sources = source_manager.sources
    
    if not sources:
        st.write("No sources found.")
        return
    
    # Create a DataFrame for easier browsing
    import pandas as pd
    df = pd.DataFrame(sources)
    
    # Select columns to display
    display_columns = ['name', 'category', 'type', 'is_active', 'access_level']
    filtered_df = df[display_columns]
    
    # Interactive table
    edited_df = st.data_editor(
        filtered_df, 
        num_rows="dynamic",
        column_config={
            "is_active": st.column_config.CheckboxColumn(
                "Active",
                help="Whether the source is currently active"
            )
        }
    )
    
    # Detailed source view and actions
    selected_rows = st.multiselect("Select sources for actions", df['id'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Edit Selected Sources"):
            for source_id in selected_rows:
                source = source_manager.get_source(source_id)
                if source:
                    st.subheader(f"Editing: {source['name']}")
                    edit_source(source)
    
    with col2:
        if st.button("Delete Selected Sources"):
            for source_id in selected_rows:
                source_manager.delete_source(source_id)
            st.experimental_rerun()

def edit_source(source):
    st.header(f"Edit Source: {source['name']}")
    
    # Populate form with existing source data
    name = st.text_input("Source Name", source.get('name', ''))
    description = st.text_area("Description", source.get('description', ''))
    
    # Recreate the form similar to create_source_form but with pre-filled data
    source_types = get_source_type_options()
    category = st.selectbox("Source Category", list(source_types.keys()), 
                             index=list(source_types.keys()).index(source.get('category', 'Source Service')))
    
    source_type = st.selectbox("Source Type", source_types[category], 
                                index=source_types[category].index(source.get('type', '')))
    
    # Add more specific editing logic here similar to create_source_form
    is_active = st.checkbox("Active", value=source.get('is_active', True))
    access_level = st.selectbox("Access Level", 
        ["Public", "Private", "Restricted"], 
        index=["Public", "Private", "Restricted"].index(source.get('access_level', 'Private')))
    
    if st.button("Update Source"):
        updated_source = {
            **source,
            "name": name,
            "description": description,
            "category": category,
            "type": source_type,
            "is_active": is_active,
            "access_level": access_level
        }
        
        source_manager = SourceManager()
        if source_manager.update_source(source['id'], updated_source):
            st.success("Source updated successfully!")
        else:
            st.error("Failed to update source")

def main():
    st.title("RAG Source Manager")
    
    menu = ["Create Source", "Browse Sources"]
    choice = st.sidebar.radio("Navigation", menu)
    
    if choice == "Create Source":
        create_source_form()
    elif choice == "Browse Sources":
        browse_sources()

main()