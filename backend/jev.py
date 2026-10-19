"""Router adapter. Uses TypeSafe Jev (POST /v1/systemone) when JEV_API_KEY is set, else keyword routing.
route() returns (knowledge file names, label shown in the UI)."""
import json
import os
import urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
DEMO = "Demo router — Jev not connected"
FILES = {  # one yes/no question per file
    "metrics.md": "Does answering need definitions of sales, revenue or payment-failure metrics?",
    "tables.md": "Does answering need the database table schema?",
    "runbook.md": "Does answering need steps for investigating why sales changed?",
}
KEYWORDS = {
    "metrics.md": ["sales", "revenue", "order", "payment", "fail", "rate", "metric"],
    "tables.md": ["table", "schema", "column", "data", "query"],
    "runbook.md": ["why", "drop", "down", "fell", "decrease", "decline", "investigate", "today"],
}


def keyword_route(question: str) -> list[str]:
    q = question.lower()
    return [f for f, words in KEYWORDS.items() if any(w in q for w in words)] or ["runbook.md", "metrics.md"]


def _jev(question: str) -> list[str]:
    body = {"model": "jev-latest", "state": question, "questions": {
        f: {"type": "noul", "instructions": q, "criteria": {"true": "yes", "false": "no"}}
        for f, q in FILES.items()}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {
        "Authorization": "Bearer " + os.environ["JEV_API_KEY"], "Content-Type": "application/json"})
    answers = json.load(urllib.request.urlopen(req, timeout=10))["answers"]
    return [f for f in FILES if answers[f]["noul"] > 0.5]  # noul = Jev's yes-probability


def route(question: str) -> tuple[list[str], str]:
    if os.getenv("JEV_API_KEY"):
        try:
            return _jev(question) or keyword_route(question), "Jev (TypeSafe)"
        except Exception:
            return keyword_route(question), "Jev unavailable — keyword fallback"
    return keyword_route(question), DEMO
