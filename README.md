# blogger-papers-agent

# PaperReview Orchestrator – Multi-Agent Scientific Literature Reviewer

Agents Intensive – Capstone Project


## 1. Project Overview

PaperReview Orchestrator is a multi-agent system built with the Google Agent Development Kit (ADK) that automates a large portion of the scientific literature review workflow.

Given a short, free-form description of a research topic, the system:

1. Refines the topic into a focused research query with keywords and optional filters.
2. Searches the web for recent, relevant scientific papers.
3. Skims candidate papers and extracts structured notes for each one.
4. Writes a polished literature review in Markdown format.
5. Saves the resulting `.md` file to disk, ready to be shared, versioned, or extended.

The project demonstrates three core concepts from the course:

- A **multi-agent system** with an orchestrator and multiple specialist agents.
- Use of **tools**, including built-in ADK tools (Google Search, URL context) and custom tools (file saving and listing).
- **Sessions & state management**, using `InMemorySessionService` and `session.state` to coordinate agents across a workflow.

This repository contains the code for the agents, tools, and a simple CLI runner to interact with the system.


## 2. Problem Statement

Creating a good scientific literature review is critical for research but involves a lot of repetitive manual work:

- Turning a vague research idea into precise queries for search engines and academic indexes.
- Navigating through long lists of search results and deciding which papers are actually relevant.
- Skimming abstracts and sections from each candidate paper and taking structured notes.
- Synthesizing all the information into a coherent, well-structured narrative.
- Consistently formatting the final review and keeping track of versions.

Researchers and students often repeat this process for every new project or question. It is time-consuming, error-prone, and difficult to scale. When deadlines are tight, they may read fewer papers than ideal or produce shallow summaries just to meet time constraints.

The core pain points are:

- **Search inefficiency** – starting from vague queries and manually refining them.
- **Information overload** – too many papers, not enough time to read them all deeply.
- **Synthesis overhead** – turning scattered notes into a cohesive document.
- **Formatting and file management** – maintaining consistent structure and storing results.

PaperReview Orchestrator aims to streamline these steps by delegating much of the mechanical work to agents and tools, leaving humans free to focus on deep understanding and critical evaluation.


## 3. Solution Statement

PaperReview Orchestrator is a multi-agent pipeline that turns a short description of a topic into a structured literature review.

At a high level, the system:

1. **Normalizes the topic**  
   A planner-style agent reads the user input and converts it into structured metadata: a single-sentence research question, keywords, and optional filters (years, venues, notes). This helps the system construct better search queries and improves reproducibility.

2. **Discovers and summarizes papers**  
   A researcher agent uses ADK’s built-in tools to:
   - Search the web for scientific articles and preprints.
   - Open promising URLs and skim their content.
   - Select a limited number of relevant and diverse papers.
   - Produce structured notes for each paper: title, year, venue, authors, URL, a short summary, and key points.

3. **Generates the Markdown literature review**  
   A writer agent takes the structured notes and the refined topic, and constructs a complete Markdown document with:
   - Title and optional abstract.
   - Table of contents.
   - Paper-by-paper sections.
   - Synthesis sections that compare approaches, highlight trends, and identify gaps.
   - A references section with URLs.

4. **Saves the result to disk**  
   A custom tool called by the writer agent saves the Markdown text to a `.md` file with a timestamped, slugified name.

Throughout this process, all intermediate data—topic, notes, final markdown—are stored in `session.state`, enabling the orchestrator to coordinate agents and reuse information across turns.


## 4. Architecture

### 4.1 System Components

The main components of the system are:

- **Orchestrator agent (`paper_review_orchestrator`)** – coordinates the overall workflow.
- **Specialist agents**:
  - `topic_normalizer_agent`
  - `paper_research_agent`
  - `markdown_writer_agent`
- **Guard agents and callbacks**:
  - `TopicPresenceGuard`
  - `MarkdownReportGuard`
  - `track_agent_start` / `track_agent_end`
