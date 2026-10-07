from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.retrieval import ServiceRetriever  # noqa: E402


def main() -> int:
    cases = json.loads((ROOT / "evals" / "questions.json").read_text(encoding="utf-8"))
    retriever = ServiceRetriever()

    top1 = 0
    top3 = 0
    rr_total = 0.0
    errors = []

    for case in cases:
        results = retriever.search(case["question"], top_k=3)
        ids = [r.service["id"] for r in results]
        expected = case["expected_id"]

        if ids[0] == expected:
            top1 += 1
        if expected in ids:
            top3 += 1
            rr_total += 1.0 / (ids.index(expected) + 1)
        else:
            errors.append(
                {
                    "question": case["question"],
                    "expected": expected,
                    "predicted": ids,
                }
            )

    n = len(cases)
    report = {
        "cases": n,
        "top1_accuracy": round(top1 / n, 4),
        "top3_recall": round(top3 / n, 4),
        "mrr_at_3": round(rr_total / n, 4),
        "errors": errors,
    }

    out = ROOT / "evals" / "results.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["top1_accuracy"] >= 0.80 else 1


if __name__ == "__main__":
    raise SystemExit(main())
