from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def _iso_at(base_time: datetime, offset_hours: int) -> str:
    return (base_time + timedelta(hours=offset_hours)).replace(microsecond=0).isoformat()


LIVE_DEMO_SUBMISSIONS = {
    "glowskin": {
        "script_id": "SCR-001",
        "script_text": "Hook: Have you ever spent money on skincare that never matched your skin? Body: GlowSkin's AI routine builder personalizes your regimen in minutes. CTA: Try your free skin analysis today.",
        "client_name": "GlowSkin",
        "client_contact": "priya@glowskin.com",
        "account_manager": "Rohit",
        "preferred_channel": "email",
        "sla_hours": 48,
    },
    "finwave": {
        "script_id": "SCR-002",
        "script_text": "Hook: Most freelancers lose money in hidden payment fees. Body: FinWave helps you invoice globally and see every fee upfront. CTA: Open your cross-border account this week.",
        "client_name": "FinWave",
        "client_contact": "ananya@finwave.io",
        "account_manager": "Rohit",
        "preferred_channel": "whatsapp",
        "sla_hours": 48,
    },
}


def build_demo_scripts() -> list[dict[str, Any]]:
    base_time = datetime.now(timezone.utc)

    return [
        {
            "script_id": "DEMO-WAIT-001",
            "script_text": "Hook: Your team's approvals should not live in one person's head. Body: ScriptAgent automatically chases client sign-off and classifies what they really mean. CTA: See every approval in one dashboard.",
            "client_name": "Orbit Media",
            "client_contact": "maya@orbitmedia.co",
            "account_manager": "Rohit",
            "preferred_channel": "email",
            "sla_hours": 48,
            "status": "awaiting_response",
            "follow_up_count": 0,
            "client_response": "",
            "classification": "",
            "revision_notes": "",
            "history": [
                f"[{_iso_at(base_time, -12)}] Script submission received.",
                f"[{_iso_at(base_time, -11)}] Approval request sent to Orbit Media via email at {_iso_at(base_time, -11)}.",
            ],
            "sent_at": _iso_at(base_time, -11),
            "version": 1,
            "created_at": _iso_at(base_time, -12),
            "updated_at": _iso_at(base_time, -11),
            "response_processed": True,
        },
        {
            "script_id": "DEMO-REV-001",
            "script_text": "Hook: Manual follow-ups steal hours from every content lead. Body: ScriptAgent keeps scripts moving with automatic reminders and smart response routing. CTA: Launch your approval command center.",
            "client_name": "Northstar Ads",
            "client_contact": "tanya@northstarads.com",
            "account_manager": "Meera",
            "preferred_channel": "whatsapp",
            "sla_hours": 48,
            "status": "needs_revision",
            "follow_up_count": 0,
            "client_response": "almost perfect but can you make the hook more punchy? also the CTA feels weak",
            "classification": "revisions",
            "revision_notes": "1. Make the hook more punchy\n2. The CTA feels weak",
            "history": [
                f"[{_iso_at(base_time, -20)}] Script submission received.",
                f"[{_iso_at(base_time, -19)}] Approval request sent to Northstar Ads via whatsapp at {_iso_at(base_time, -19)}.",
                f"[{_iso_at(base_time, -18)}] Client response captured for review.",
                f"[{_iso_at(base_time, -18)}] Client response classified as \"revisions\".",
                f"[{_iso_at(base_time, -18)}] Revision notes extracted and routed to the scriptwriter.",
            ],
            "sent_at": _iso_at(base_time, -19),
            "version": 1,
            "created_at": _iso_at(base_time, -20),
            "updated_at": _iso_at(base_time, -18),
            "response_processed": True,
        },
        {
            "script_id": "DEMO-OVERDUE-001",
            "script_text": "Hook: Approval delays are invisible until launch day. Body: ScriptAgent spots silence, follows up automatically, and escalates before deadlines slip. CTA: Give your account team a live status board.",
            "client_name": "Peak Commerce",
            "client_contact": "ops@peakcommerce.com",
            "account_manager": "Aisha",
            "preferred_channel": "email",
            "sla_hours": 48,
            "status": "awaiting_response",
            "follow_up_count": 2,
            "client_response": "",
            "classification": "",
            "revision_notes": "",
            "history": [
                f"[{_iso_at(base_time, -75)}] Script submission received.",
                f"[{_iso_at(base_time, -73)}] Approval request sent to Peak Commerce via email at {_iso_at(base_time, -73)}.",
                f"[{_iso_at(base_time, -49)}] Sent first follow-up after 24 hours with no response.",
                f"[{_iso_at(base_time, -25)}] Sent second follow-up after 48 hours with no response.",
            ],
            "sent_at": _iso_at(base_time, -73),
            "version": 1,
            "created_at": _iso_at(base_time, -75),
            "updated_at": _iso_at(base_time, -25),
            "response_processed": True,
        },
    ]