- **Tools**:
  - Built-in: `GoogleSearchTool`, `UrlContextTool`
  - Custom: `save_markdown_report`, `list_existing_reports`
- **Session service and runner**:
  - `InMemorySessionService` for stateful sessions.
  - `runner.py` as a simple CLI wrapper around the root agent.

Conceptually, you can imagine the architecture as a central orchestrator node that calls specialist agents in sequence, with guard agents acting as gatekeepers and tools supplying external capabilities like web search and file saving.


### 4.2 Agents

#### Orchestrator: `paper_review_orchestrator` (root_agent)

Defined in `paper_review_agent/agent.py` and re-exported from `paper_review_agent/__init__.py` as `root_agent`.

Responsibilities:

- Receives user messages describing the research topic.
- Stores the initial topic in `session.state["raw_topic"]` if not already present.
- Coordinates the planner, researcher, and writer agents.
- Uses sub-agents and guard agents to progress through the pipeline.
- Sets `output_key="final_markdown"` so the final Markdown text is returned to the caller.

The orchestrator is the main entry point for ADK runtimes or the CLI runner.


#### Topic Normalizer: `topic_normalizer_agent`

Defined in `paper_review_agent/query_agent.py`.

Responsibilities:

- Takes the user’s free-form topic description.
- Produces a structured JSON object:

  ```json
  {
    "normalized_query": "single sentence research question",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "filters": {
      "year_from": 2020,
      "year_to": 2025,
      "venues": ["journal or conference"],
      "notes": "additional constraints"
    }
  }

Stores this object in `session.state["normalized_topic"]` (via `output_key`).

This agent does not use tools; it is purely an LLM planner. Having normalized metadata improves search quality and makes it easier to reproduce the review later.

### Paper Researcher: `paper_research_agent`

Defined in `paper_review_agent/research_agent.py`.

**Responsibilities:**

- Consumes `session.state["normalized_topic"]` (if available) and/or the original user topic.
- Uses tools:
  - `GoogleSearchTool` to search for scientific articles.
  - `UrlContextTool` to read the content of landing pages or PDFs.
- Selects up to `config.max_papers` relevant papers.
- Produces structured notes and stores them in `session.state["paper_notes"]` with shape:

```json
{
  "papers": [
    {
      "title": "...",
      "year": 2024,
      "venue": "...",
      "url": "...",
      "authors": ["Author One", "Author Two"],
      "short_summary": "...",
      "key_points": ["...", "..."]
    }
  ]
}
```
This agent illustrates the integration of built-in tools with LLM reasoning to perform realistic web research tasks.

### Markdown Writer: `markdown_writer_agent`

Defined in `paper_review_agent/markdown_agent.py`.

**Responsibilities:**

- Reads `normalized_topic` and `paper_notes` from `session.state`.
- Writes a complete literature review in Markdown, including:
  - Title and abstract.
  - Table of contents.
  - One section per paper.
  - Synthesis sections.
  - References section.
- Calls `save_markdown_report(topic, markdown_content)` (via `FunctionTool`) exactly once per run to persist the file.
- Optionally uses `list_existing_reports()` if the user asks about previous reviews.
- Stores the final document in `session.state["final_markdown"]` and returns it as the final response.

The instructions for this agent emphasize academic tone, clear structure, and avoidance of hallucinated citations.


### 4.3 Guard Agents and Callbacks

Defined in `paper_review_agent/agent_utils.py`.

#### `TopicPresenceGuard`

- Subclass of `BaseAgent`.
- Checks `session.state` for `normalized_topic` or `raw_topic`.
- Escalates only when a topic exists, preventing the pipeline from proceeding without a defined subject.

#### `MarkdownReportGuard`

- Escalates only when `final_markdown` exists in `session.state`.
- Useful if you later chain additional agents that further process the completed review.

#### Callbacks: `track_agent_start` and `track_agent_end`

- Registered as before/after callbacks on the root agent.
- Write the name of the agent that just started or finished into `session.state`.
- Provide lightweight execution tracing and make it easier to debug or inspect the multi-agent workflow.

