import os
from pathlib import Path
from opentelemetry import trace
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.inference.prompts import PromptTemplate
from config import ASSET_PATH, get_logger, enable_telemetry
from query_search_index import get_product_documents

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

project = AIProjectClient.from_connection_string(
    conn_str="eastus.api.azureml.ms;c33784d2-77cc-4280-b6b4-7846df73349f;gaimon;gaimon1",
    credential=DefaultAzureCredential()
)

completions = project.inference.get_chat_completions_client()

@tracer.start_as_current_span(name="chat_with_products")
def chat_with_products(messages: list[dict]) -> dict:
    documents = get_product_documents(messages, {})

    grounded_chat_prompt = PromptTemplate.from_prompty(Path(ASSET_PATH)/"grounded_chat.prompty")

    system_message = grounded_chat_prompt.create_messages(documents=documents)

    response = completions.complete(
        model="gpt-4o-mini",
        messages=system_message + messages,
        **grounded_chat_prompt.parameters,
    )

    logger.info(f"Chat response: {response.choices[0].message}")

    return { "message": response.choices[0].message }

if __name__ == "__main__":
    enable_telemetry(log_to_project=True)
    chat_with_products(
        messages=[{
            "role": "user", 
            "content": "I need a new tent for 4 people, what would you recommend?"
        }]
    )