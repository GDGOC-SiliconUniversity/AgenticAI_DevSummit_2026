from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def _get_resend_api_key() -> str:
    return (
        os.getenv("RESEND_API_KEY", "").strip()
        or os.getenv("resen_api_key", "").strip()
        or os.getenv("RESEND_APIKEY", "").strip()
    )


def _plain_text_to_html(text: str) -> str:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return "<br>".join(escaped.splitlines())


def send_email(*, to_email: str, subject: str, text_body: str, reply_to: Optional[str] = None) -> dict:
    api_key = _get_resend_api_key()
    if not api_key:
        raise RuntimeError("Resend API key is missing. Set RESEND_API_KEY in .env.")

    try:
        import resend
    except ImportError as error:
        raise RuntimeError("Resend SDK is not installed. Run `pip install -r requirements.txt`.") from error

    resend.api_key = api_key

    from_email = os.getenv("RESEND_FROM_EMAIL", "ScriptAgent <onboarding@resend.dev>")
    params: resend.Emails.SendParams = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "text": text_body,
        "html": f"<div style=\"font-family: monospace; line-height: 1.6;\">{_plain_text_to_html(text_body)}</div>",
    }

    if reply_to:
        params["reply_to"] = reply_to

    return resend.Emails.send(params)
