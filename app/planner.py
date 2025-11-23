"""
LLM-based planner that selects which agents to call. Includes a deterministic
fallback so the app works without OpenAI credentials.
"""
from __future__ import annotations

import json
import os
from typing import List

try:
    from openai import OpenAI  # type: ignore
except ImportError:
    OpenAI = None  # library optional for the demo

from .models import Plan, PlanStep


def plan_tools_with_llm(query: str, registry: List) -> Plan:
    """Ask an LLM to propose a tool plan; fall back to a safe default."""

    if OpenAI is None or os.getenv("OPENAI_API_KEY") is None:
        return Plan(
            steps=[
                PlanStep(
                    step_id=0,
                    agent="document_summarizer_agent",
                    intent="summary.create",
                    input_source="user_query",
                )
            ]
        )

    client = OpenAI()
    agents_summary = [
        {"name": a.name, "description": a.description, "intents": a.intents}
        for a in registry
    ]

    system_prompt = (
        "You are a planner that selects worker agents to satisfy a user query. "
        "Return ONLY JSON with the shape {\\"steps\\":[{\\"step_id\\":0,\\"agent\\":...,\\"intent\\":...,\\"input_source\\":...},...]}. "
        "input_source is either 'user_query' or 'step:X.output.result'."
    )
    user_prompt = json.dumps(
        {
            "user_query": query,
            "available_agents": agents_summary,
        },
        indent=2,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()
    try:
        plan_json = json.loads(content)
        return Plan(**plan_json)
    except Exception:
        return Plan(
            steps=[
                PlanStep(
                    step_id=0,
                    agent="document_summarizer_agent",
                    intent="summary.create",
                    input_source="user_query",
                )
            ]
        )
