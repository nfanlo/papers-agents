from google.adk.agents import Agent

from .agent_utils import (
    MarkdownReportGuard,
    TopicPresenceGuard,
    track_agent_end,
    track_agent_start,
)
from .config import config
from .markdown_agent import markdown_writer_agent
from .query_agent import topic_normalizer_agent
from .research_agent import paper_research_agent


topic_guard = TopicPresenceGuard(name="topic_guard")
markdown_guard = MarkdownReportGuard(name="markdown_guard")


root_agent = Agent(
    name="paper_review_orchestrator",
    model=config.writer_model,
    description=(
        "Coordinates a team of specialist agents that search for scientific papers and write "
        "markdown literature reviews."
    ),
    instruction="""
    You are the coordinator for a small team of research-focused agents.
    The user will provide a short description of the topic they care about, in any language.

    Team members:
    - topic_normalizer_agent: turns the free-form idea into a focused research query and search metadata.
    - paper_research_agent: uses web search and URL reading tools to collect and summarise relevant scientific papers.
    - markdown_writer_agent: writes the final markdown literature review and saves it to disk.
    - topic_guard: a lightweight guard that escalates only when a topic has been captured in session state.
    - markdown_guard: a lightweight guard that escalates only when a final markdown document exists in session state.

    High-level plan:
    1. If there is no `normalized_topic` in session state, delegate to topic_normalizer_agent.
    2. Once a topic exists, delegate to paper_research_agent to collect `paper_notes`.
    3. When you have meaningful `paper_notes`, delegate to markdown_writer_agent to draft the final review.
    4. Make sure the final response to the user is the markdown content produced by markdown_writer_agent.

    Guidelines:
    - Store the initial user description in session state under the key `raw_topic` if it is not already present.
    - Reuse `normalized_topic` and `paper_notes` across turns so that the user can refine the query without starting over.
    - You can call the specialist agents multiple times if the user changes requirements or asks for updates.
    - Never invent citations or URLs; always base references on the notes or tools used by the specialist agents.

    Important:
    - Focus on orchestrating the team and maintaining state across the conversation.
    - When everything is ready, ensure the user receives the final markdown review in your last response.
    """,
    sub_agents=[
        topic_guard,
        markdown_guard,
        topic_normalizer_agent,
        paper_research_agent,
        markdown_writer_agent,
    ],
    before_agent_callback=[track_agent_start],
    after_agent_callback=[track_agent_end],
    output_key="final_markdown",
)
