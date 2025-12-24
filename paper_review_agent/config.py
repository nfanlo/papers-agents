from dataclasses import dataclass


@dataclass
class PaperReviewConfig:
    planner_model: str
    researcher_model: str
    writer_model: str
    max_papers: int
    output_directory: str


config = PaperReviewConfig(
    planner_model="gemini-2.5-flash",
    researcher_model="gemini-2.5-flash",
    writer_model="gemini-2.5-flash",
    max_papers=5,
    output_directory="results",
)
