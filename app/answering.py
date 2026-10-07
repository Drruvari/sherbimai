from __future__ import annotations

from typing import Any

from .retrieval import normalize


COST_TERMS = {"kushton", "kosto", "tarife", "pagese", "pagese", "falas", "cmim"}
TIME_TERMS = {"zgjat", "kohe", "afati", "sa dite", "sa muaj", "kur del"}
DOC_TERMS = {"dokument", "dokumente", "duhen", "ngarkoj", "kerkohen"}
VALIDITY_TERMS = {"vlefshmeri", "vlefshme", "skadon", "afat vlefshmerie"}
STEP_TERMS = {"si", "hapat", "aplikoj", "behet", "procedura", "ku aplikoj"}


def detect_intents(question: str) -> set[str]:
    q = normalize(question)
    intents: set[str] = set()

    def has_any(terms: set[str]) -> bool:
        return any(term in q for term in terms)

    if has_any(COST_TERMS):
        intents.add("cost")
    if has_any(TIME_TERMS):
        intents.add("time")
    if has_any(DOC_TERMS):
        intents.add("documents")
    if has_any(VALIDITY_TERMS):
        intents.add("validity")
    if has_any(STEP_TERMS):
        intents.add("steps")
    return intents


def _list_md(items: list[str]) -> str:
    if not items:
        return "Nuk kërkohet dokumentacion shoqërues sipas faqes së shërbimit."
    return "\n".join(f"- {item}" for item in items)


def compose_answer(service: dict[str, Any], question: str) -> str:
    intents = detect_intents(question)
    title = service["title"]

    if intents == {"cost"}:
        return f"**{title}**\n\nKostoja: **{service['cost']}**."
    if intents == {"time"}:
        return f"**{title}**\n\nKoha e përpunimit: **{service['processing_time']}**."
    if intents == {"validity"}:
        return f"**{title}**\n\nVlefshmëria: **{service['validity']}**."
    if intents == {"documents"}:
        return f"**{title}**\n\nDokumentet:\n{_list_md(service['documents'])}"

    lines = [
        f"**{title}**",
        "",
        service["description"],
        "",
        f"**Kush mund ta përdorë:** {service['eligibility']}",
    ]

    if "documents" in intents or not intents:
        lines += ["", "**Dokumentet:**", _list_md(service["documents"])]

    if "steps" in intents or not intents:
        lines += ["", "**Hapat:**"]
        lines += [f"{i}. {step}" for i, step in enumerate(service["steps"], start=1)]

    lines += [
        "",
        f"**Koha:** {service['processing_time']}",
        f"**Kostoja:** {service['cost']}",
        f"**Vlefshmëria:** {service['validity']}",
    ]

    if service.get("notes"):
        lines += ["", f"**Shënim:** {service['notes']}"]

    return "\n".join(lines)
