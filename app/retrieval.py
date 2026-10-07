from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "data" / "services.json"


def normalize(text: str) -> str:
    text = text.lower().replace("ë", "e").replace("ç", "c")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def service_document(service: dict[str, Any]) -> str:
    aliases = " ".join(service.get("aliases", []))
    documents = " ".join(service.get("documents", []))
    return " ".join(
        [
            service["title"],
            service["title"],
            aliases,
            aliases,
            service.get("category", ""),
            service.get("institution", ""),
            service.get("description", ""),
            service.get("eligibility", ""),
            documents,
        ]
    )


@dataclass(frozen=True)
class SearchResult:
    service: dict[str, Any]
    score: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.service["id"],
            "title": self.service["title"],
            "category": self.service["category"],
            "institution": self.service["institution"],
            "score": round(self.score, 4),
            "source_url": self.service["source_url"],
        }


class ServiceRetriever:
    def __init__(self, data_path: Path | str = DEFAULT_DATA_PATH):
        self.data_path = Path(data_path)
        self.services: list[dict[str, Any]] = json.loads(
            self.data_path.read_text(encoding="utf-8")
        )
        if not self.services:
            raise ValueError("services.json is empty")

        self.documents = [normalize(service_document(s)) for s in self.services]

        self.word = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            sublinear_tf=True,
            strip_accents=None,
        )
        self.char = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            sublinear_tf=True,
            min_df=1,
        )

        self.word_matrix = self.word.fit_transform(self.documents)
        self.char_matrix = self.char.fit_transform(self.documents)

    def _score(self, query: str) -> np.ndarray:
        q = normalize(query)
        if not q:
            return np.zeros(len(self.services), dtype=float)

        word_scores = cosine_similarity(
            self.word.transform([q]), self.word_matrix
        )[0]
        char_scores = cosine_similarity(
            self.char.transform([q]), self.char_matrix
        )[0]

        fuzzy_scores = np.array(
            [
                max(
                    fuzz.token_set_ratio(q, normalize(s["title"])) / 100.0,
                    max(
                        [
                            fuzz.token_set_ratio(q, normalize(alias)) / 100.0
                            for alias in s.get("aliases", [])
                        ]
                        or [0.0]
                    ),
                )
                for s in self.services
            ],
            dtype=float,
        )

        # Short exact aliases should be strongly useful (e.g. "ADR", "PAK").
        alias_bonus = np.array(
            [
                1.0
                if any(
                    normalize(alias) == q or normalize(alias) in q
                    for alias in s.get("aliases", [])
                    if len(normalize(alias)) >= 3
                )
                else 0.0
                for s in self.services
            ],
            dtype=float,
        )

        return (
            0.42 * char_scores
            + 0.28 * word_scores
            + 0.22 * fuzzy_scores
            + 0.08 * alias_bonus
        )

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        scores = self._score(query)
        order = np.argsort(scores)[::-1][: max(1, top_k)]
        return [
            SearchResult(service=self.services[int(i)], score=float(scores[int(i)]))
            for i in order
        ]

    def get(self, service_id: str) -> dict[str, Any] | None:
        return next((s for s in self.services if s["id"] == service_id), None)
