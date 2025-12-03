import asyncio
import uuid
from typing import Optional, Tuple

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from paper_review_agent import root_agent


APP_NAME = "paper_review_app"


async def create_runner(user_id: str, session_id: Optional[str] = None) -> Tuple[Runner, str]:
    session_service = InMemorySessionService()
    effective_session_id = session_id or str(uuid.uuid4())
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=effective_session_id,
    )
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    return runner, effective_session_id


async def run_once(topic: str, user_id: str = "cli-user") -> str:
    runner, session_id = await create_runner(user_id=user_id)
    user_message = Content(
        role="user",
        parts=[Part(text=topic)],
    )
    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or ""
    return final_text


def main() -> None:
    topic = input("Enter a short description of the research topic: ").strip()
    if not topic:
        print("Empty topic, nothing to do.")
        return
    markdown = asyncio.run(run_once(topic))
    print()
    print("=== Generated Markdown Review ===")
    print()
    print(markdown)


if __name__ == "__main__":
    main()
