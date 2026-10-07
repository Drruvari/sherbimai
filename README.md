# ShërbimAI

ShërbimAI is a small, grounded NLP assistant for Albanian public services.

A user asks a question in natural Albanian, the system retrieves the most relevant curated service, composes an answer from structured facts, and always exposes the official e-Albania source.

**Current scope:** 8 verified services.

This is an independent demo and is not an official Albanian government product.

## Why this exists

Government portals often require citizens to know the exact administrative name of a service.

ShërbimAI allows users to search using ordinary Albanian language, for example:

- `Si regjistroj fëmijën në klasë të parë?`
- `Jam jashtë Shqipërisë dhe më duhet dëshmi penaliteti.`
- `Sa kushton rinovimi ADR?`
- `Më duhet vërtetim për pagesën PAK.`

The goal is to make public-service information easier to discover while keeping answers grounded in verified source data.

## How it works

```text
Browser
  |
  v
FastAPI
  |
  v
Intent-aware answer composer
  |
  v
Hybrid retrieval
  |- word TF-IDF
  |- character TF-IDF
  |- fuzzy title / alias similarity
  |
  v
curated services.json
  |
  v
official e-Albania source URL
```

The system deliberately avoids unrestricted free-form generation in version 1.

Instead, it retrieves a relevant service and constructs the answer from structured fields such as:

- institution
- eligibility
- required documents
- application steps
- processing time
- cost
- validity
- official source URL

This makes factual claims traceable and reduces the risk of inventing procedures, prices, requirements, or deadlines.

## Tech stack

- Python 3.12
- FastAPI
- Uvicorn
- scikit-learn
- RapidFuzz
- NumPy
- HTML / CSS / JavaScript
- Pytest
- Docker
- GitHub Actions

## Project structure

```text
sherbimai/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── retrieval.py
│   ├── answering.py
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── app.js
│
├── data/
│   └── services.json
│
├── evals/
│   ├── questions.json
│   └── evaluate.py
│
├── tests/
│   ├── test_api.py
│   └── test_retrieval.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
├── run.sh
├── LICENSE
└── README.md
```

## Run locally

Use Python 3.12.

### 1. Create a virtual environment

```bash
python3.12 -m venv .venv
```

### 2. Activate it

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the server

```bash
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## macOS with Homebrew

If Python 3.12 is not installed:

```bash
brew install python@3.12
```

Then:

```bash
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Example questions

Try:

```text
Si rinovoj ADR?
```

```text
Jam në Itali dhe më duhet certifikata e martesës.
```

```text
Si regjistroj fëmijën në klasë të parë?
```

```text
Jam jashtë Shqipërisë dhe më duhet dëshmi penaliteti.
```

```text
Sa kushton rinovimi ADR?
```

## API

### Health check

```bash
curl http://127.0.0.1:8000/api/health
```

Example response:

```json
{
  "status": "ok",
  "services": 8,
  "version": "1.0.0"
}
```

### Ask a question

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Sa kushton rinovimi ADR?"}'
```

Example response:

```json
{
  "matched": true,
  "answer": "**Rinovim i Certifikatës së Trajnimit ADR**\n\nKostoja: **6500 lekë**.",
  "confidence": 0.84,
  "service": {
    "id": "adr-renewal",
    "title": "Rinovim i Certifikatës së Trajnimit ADR"
  }
}
```

### Search services

```bash
curl "http://127.0.0.1:8000/api/search?q=deshmi%20penaliteti"
```

### List services

```bash
curl http://127.0.0.1:8000/api/services
```

## Retrieval approach

The retrieval engine combines several signals.

### Word TF-IDF

The system uses word-level TF-IDF with 1-2 word n-grams.

This helps match phrases such as:

```text
deshmi penaliteti
```

with the relevant service.

### Character TF-IDF

Character-level TF-IDF uses 3-5 character n-grams.

This makes retrieval more tolerant of:

- missing Albanian accents
- spelling differences
- partial words
- small typos

For example:

```text
deshmi penaliteti
```

can still match content containing:

```text
dëshmi penaliteti
```

### Fuzzy matching

RapidFuzz compares the question against:

- service titles
- aliases
- alternative phrases

This helps users who do not know the exact administrative terminology.

### Confidence gating

The system does not automatically answer every question.

If the highest retrieval score is too low, it returns an out-of-scope response instead of confidently showing an unrelated service.

Example:

```text
Nuk gjeta një përputhje mjaftueshëm të sigurt në grupin e
shërbimeve që mbuloj aktualisht.
```

## Answer generation

The answer layer detects simple user intent.

Supported intent types include:

- cost
- processing time
- required documents
- validity
- application steps

For example:

```text
Sa kushton rinovimi ADR?
```

can return only the relevant cost instead of the full service description.

A broader question such as:

```text
Si rinovoj ADR?
```

returns:

- service description
- eligibility
- required documents
- steps
- processing time
- cost
- validity

## Dataset

The current version contains 8 curated public services.

The dataset is stored in:

```text
data/services.json
```

Each service contains fields such as:

```json
{
  "id": "adr-renewal",
  "title": "Rinovim i Certifikatës së Trajnimit ADR",
  "category": "Transport dhe Automjete",
  "institution": "Drejtoria e Përgjithshme e Shërbimeve të Transportit Rrugor",
  "description": "...",
  "eligibility": "...",
  "documents": [],
  "steps": [],
  "processing_time": "1 muaj nga data e aplikimit",
  "validity": "5 vjet",
  "cost": "6500 lekë",
  "aliases": [],
  "source_url": "https://e-albania.al/...",
  "verified_at": "2026-10-07"
}
```

## Data policy

The current dataset is intentionally curated rather than scraped dynamically at request time.

Each entry includes:

- official service URL
- institution
- eligibility
- required documents
- application procedure
- processing time
- cost
- validity
- verification date

This design makes the system easier to test and reduces the chance of silently serving fabricated information.

It also means the current version does not automatically detect changes made later on official government pages.

## Evaluation

The repository includes a labeled evaluation set:

```text
evals/questions.json
```

Run:

```bash
python evals/evaluate.py
```

The evaluator reports:

- Top-1 accuracy
- Top-3 recall
- MRR@3
- retrieval failures

The current evaluation set contains 32 labeled Albanian questions across the supported services.

Current result on the included regression set:

```text
Top-1 accuracy: 100%
Top-3 recall:   100%
MRR@3:          1.000
```

These numbers describe performance only on the included curated evaluation set.

They are **not** a claim that the system achieves 100% accuracy across all Albanian public-service questions or real-world users.

A larger production evaluation should include:

- unseen questions
- spelling mistakes
- dialect variation
- ambiguous requests
- incomplete requests
- out-of-scope questions
- similar services that are difficult to distinguish

## Run tests

```bash
pytest -q
```

The tests cover:

- API health
- service retrieval
- expected query matches
- source availability
- missing services
- grounded API responses

## Continuous integration

The repository includes GitHub Actions configuration in:

```text
.github/workflows/ci.yml
```

On each push or pull request, GitHub Actions runs:

```bash
pytest -q
python evals/evaluate.py
```

This helps detect retrieval regressions when the code or dataset changes.

## Run with Docker

Build and start:

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000
```

