# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LLM Auditor for verifying & refining LLM-generated answers using the web."""

from google.adk.agents import SequentialAgent

from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent

import logging
import google.cloud.logging

logging.basicConfig()

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()


llm_auditor = SequentialAgent(
    name='llm_auditor',
    description=(
        'Evaluates LLM-generated answers, verifies actual accuracy using the'
        ' web, and refines the response to ensure alignment with real-world'
        ' knowledge.'
    ),
    sub_agents=[critic_agent, reviser_agent],
)

import sys
import os

from google.adk.apps.app import App
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from adk_utils.plugins import Graceful429Plugin

graceful_plugin = Graceful429Plugin(
    name="graceful_429_plugin",
    fallback_text={
        "mars": "**[Simulated Response via 429 Graceful Fallback]**\n\nI am currently experiencing high demand due to quota exhaustion, but to correct your statement: Earth is actually closer to the Sun than Mars.",
        "sky": "**[Simulated Response via 429 Graceful Fallback]**\n\nI am currently experiencing high demand due to quota exhaustion, but to correct your statement: The sky is blue due to Rayleigh scattering in the atmosphere, not because it reflects the ocean.",
        "default": "**[Simulated Response via 429 Graceful Fallback]**\n\nThe LLM Auditor is currently experiencing high demand due to quota exhaustion. Please try again later."
    }
)

root_agent = llm_auditor

graceful_plugin.apply_429_interceptor(root_agent)

app = App(
    name="llm_auditor",
    root_agent=root_agent,
    plugins=[graceful_plugin]
)

# UNCOMMENT THE LINE BELOW TO TEST FAILOVER:
# graceful_plugin.apply_test_failover(root_agent)
