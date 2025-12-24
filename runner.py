import asyncio
import uuid
from typing import Optional, Tuple

from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from paper_review_agent import root_agent
from paper_review_agent.config import config


APP_NAME = "agents"


async def create_runner(
    user_id: str,
    session_id: Optional[str] = None,
) -> Tuple[Runner, InMemorySessionService, str]:
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
    return runner, session_service, effective_session_id


def extract_text_from_event(event) -> str:
    if not event.content or not event.content.parts:
        return ""
    chunks = []
    for part in event.content.parts:
        text = getattr(part, "text", None)
        if text:
            chunks.append(text)
    return "".join(chunks).strip()


async def run_once(topic: str, user_id: str = "cli-user") -> None:
    runner, session_service, session_id = await create_runner(user_id=user_id)
    user_message = Content(
        role="user",
        parts=[Part(text=topic)],
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        text = extract_text_from_event(event)
        if text:
            print()
            print(f"[{event.author}]")
            print(text)

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    state = session.state or {}

    print()
    print("Session state keys:", list(state.keys()))

    if "final_markdown" in state:
        value = state["final_markdown"]
        print()
        print("final_markdown type:", type(value).__name__)
        if isinstance(value, str):
            print()
            print("Final markdown preview:")
            print(value[:800])
    else:
        print()
        print("No final_markdown found in session state.")


def main() -> None:
    load_dotenv()
    topic = input("Enter a short description of the research topic: ").strip()
    if not topic:
        print("Empty topic, nothing to do.")
        return

    asyncio.run(run_once(topic))

    print()
    print("Pipeline finished.")
    print(f"If markdown_writer_agent ran successfully, a Markdown file")
    print(f"should now exist under ./ {config.output_directory}")


if __name__ == "__main__":
    main()
