from __future__ import annotations

import os
import re
from typing import Iterable, Optional

from dotenv import load_dotenv

load_dotenv()


DEFAULT_MODEL_NAME = "gemini-2.5-flash"
ALLOWED_CLASSIFICATIONS = {
    "approved",
    "revisions",
    "rejected",
    "call_requested",
    "unclear",
}


def _configured_api_keys() -> list[str]:
    keys = [
        os.getenv("GEMINI_API_KEY", "").strip(),
        os.getenv("GEMINI_API_KEY_BACKUP", "").strip(),
    ]
    return [key for key in keys if key]


def _iter_clients() -> Iterable[object]:
    api_keys = _configured_api_keys()

    if not api_keys:
        return []

    try:
        from google import genai
    except ImportError:
        return []

    clients: list[object] = []
    for api_key in api_keys:
        try:
            clients.append(genai.Client(api_key=api_key))
        except Exception:
            continue
    return clients


def _normalize_classification(raw_value: str) -> str:
    cleaned = raw_value.strip().lower()
    cleaned = re.sub(r"[^a-z_]", "", cleaned)

    if cleaned in ALLOWED_CLASSIFICATIONS:
        return cleaned

    if cleaned in {"approve", "approvedresponse"}:
        return "approved"
    if cleaned in {"revision", "changes", "change_requested"}:
        return "revisions"
    if cleaned in {"reject", "rejection"}:
        return "rejected"
    if cleaned in {"call", "callrequest"}:
        return "call_requested"

    return "unclear"


def _contains_any(text: str, patterns: list[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def _heuristic_classification(client_response: str) -> str:
    message = client_response.strip()
    lowered = message.lower()

    if not message:
        return "unclear"

    approval_emojis = ["👍", "✅", "👌", "🔥", "💯", "🙌"]
    if message in approval_emojis:
        return "approved"

    call_patterns = [
        "jump on a call",
        "hop on a call",
        "schedule a call",
        "book a call",
        "discuss this on a call",
        "talk this through",
        "can we talk",
        "can we chat",
        "call me",
        "let's connect",
        "meeting",
        "zoom",
    ]
    if _contains_any(lowered, call_patterns) or ("call" in lowered and "recall" not in lowered):
        return "call_requested"

    rejection_patterns = [
        "reject",
        "rejected",
        "not a fit",
        "doesn't work",
        "does not work",
        "don't want",
        "do not want",
        "no go",
        "pass on this",
        "skip this",
        "scrap this",
        "kill this",
        "not approved",
    ]
    if _contains_any(lowered, rejection_patterns):
        return "rejected"

    revision_patterns = [
        "can you",
        "could you",
        "please change",
        "please update",
        "please make",
        "change ",
        "update ",
        "revise",
        "edit ",
        "add ",
        "remove ",
        "swap ",
        "adjust ",
        "fix ",
        "rewrite ",
        "tone down",
        "make the",
        "hook",
        "cta",
        "almost",
        "but ",
        "also ",
        "feels weak",
        "needs work",
    ]
    if _contains_any(lowered, revision_patterns):
        return "revisions"

    exact_approval_patterns = {
        "approved",
        "fine by me",
        "k",
        "ok",
        "okay",
        "send it",
        "ship it",
        "sure",
        "yes",
        "yep",
        "yup",
    }
    if lowered in exact_approval_patterns:
        return "approved"

    approval_patterns = [
        "looks good",
        "looks great",
        "lgtm",
        "all good",
        "good to go",
        "go ahead",
        "works for me",
        "perfect",
    ]
    if _contains_any(lowered, approval_patterns):
        return "approved"

    if any(emoji in message for emoji in approval_emojis):
        return "approved"

    return "unclear"


def _cleanup_revision_note(note: str) -> str:
    cleaned = note.strip(" ,.-")
    cleaned = re.sub(
        r"^(almost perfect but|this is perfect but|looks good but|but|also|and)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"^(can you|could you|please|maybe|just)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    if not cleaned:
        return ""

    if len(cleaned) == 1:
        return cleaned.upper()

    return cleaned[0].upper() + cleaned[1:]


def _heuristic_revision_notes(client_response: str) -> str:
    normalized_text = " ".join(client_response.strip().split())
    if not normalized_text:
        return "1. [UNCLEAR] Client asked for revisions but no details were captured."

    chunks = re.split(r"[?!.\n]|(?:\s+also\s+)", normalized_text, flags=re.IGNORECASE)
    notes: list[str] = []
    request_markers = [
        "can you",
        "could you",
        "change",
        "update",
        "make",
        "add",
        "remove",
        "swap",
        "edit",
        "fix",
        "rewrite",
        "feels ",
        "too ",
        "needs ",
        "hook",
        "cta",
    ]

    for chunk in chunks:
        lowered = chunk.lower().strip()
        if not lowered:
            continue

        if _contains_any(lowered, request_markers):
            cleaned = _cleanup_revision_note(chunk)
            if cleaned:
                notes.append(cleaned)

    deduped: list[str] = []
    seen: set[str] = set()
    for note in notes:
        normalized = note.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(note)

    if not deduped:
        deduped = [f"[UNCLEAR] {normalized_text}"]

    return "\n".join(f"{index}. {note}" for index, note in enumerate(deduped, start=1))


def _generate_with_gemini(prompt: str) -> Optional[str]:
    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL_NAME)

    for client in _iter_clients():
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            text = getattr(response, "text", "") or ""
            if text.strip():
                return text.strip()
        except Exception as error:
            print(f"[classifier] Gemini request failed, trying next configured key: {error}")
            continue

    return None


def _normalize_revision_notes(raw_text: str) -> str:
    cleaned_lines: list[str] = []

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^\d+\.", stripped):
            cleaned_lines.append(stripped)

    if cleaned_lines:
        return "\n".join(cleaned_lines)

    return raw_text.strip()


def classify_client_response(client_response: str) -> str:
    prompt = f"""
You are classifying a client response to a content script approval request.

Classify the response into exactly one of these categories:
- approved: Client is happy with the script (includes informal approval like "looks good", "perfect", thumbs up emoji, "yes", "send it")
- revisions: Client wants changes (includes partial feedback, "can you change X", "almost but...")
- rejected: Client does not want this script at all
- call_requested: Client wants to discuss over a call before deciding
- unclear: Cannot determine intent from this message

Client response: "{client_response}"

Return ONLY the category word. Nothing else.
""".strip()

    generated = _generate_with_gemini(prompt)
    if generated:
        return _normalize_classification(generated)

    return _heuristic_classification(client_response)


def extract_revision_notes(client_response: str) -> str:
    prompt = f"""
A client has requested revisions to a content script.
Extract their specific revision requests as a numbered list.
Be precise - only include what they explicitly asked for.
If a request is ambiguous, flag it with [UNCLEAR].

Client message: "{client_response}"

Return a numbered list of revision requests only.
""".strip()

    generated = _generate_with_gemini(prompt)
    if generated:
        return _normalize_revision_notes(generated)

    return _heuristic_revision_notes(client_response)
