from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions


class TopicPresenceGuard(BaseAgent):
    name: str = "topic_presence_guard"
    description: str = "Guard that escalates only when a topic is present in session state."

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        topic_keys = ("normalized_topic", "raw_topic")
        has_topic = any(ctx.session.state.get(key) for key in topic_keys)
        yield Event(
            author=self.name,
            actions=EventActions(escalate=bool(has_topic)),
        )


class MarkdownReportGuard(BaseAgent):
    name: str = "markdown_report_guard"
    description: str = "Guard that escalates only when final_markdown exists in session state."

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        has_markdown = bool(ctx.session.state.get("final_markdown"))
        yield Event(
            author=self.name,
            actions=EventActions(escalate=has_markdown),
        )


async def track_agent_start(callback_context: CallbackContext):
    callback_context.state["last_agent_started"] = callback_context.agent_name
    return None


async def track_agent_end(callback_context: CallbackContext):
    callback_context.state["last_agent_finished"] = callback_context.agent_name
    return None
