from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions


class TopicPresenceGuard(BaseAgent):
    """Escalates only when a topic is present in the session state."""

    async def _run_async_impl(
        self, context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        topic_keys = ("normalized_topic", "raw_topic")
        has_topic = any(context.session.state.get(key) for key in topic_keys)
        if has_topic:
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name)


class MarkdownReportGuard(BaseAgent):
    """Escalates only when a final markdown report exists in the session state."""

    async def _run_async_impl(
        self, context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        if context.session.state.get("final_markdown"):
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name)


async def track_agent_start(callback_context: CallbackContext) -> None:
    """Stores the name of the agent that just started in the session state."""

    invocation = callback_context.invocation_context
    invocation.session.state["last_agent_started"] = invocation.agent.name


async def track_agent_end(callback_context: CallbackContext) -> None:
    """Stores the name of the agent that just finished in the session state."""

    invocation = callback_context.invocation_context
    invocation.session.state["last_agent_finished"] = invocation.agent.name
