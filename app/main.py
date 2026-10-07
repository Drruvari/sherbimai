from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .answering import compose_answer
from .retrieval import ServiceRetriever


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "app" / "static"

app = FastAPI(
    title="ShërbimAI",
    version="1.0.0",
    description="Grounded Albanian public-service assistant.",
)
retriever = ServiceRetriever()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "services": len(retriever.services),
        "version": app.version,
    }


@app.get("/api/services")
def services():
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "category": s["category"],
            "institution": s["institution"],
            "source_url": s["source_url"],
            "verified_at": s["verified_at"],
        }
        for s in retriever.services
    ]


@app.get("/api/search")
def search(q: str = Query(min_length=2, max_length=500), top_k: int = 3):
    top_k = max(1, min(top_k, 5))
    return {"results": [r.as_dict() for r in retriever.search(q, top_k)]}


@app.post("/api/ask")
def ask(payload: AskRequest):
    results = retriever.search(payload.question, top_k=3)
    best = results[0]

    # Gating protects users from confident answers outside the curated scope.
    if best.score < 0.22:
        return {
            "matched": False,
            "answer": (
                "Nuk gjeta një përputhje mjaftueshëm të sigurt në grupin e "
                "shërbimeve që mbuloj aktualisht. Provo ta formulosh me emrin "
                "e dokumentit ose shërbimit."
            ),
            "confidence": round(best.score, 4),
            "alternatives": [r.as_dict() for r in results],
        }

    return {
        "matched": True,
        "answer": compose_answer(best.service, payload.question),
        "confidence": round(best.score, 4),
        "service": best.service,
        "alternatives": [r.as_dict() for r in results[1:]],
    }


@app.get("/api/services/{service_id}")
def service(service_id: str):
    found = retriever.get(service_id)
    if not found:
        raise HTTPException(status_code=404, detail="Service not found")
    return found
