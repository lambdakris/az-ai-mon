import os
from pathlib import Path
from opentelemetry import trace
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.ai.inference.prompts import PromptTemplate
from azure.search.documents.models import VectorizedQuery
from config import ASSET_PATH, get_logger

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

project = AIProjectClient.from_connection_string(
    conn_str="eastus.api.azureml.ms;c33784d2-77cc-4280-b6b4-7846df73349f;gaimon;gaimon1",
    credential=DefaultAzureCredential()
)

search_connection = project.connections.get_default(
    connection_type=ConnectionType.AZURE_AI_SEARCH,
    include_credentials=True
)

search_client = SearchClient(
    index_name="products",
    endpoint=search_connection.endpoint_url,
    credential=AzureKeyCredential(search_connection.key)
)

completions_client = project.inference.get_chat_completions_client()
embeddings_client = project.inference.get_embeddings_client()

@tracer.start_as_current_span(name="get_product_documents")
def get_product_documents(messages: list, context: dict = {}) -> dict:
    overrides = context.get("overrides", {})
    top = overrides.get("top", 5)

    query_intent_prompt = PromptTemplate.from_prompty(Path(ASSET_PATH)/"intent_mapping.prompty")

    query_intent_completion = completions_client.complete(
        model="gpt-4o-mini",
        messages=query_intent_prompt.create_messages(conversation=messages),
        **query_intent_prompt.parameters,
    )

    search_query = query_intent_completion.choices[0].message.content

    logger.debug(f"Search query: {search_query}")

    search_query_embedding = embeddings_client.embed(
        model="text-embedding-ada-002",
        input = search_query
    )
    search_query_vectorized = VectorizedQuery(
        vector=search_query_embedding.data[0].embedding,
        k_nearest_neighbors=top,
        fields="contentVector",
    )
    search_results = search_client.search(
        search_text=search_query,
        vector_queries=[search_query_vectorized],
        select=["id", "title", "content"]
    )

    grounding = [
        {
            "id": result["id"],
            "title": result["title"],
            "content": result["content"]
        }
        for result in search_results
    ]
    
    if "thoughts" not in context:
        context["thoughts"] = []

    context["thoughts"].append({
        "title": "Generated Search Query",
        "description": search_query,
    })

    if "grounding" not in context:
        context["grounding"] = []

    context["grounding"].append(grounding)

    logger.info(f"Grounding: {grounding}")

if __name__ == "__main__":
    messages = [
        {"role": "user", "content": "nature lover"},
    ]

    get_product_documents(messages)