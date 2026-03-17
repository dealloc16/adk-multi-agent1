import logging
import google.cloud.logging

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest

 # print statements go to terminal, logging statements go to cloud logging
 # theres also a before/after agent callback but did not seem to be helpful here

def log_query_to_model(callback_context: CallbackContext, llm_request: LlmRequest):
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        if llm_request.contents[-1].parts[-1].text:
            last_user_message = llm_request.contents[-1].parts[0].text
            logging.info(f"[query to {callback_context.agent_name}]: " + last_user_message)

def log_model_response(callback_context: CallbackContext, llm_response: LlmResponse):
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                logging.info(f"[response from {callback_context.agent_name}]: " + part.text)
            elif part.function_call:
                logging.info(f"[function call from {callback_context.agent_name}]: " + part.function_call.name)

def log_query_to_tool(tool: dict, input: dict, callback_context: CallbackContext):
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
    logging.info(f"[query to tool]: " + str(input))

def log_tool_response(tool: dict, input: dict, callback_context: CallbackContext, tool_response: dict):
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
    logging.info(f"[tool response]: " + str(tool_response))