You can also build manually:

```bash
docker build -t sherbimai .
docker run -p 8000:8000 sherbimai
```

## Deploy on Render

The project includes:

```text
render.yaml
```

Deployment steps:

1. Push the repository to GitHub.
2. Sign in to Render.
3. Create a new Blueprint.
4. Connect the GitHub repository.
5. Render detects `render.yaml`.
6. Deploy the service.
7. Verify the deployment using:

```text
https://YOUR-APP.onrender.com/api/health
```

No database or API key is required for version 1.

## Current limitations

ShërbimAI is intentionally small.

Current limitations include:

- only 8 services are supported
- the dataset is manually curated
- source changes are not automatically detected
- no conversational history
- no user accounts
- no database
- no automatic web ingestion
- no semantic embedding model
- no LLM generation layer
- evaluation data is small

These limitations are intentional for the first release because they keep the system reproducible, explainable, and easy to evaluate.

## Production improvements

If the project were expanded, the next priorities would be:

1. Add automatic ingestion from official government sources.
2. Detect when source pages change.
3. Store historical source snapshots.
4. Add a human-review workflow before publishing changed information.
5. Increase the dataset from 8 services to hundreds.
6. Add multilingual embeddings for stronger semantic retrieval.
7. Build a larger independent evaluation set.
8. Add analytics for failed and low-confidence searches.
9. Add monitoring and structured logging.
10. Add caching and rate limiting.
11. Add source-level freshness checks.
12. Add Albanian dialect and typo robustness.

## Why the first version does not use an LLM

The first version intentionally uses deterministic retrieval and structured answer generation.

For administrative information, incorrect details can be more harmful than an incomplete answer.

Using structured source data gives several advantages:

- answers are easier to audit
- tests are reproducible
- costs are minimal
- deployment requires no API key
- hallucination risk is lower
- every result can link directly to a source

An LLM could be added later for paraphrasing or conversational interaction while keeping retrieval and source grounding as the authoritative layer.

## Quality measurement

The main quality metric for the current version is retrieval correctness.

For each evaluation question, the system checks whether the expected government service appears:

- at rank 1
- within the top 3 results

MRR@3 also rewards the system for ranking the correct result higher.

This is more appropriate for the current system than measuring generic text-generation quality because the main AI task is mapping a user's natural-language question to the correct public service.

## Example use case

User:

```text
Sa kushton rinovimi ADR?
```

The system:

1. normalizes the Albanian text
2. creates TF-IDF query representations
3. compares the query against service documents
4. applies fuzzy similarity scoring
5. ranks the candidate services
6. selects the highest-confidence result
7. detects that the user is asking about cost
8. returns the stored cost
9. exposes the official source URL

Example output:

```text
Rinovim i Certifikatës së Trajnimit ADR

Kostoja: 6500 lekë.
```

## Application description

A concise description of the project:

> I built ShërbimAI, a grounded NLP assistant that helps Albanian citizens find the correct government service using natural-language questions. The system uses hybrid retrieval combining word and character TF-IDF with fuzzy matching, then generates structured answers from a curated dataset linked to official e-Albania sources. I measured retrieval quality using a labeled evaluation set with Top-1 accuracy, Top-3 recall, and MRR. The current 32-query regression set achieves 100% Top-1 accuracy, although I treat this as a small controlled evaluation rather than a claim of general real-world accuracy. If I rebuilt it for broader production use, I would focus on automated source ingestion and change detection so government-service information stays current without relying on manual updates.

## Disclaimer

ShërbimAI is an independent informational project.

It is not affiliated with or endorsed by e-Albania, AKSHI, or the Albanian government.

Users should always verify:

- eligibility
- required documents
- prices
- processing times
- deadlines
- validity

on the linked official government source before submitting an application.

## License

MIT License.
