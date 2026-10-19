import os

from crewai import Agent, Crew, LLM, Task
from crewai.tools import tool

import db


@tool("compare_metrics")
def compare_metrics() -> dict:
    """Read-only. Revenue, successful orders and payment failure rate, today vs yesterday, matching time windows."""
    return db.compare_metrics()


@tool("failure_breakdown")
def failure_breakdown(group_by: str) -> dict:
    """Read-only. Failed payment attempts today vs yesterday, grouped by 'failure_reason' or 'payment_method'."""
    return db.failure_breakdown(group_by)


def analyze(question: str, knowledge: str) -> str:
    llm = LLM(model="openai/" + os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), temperature=0.2)
    agent = Agent(
        role="Sales analyst",
        goal="Explain sales changes using only numbers returned by your tools.",
        backstory="You are careful: you cite numbers, and you only suggest possible causes, never proven ones.",
        tools=[compare_metrics, failure_breakdown], llm=llm, allow_delegation=False, verbose=False,
    )
    task = Task(
        description=(f"Question: {question}\n\nKnowledge (follow the runbook if present):\n{knowledge}\n\n"
                     "Call the tools to get numbers. All data is DEMO data; say so. Do not invent numbers."),
        expected_output="A short answer (under 150 words): key numbers for today vs yesterday (matching window), "
                        "then 1-3 possible causes worded as hypotheses, then one suggested next check.",
        agent=agent,
    )
    return str(Crew(agents=[agent], tasks=[task], verbose=False).kickoff())
