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

from google.adk.agents import Agent
from . import prompt
from podcast_transcript_agent.models.podcast_topics import PodcastTopics

podcast_topics_agent = Agent(
    name="podcast_topics_agent",
    model="gemini-2.5-flash",
    description="Extracts podcast topics from provided input",
    instruction= prompt.TOPIC_EXTRACTION_PROMPT,
    output_schema=PodcastTopics,
    output_key="podcast_topics"
)
