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
from podcast_transcript_agent.models.podcast_transcript import PodcastTranscript

podcast_transcript_writer_agent = Agent( 
    name="podcast_transcript_writer_agent",
    model="gemini-2.5-flash",
    description="Writes the podcast transcript based on the podcast plan",
    instruction=prompt.PODCAST_TRANSCRIPT_WRITER_PROMPT,
    output_schema=PodcastTranscript,
    output_key="podcast_episode_transcript"
 )

