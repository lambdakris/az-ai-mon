import os
import multiprocessing
import contextlib
import pandas as pd
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.ai.evaluation import evaluate, GroundednessEvaluator
from azure.identity import DefaultAzureCredential
from chat_with_products import chat_with_products
from config import ASSET_PATH

from dotenv import load_dotenv

load_dotenv()

project = AIProjectClient.from_connection_string(
    conn_str=os.getenv("AIPROJECT_CONNECTION_STRING"),
    credential=DefaultAzureCredential()
)

connection = project.connections.get_default(ConnectionType.AZURE_OPEN_AI, include_credentials=True)

evaluator_model = {
    "azure_endpoint": connection.endpoint_url,
    "azure_deployment": os.environ["EVALUATION_MODEL"],
    "api_version": "2024-06-01",
    "api_key": connection.key,
}

groundedness = GroundednessEvaluator(evaluator_model)

def eval_chat_with_products(query):
    response = chat_with_products(messages=[{"role": "user", "content": query}])
    return {
        "response": response["message"].content, 
        "context": response["context"]["grounding_data"]
    }

if __name__ == "__main__":
    result = evaluate(
        data = Path(ASSET_PATH)/"chat_eval_data.jsonl",
        target = evaluate_chat_with_products,
        evaluation_name = "evaluate_chat_with_products",
        evaluators = {
            "groundedness": groundedness
        },
        evaluator_config={
            "default": {
                "query": { "${data.query}"},
                "context": { "${target.context}"},
                "response": { "${target.response}"}
            }
        },
        azure_ai_project=project.scope,
        output_path="./myevalresults.json",
    )
