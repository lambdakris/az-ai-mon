import os
import sys
import pathlib
import logging
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference.tracing import AIInferenceInstrumentor
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv

load_dotenv()

ASSET_PATH = pathlib.Path(__file__).parent / "assets"

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

def get_logger(module_name):
    return logger.getChild(module_name)

def enable_telemetry(log_to_project: bool = False):
    AIInferenceInstrumentor().instrument()

    os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true"

    if log_to_project:
        project = AIProjectClient.from_connection_string(
            conn_str=os.environ["AIPROJECT_CONNECTION_STRING"],
            credential=DefaultAzureCredential()
        )
        telemetry_conn_str = project.telemetry.get_connection_string()
        configure_azure_monitor(connection_string=telemetry_conn_str)

        tracing_link = f"https://ai.azure.com/tracing?wsid=/subscriptions/{project.scope['subscription_id']}/resourceGroups/{project.scope['resource_group_name']}/providers/Microsoft.MachineLearningServices/workspaces/{project.scope['project_name']}"
        logger.info(f"Telemetry enabled. View traces at {tracing_link}")
