import os
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SemanticSearch,
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SearchableField,
    SimpleField,
    SemanticField,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    HnswAlgorithmConfiguration,
    HnswParameters,
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    VectorSearchProfile,
)
import pandas as pd
from config import get_logger

logger = get_logger(__name__)

project = AIProjectClient.from_connection_string(
    conn_str="eastus.api.azureml.ms;c33784d2-77cc-4280-b6b4-7846df73349f;gaimon;gaimon1", #os.environ["AIPROJECT_CONNECTION_STRING"],
    credential=DefaultAzureCredential()
)

embeddings = project.inference.get_embeddings_client()

search_connection = project.connections.get_default(
    connection_type=ConnectionType.AZURE_AI_SEARCH,
    include_credentials=True
)

search_index_client = SearchIndexClient(
    endpoint=search_connection.endpoint_url,
    credential=AzureKeyCredential(key=search_connection.key)
)

def create_index() -> SearchIndex:
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="hnswProfile",
        )
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnswConfig",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    m=4,
                    ef_construction=1000,
                    ef_search=1000,
                    metric=VectorSearchAlgorithmMetric.COSINE,
                ),
            ),
            ExhaustiveKnnAlgorithmConfiguration(
                name="eknnConfig",
                kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                parameters=ExhaustiveKnnParameters(
                    metric=VectorSearchAlgorithmMetric.COSINE,
                ),
            ),
        ],
        profiles=[
            VectorSearchProfile(
                name="hnswProfile",
                algorithm_configuration_name="hnswConfig"
            ),
            VectorSearchProfile(
                name="eknnProfile",
                algorithm_configuration_name="eknnConfig"
            )
        ]
    )

    semantic_config = SemanticConfiguration(
        name="defaultConfig",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[SemanticField(field_name="content")],
            keywords_fields=[],
        ),
    )

    semantic_search = SemanticSearch(configurations=[semantic_config])

    search_index = SearchIndex(
        name="products",
        fields=fields,
        semantic_search=semantic_search,
        vector_search=vector_search,
    )

    search_index_client.create_or_update_index(search_index)

    return

def load_docs(path: str, embedding_model: str):
    products = pd.read_csv(path)
    documents = []

    for product in products.to_dict("records"):
        id = product["id"]
        title = product["name"]
        content = product["description"]
        contentVector = embeddings.embed(input=content, model=embedding_model).data[0].embedding
        rec = {
            "id": str(id),
            "title": title,
            "content": content,
            "contentVector": contentVector
        }
        documents.append(rec)

    return documents

def write_docs(docs: list[dict]):
    search_client = SearchClient(
        endpoint=search_connection.endpoint_url,
        credential=AzureKeyCredential(key=search_connection.key),
        index_name="products",
    )

    search_client.upload_documents(documents=docs)

    return

def populate_index():
    create_index()

    csv_file = "assets/products.csv"

    docs = load_docs(csv_file, embedding_model="text-embedding-ada-002")

    write_docs(docs)

if __name__ == "__main__":
    populate_index()
    logger.info("Index populated successfully")