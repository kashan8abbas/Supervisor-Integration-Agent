"""
Final answer synthesis: combine tool outputs into a user-friendly response.
Falls back to deterministic stitching when OpenAI is unavailable.
"""
from __future__ import annotations

import json
import os
from typing import Dict

try:
    from openai import OpenAI  # type: ignore
except ImportError:
    OpenAI = None

from .models import AgentResponse


def compose_final_answer(query: str, step_outputs: Dict[int, AgentResponse]) -> str:
    """Convert tool outputs into a concise answer."""
    successful = [s for s in step_outputs.values() if s.is_success()]
    if not successful:
        return "I could not complete your request because every tool failed. Please try again."

    if OpenAI is None or os.getenv("OPENAI_API_KEY") is None:
        stitched = " | ".join(str(s.output.result) for s in successful if s.output)
        return f"Based on the tools, here is what I found: {stitched}"

    client = OpenAI()
    tool_findings = [
        {
            "agent": s.agent_name,
            "status": s.status,
            "result": s.output.result if s.output else None,
            "details": s.output.details if s.output else None,
        }
        for s in step_outputs.values()
    ]

    system_prompt = (
        "You are a helpful assistant. Given the user's query and tool outputs, "
        "write a concise, actionable answer."
    )
    user_prompt = json.dumps(
        {
            "user_query": query,
            "tool_outputs": tool_findings,
        },
        indent=2,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()
