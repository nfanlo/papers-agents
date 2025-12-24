import os
import re
from datetime import datetime
from typing import Dict, List

from google.adk.tools import FunctionTool

from .config import config


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-") or "report"


def save_markdown_report(topic: str, markdown_content: str) -> Dict[str, str]:
    os.makedirs(config.output_directory, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    slug = _slugify(topic)
    filename = f"{timestamp}-{slug}.md"
    path = os.path.join(config.output_directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    return {"filename": filename, "path": path}


def list_existing_reports() -> List[str]:
    if not os.path.isdir(config.output_directory):
        return []
    entries = [
        name
        for name in os.listdir(config.output_directory)
        if name.endswith(".md")
    ]
    entries.sort()
    return entries


save_markdown_report_tool = FunctionTool(func=save_markdown_report)
list_existing_reports_tool = FunctionTool(func=list_existing_reports)
