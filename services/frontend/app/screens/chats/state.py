from azure.ai.projects import AIProjectClient
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import ChatRequestMessage
from azure.identity import DefaultAzureCredential

connstr = "eastus.api.azureml.ms;c33784d2-77cc-4280-b6b4-7846df73349f;gaimon;gaimon1"
project = AIProjectClient.from_connection_string(connstr, DefaultAzureCredential())

def get_chat_client() -> ChatCompletionsClient:
    client = project.inference.get_chat_completions_client()
    return client

def get_chat_response(client: ChatCompletionsClient, messages: list[ChatRequestMessage]):
    completion = client.complete(
        model="gpt-4o-mini", 
        messages=messages,
        temperature=1,
        frequency_penalty=0.5,
        presence_penalty=0.5,
    )
    return completion.choices[0].message

