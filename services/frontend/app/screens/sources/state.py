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


def get_source_types():
    return [
        'Provider',
        'Repository'
    ]

def get_source_type_options():
    return {
        'Provider': [
            'Retrieval API',
            'Grounding API',
        ],
        'Repository': [
            'DB Pull (SQL)',
            'DB Pull (NoSQL)', 
            'API Pull (HTTP)',
            'API Pull (GraphQL)', 
            'Web Crawl',
            'File Share',
            'Data Stream'
        ]
    }