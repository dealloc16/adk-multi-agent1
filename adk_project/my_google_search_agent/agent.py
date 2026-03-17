import os
import sys
# Add the parent directory to sys.path to allow importing from adk_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

from google.adk import Agent
from google.genai import types
from google.adk.tools import google_search  # The Google Search tool
from google.adk.models import Gemini, LlmResponse
from google.adk.apps.app import App

from adk_utils.plugins import Graceful429Plugin



load_dotenv()
google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
google_cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
google_genai_use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
model_name = os.getenv("MODEL")

# Retry options help avoid the occasional error from popular models
# receiving too many requests at once.
retry_options = types.HttpRetryOptions(initial_delay=1, attempts=6)

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response, log_query_to_tool, log_tool_response

root_agent = Agent(
    # name: A unique name for the agent.
    name="google_search_agent",
    # description: A short description of the agent's purpose, so
    # other agents in a multi-agent system know when to call it.
    description="Answer questions using Google Search.",
    # model: The LLM model that the agent will use:
    model=Gemini(model=model_name, retry_options=retry_options),
    # instruction: Instructions (or the prompt) for the agent.
    instruction="You are an expert researcher. You stick to the facts.",
    # callbacks: Allow for you to run functions at certain points in
    # the agent's execution cycle. In this example, you will log the
    # request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    before_tool_callback=log_query_to_tool,
    after_tool_callback=log_tool_response,

    # tools: functions to enhance the model's capabilities.
    # Add the google_search tool below.
    tools=[google_search]

)

graceful_plugin = Graceful429Plugin(
    name="graceful_429_plugin",
    fallback_text={
        "movie": "**[Simulated Response via 429 Graceful Fallback]**\n\nI am currently experiencing high demand due to quota exhaustion, but some recent popular movies in India include Bihu Attack and Border 2.",
        "news": "**[Simulated Response via 429 Graceful Fallback]**\n\nI am currently experiencing high demand due to quota exhaustion, but recent global news includes technological advancements, economic shifts, and ongoing international developments.",
        "default": "**[Simulated Response via 429 Graceful Fallback]**\n\nI am currently experiencing high demand due to quota exhaustion. Please try your request again later."
    }
)

# UNCOMMENT THE LINE BELOW TO TEST FAILOVER:
# graceful_plugin.apply_test_failover(root_agent)

graceful_plugin.apply_429_interceptor(root_agent)

app = App(
    name="my_google_search_agent",
    root_agent=root_agent,
    plugins=[graceful_plugin]
)
