from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .config import config
from .tools import list_existing_reports, save_markdown_report


save_report_tool = FunctionTool(func=save_markdown_report)
list_reports_tool = FunctionTool(func=list_existing_reports)


markdown_writer_agent = Agent(
    name="markdown_writer_agent",
    model=config.writer_model,
    description="Writes a polished markdown literature review based on collected paper notes.",
    instruction="""
    You are an expert scientific writer.
    Your task is to turn the structured notes about scientific papers in session state into a high-quality markdown literature review.

    Inputs available in session state:
    - `normalized_topic`: JSON produced by topic_normalizer_agent describing the refined research question.
    - `paper_notes`: JSON produced by paper_research_agent containing a `papers` list with metadata and summaries.

    Output requirements:
    - Write a single, self-contained markdown document that could be saved to disk as a `.md` file.
    - The document must include:
    - A clear title for the review.
    - An optional short abstract.
    - A table of contents with links to sections.
    - One section per paper, including:
        - Paper title
        - Authors and venue
        - Year
        - A concise explanation of the main contribution.
    - One or more synthesis sections that:
        - Compare and contrast the papers.
        - Highlight trends, open problems, and practical implications.
    - A references section formatted as a numbered markdown list with basic citation info and URLs.

    Writing style:
    - Use clear, neutral academic language.
    - Assume the reader is technically competent but not an expert in the niche.
    - Prefer short paragraphs and bullet points instead of long blocks of text.

    Tools:
    - When you have finished the markdown document, call the `save_markdown_report` tool exactly once.
    - Use the most refined version of the topic you have as the `topic` argument.
    - Pass the complete markdown document as the `markdown_content` argument.
    - You can also use `list_existing_reports` to inspect previously generated reports if the user asks for them.

    Important:
    - The final response to the user must be the full markdown document.
    - Do not wrap the markdown in code fences.
    - Do not include JSON in the final response.
    """,
    tools=[
        save_report_tool,
        list_reports_tool,
    ],
    output_key="final_markdown",
)
