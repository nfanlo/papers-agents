import os
from dataclasses import dataclass


@dataclass
class PaperReviewConfig:
    planner_model: str
    researcher_model: str
    writer_model: str
    max_papers: int
    output_directory: str

    @classmethod
    def from_env(cls) -> "PaperReviewConfig":
        planner = os.environ.get("PAPER_REVIEW_PLANNER_MODEL", "gemini-2.0-flash")
        researcher = os.environ.get("PAPER_REVIEW_RESEARCHER_MODEL", "gemini-2.0-flash")
        writer = os.environ.get("PAPER_REVIEW_WRITER_MODEL", "gemini-2.0-pro")
        max_papers_raw = os.environ.get("PAPER_REVIEW_MAX_PAPERS", "5")
        output_dir = os.environ.get("PAPER_REVIEW_OUTPUT_DIR", "paper_markdown_reports")
        try:
            max_papers_value = int(max_papers_raw)
        except ValueError:
            max_papers_value = 5
        return cls(
            planner_model=planner,
            researcher_model=researcher,
            writer_model=writer,
            max_papers=max_papers_value,
            output_directory=output_dir,
        )


config = PaperReviewConfig.from_env()
