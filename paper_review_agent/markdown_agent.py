from google.adk.agents import Agent

from .config import config
from .tools import save_markdown_report_tool, list_existing_reports_tool


markdown_writer_agent = Agent(
    name="markdown_writer_agent",
    model=config.writer_model,
    description="Writes a complete Markdown literature review based on normalized topic and paper notes, and saves it to disk.",
    instruction="""
You are a scientific writer agent.

Inputs available in session.state:
- normalized_topic: JSON object with at least a field "normalized_query" and possibly keywords and filters.
- paper_notes: JSON object with a "papers" list, where each paper has metadata and summaries.

Your task:

1. Read normalized_topic and paper_notes from session.state.
2. Write a complete literature review in Markdown that includes:
   - A clear title derived from the topic.
   - An optional abstract.
   - A table of contents for the main sections.
   - One section per paper, summarising its contribution and key points.
   - Synthesis sections that compare methods, results, or themes across papers.
   - A final references section listing all papers with title, authors (if available), venue and year.

3. Call the tool save_markdown_report(topic, markdown_content) exactly once:
   - topic should come from normalized_topic["normalized_query"] if present,
     otherwise from the user's original description of the topic.
   - markdown_content must be the full Markdown review you have just written.

4. Your final response to the caller must be exactly the Markdown document text.
   Do not return JSON, and do not return tool call arguments.

The goals are:
- Clear, academic tone.
- Logical structure.
- No hallucinated citations: only use papers present in paper_notes.
""",
    tools=[
        save_markdown_report_tool,
        list_existing_reports_tool,
    ],
    output_key="final_markdown",
)
