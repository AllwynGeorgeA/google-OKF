import os
import re
from pathlib import Path

os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

import db
import jev

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
KNOWLEDGE = ROOT / "knowledge"
SETUP = ("OpenAI key missing. 1) copy .env.example to .env  2) set OPENAI_API_KEY=sk-...  "
         "3) restart the backend.")

app = FastAPI(title="Sales Drop Assistant (demo)")
if not db.DB.exists():
    db.seed()


class Ask(BaseModel):
    question: str


@app.post("/api/analyze")
def analyze(body: Ask):
    routed, label = jev.route(body.question)
    names = ["index.md"] + [n for n in routed if (KNOWLEDGE / n).is_file()]
    files = {n: (KNOWLEDGE / n).read_text(encoding="utf-8") for n in dict.fromkeys(names)}
    res = {"router": label, "files": files, "metrics": db.compare_metrics(), "answer": None, "error": None}
    if not os.getenv("OPENAI_API_KEY"):
        res["error"] = SETUP
        return res
    try:
        from agent import analyze as run  # lazy: keeps startup fast
        res["answer"] = run(body.question, "\n\n".join(files.values()))
    except Exception as e:
        res["error"] = re.sub(r"sk-[A-Za-z0-9_\-*.]+", "sk-***", f"{type(e).__name__}: {e}")  # never leak key
    return res
