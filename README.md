# ShërbimAI

ShërbimAI is a small, grounded NLP assistant for Albanian public services. A user
asks a question in natural Albanian, the system retrieves the most relevant
curated service, composes an answer from structured facts, and always exposes
the official e-Albania source.

**Current scope:** 8 verified services. This is an independent demo, not an
official government product.

## Why this exists

Government portals often require citizens to know the exact administrative
term for a service. ShërbimAI lets users search with ordinary language such as:

- `Si regjistroj fëmijën në klasë të parë?`
- `Jam jashtë Shqipërisë dhe më duhet dëshmi penaliteti.`
- `Sa kushton rinovimi ADR?`

## Architecture

```text
Browser
  |
  v
FastAPI  ---> intent-aware answer composer
  |
  v
Hybrid retrieval
  |- word TF-IDF (1-2 grams)
  |- character TF-IDF (3-5 grams)
  |- fuzzy title/alias similarity
  |
  v
curated services.json
  |
  v
official e-Albania source URL
```

The system deliberately avoids free-form generation in v1. That makes every
factual claim traceable to the structured dataset and prevents the assistant
from inventing procedures, prices, or deadlines.

## Run locally

Requires Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000`.

API docs are available at `http://localhost:8000/docs`.

## Run with Docker

```bash
docker compose up --build
```

Then open `http://localhost:8000`.

## API

Health:

```bash
curl http://localhost:8000/api/health
```

Ask:

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Sa kushton rinovimi ADR?"}'
```

Search:

```bash
curl "http://localhost:8000/api/search?q=deshmi%20penaliteti"
```

## Evaluation

`evals/questions.json` contains labeled natural-language Albanian queries.
Run:

```bash
python evals/evaluate.py
```

The script reports:

- Top-1 accuracy
- Top-3 recall
- MRR@3
- individual failures

Current result on the included 32-query labeled set: **100% Top-1 accuracy, 100% Top-3 recall, and 1.000 MRR@3**. This is a small curated regression set, not a claim of general population accuracy.

The repository includes the latest evaluation snapshot in `evals/results.json`. Re-run the evaluation whenever retrieval logic or data changes.

## Tests

```bash
pytest -q
```

GitHub Actions runs both the test suite and retrieval evaluation on every push
and pull request.

## Deploy on Render

This repo contains `render.yaml`.

1. Push the repository to GitHub.
2. In Render, create a new Blueprint and select the repository.
3. Render detects `render.yaml` and starts the FastAPI service.
4. Verify `/api/health` after deployment.

No API key or database is required.

## Data policy

The current dataset is intentionally curated rather than scraped at request
time. Each entry includes:

- official service URL
- institution
- eligibility
- required documents
- procedure
- processing time
- cost
- validity
- last verification date

This design makes evaluation reproducible and reduces the chance of silently
serving stale or fabricated information.

## Production improvements

The next version should add an ingestion pipeline that periodically checks
official sources for changes, stores snapshots, and flags modified procedures
for review. A larger evaluation set should include dialect variation,
misspellings, ambiguous questions, and explicit out-of-scope queries.

## Application-ready description

After you deploy and run the evaluation, use the real metrics from
`python evals/evaluate.py` in your application. Do not claim broader coverage
than the eight services currently in the dataset.

## Disclaimer

ShërbimAI is an independent informational demo. Always verify requirements,
prices, deadlines, and eligibility on the linked official e-Albania page.
