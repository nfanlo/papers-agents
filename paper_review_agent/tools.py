import os
import re
from datetime import datetime
from typing import Dict, List, Optional

from .config import config


def _slugify(text: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return normalized or "paper-review"


def build_markdown_filename(topic: str, timestamp: Optional[datetime] = None) -> str:
    safe_topic = _slugify(topic)
    ts = timestamp or datetime.utcnow()
    suffix = ts.strftime("%Y%m%d-%H%M%S")
    return f"{suffix}-{safe_topic}.md"


def save_markdown_report(topic: str, markdown_content: str, directory: Optional[str] = None) -> Dict[str, str]:
    base_directory = directory or config.output_directory
    os.makedirs(base_directory, exist_ok=True)
    filename = build_markdown_filename(topic)
    path = os.path.join(base_directory, filename)
    with open(path, "w", encoding="utf-8") as file:
        file.write(markdown_content)
    return {"path": path, "filename": filename}


def list_existing_reports(directory: Optional[str] = None) -> Dict[str, List[str]]:
    base_directory = directory or config.output_directory
    if not os.path.isdir(base_directory):
        return {"files": []}
    entries = [
        entry
        for entry in os.listdir(base_directory)
        if os.path.isfile(os.path.join(base_directory, entry))
    ]
    return {"files": sorted(entries)}
