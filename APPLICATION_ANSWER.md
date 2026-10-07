# Application answer

Use this only after the project is publicly deployed. Do not claim usage or users you do not have.

I built ShërbimAI, a grounded NLP assistant that helps Albanian citizens find and understand public services without knowing the exact administrative terminology used by government portals. A user can ask a question in natural Albanian, such as how to register a child for first grade or obtain a consular document, and the system retrieves the most relevant curated service, returns the requirements and procedure, and links directly to the official e-Albania source.

I measured retrieval quality with a labeled evaluation set of 32 Albanian questions covering the eight services in the first release. The current version achieves 100% Top-1 accuracy, 100% Top-3 recall, and 1.000 MRR@3 on that regression set. I also added confidence gating, API tests, source validation, and CI so changes to the retriever or dataset are checked automatically. I treat the small evaluation set as a regression benchmark rather than evidence of general population accuracy.

If I rebuilt it, I would invest first in the data pipeline. The current release uses a deliberately curated service set so every answer is traceable. The next step would be automated ingestion and change detection for official sources, followed by human review and a much larger evaluation set covering misspellings, dialect variation, ambiguous requests, and out-of-scope questions.
