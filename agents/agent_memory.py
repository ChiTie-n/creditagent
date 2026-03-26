"""
agent_memory.py
Shared in-process memory store for agent state, reasoning traces, and decision history.
Enables agents to recall past decisions and build context across a session.
"""

from collections import deque
from datetime import datetime
from typing import Any


class AgentMemory:
    """
    Lightweight in-memory store for a single assessment run.
    Tracks: observations, tool calls, reasoning steps, and final decisions.
    """

    def __init__(self, max_steps: int = 50):
        self.steps: list[dict] = []
        self.observations: dict[str, Any] = {}
        self.tool_calls: list[dict] = []
        self._max = max_steps

    def add_thought(self, agent: str, thought: str):
        self.steps.append({
            "type": "thought",
            "agent": agent,
            "content": thought,
            "ts": datetime.utcnow().isoformat(),
        })

    def add_action(self, agent: str, tool: str, args: dict, result: Any):
        entry = {
            "type": "action",
            "agent": agent,
            "tool": tool,
            "args": args,
            "result": result,
            "ts": datetime.utcnow().isoformat(),
        }
        self.steps.append(entry)
        self.tool_calls.append(entry)

    def add_observation(self, key: str, value: Any):
        self.observations[key] = value

    def get_context_summary(self) -> str:
        """Return a compact text summary of what has been done so far."""
        lines = []
        for s in self.steps[-20:]:  # last 20 steps for context window efficiency
            if s["type"] == "thought":
                lines.append(f"[THOUGHT/{s['agent']}] {s['content']}")
            elif s["type"] == "action":
                lines.append(f"[ACTION/{s['agent']}] {s['tool']}({s['args']}) → {str(s['result'])[:120]}")
        return "\n".join(lines)

    def to_trace(self) -> list[dict]:
        return list(self.steps)


# ── Session-level history (persists across requests in the same process) ──────
_session_history: deque = deque(maxlen=100)


def record_decision(borrower_id: str, decision: str, composite_score: int, reasoning: str):
    _session_history.append({
        "borrower_id": borrower_id,
        "decision": decision,
        "composite_score": composite_score,
        "reasoning": reasoning,
        "ts": datetime.utcnow().isoformat(),
    })


def get_session_history() -> list[dict]:
    return list(_session_history)
