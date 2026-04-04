from __future__ import annotations

from typing import Any, cast

from classifier import classify_client_response, extract_revision_notes
from database import (
    STATE_COLUMNS,
    ScriptState,
    append_history,
    get_script_record,
    hours_since,
    now_iso,
    save_script_state,
)
from email_service import send_email


def _copy_state(record: dict[str, Any]) -> ScriptState:
    state = cast(ScriptState, {key: record[key] for key in STATE_COLUMNS if key != "history"})
    state["history"] = list(record["history"])
    return state


def _print_event(title: str, body: str) -> None:
    print(f"\n=== {title} ===\n{body}\n")


def _format_approval_message(state: ScriptState) -> str:
    if state["preferred_channel"] == "whatsapp":
        return (
            f"Hi {state['client_name']}! Sharing script v{state['version']} for approval.\n\n"
            f"{state['script_text']}\n\n"
            "Reply here with approval or revision notes and we will route it immediately."
        )

    return (
        f"Subject: Script Approval Request - {state['client_name']} - v{state['version']}\n\n"
        f"Hi {state['client_name']},\n\n"
        "Please review the script below and reply with approval or any revision notes.\n\n"
        f"{state['script_text']}\n\n"
        "Thanks,\nScriptAgent"
    )


def _extract_email_subject_and_body(message: str) -> tuple[str, str]:
    if message.startswith("Subject: "):
        subject, _, body = message.partition("\n\n")
        return subject.replace("Subject: ", "", 1).strip(), body.strip()
    return "ScriptAgent update", message


def _send_email_if_needed(state: ScriptState, message: str) -> None:
    if state["preferred_channel"] != "email":
        return

    subject, body = _extract_email_subject_and_body(message)
    response = send_email(
        to_email=state["client_contact"],
        subject=subject,
        text_body=body,
    )
    email_id = response.get("id", "unknown")
    append_history(state, f"Email queued via Resend with id {email_id}.")


def _format_followup_message(state: ScriptState, hours_elapsed: float) -> tuple[str, int]:
    if hours_elapsed >= 48:
        return (
            "Quick follow-up: production timing is now at risk without approval on this script. "
            "Please reply with approval, revisions, or a call request when you can.",
            2,
        )

    return (
        "Just checking in on the script approval request. "
        "When you have a moment, please reply with approval or any changes you want.",
        1,
    )


def route_from_start(state: ScriptState) -> str:
    if state.get("status") == "pending_send" or not state.get("sent_at"):
        return "send_approval_request"
    return "check_for_response"


def route_after_check(state: ScriptState) -> str:
    return cast(str, state.get("next_action", "wait"))


def route_after_classify(state: ScriptState) -> str:
    classification = state.get("classification", "")

    if classification == "approved":
        return "update_tracker"
    if classification == "revisions":
        return "extract_revision_notes"
    if classification == "rejected":
        return "escalate"
    if classification == "call_requested":
        return "escalate"
    return "send_followup"


def send_approval_request(state: ScriptState) -> ScriptState:
    sent_at = now_iso()
    state["status"] = "awaiting_response"
    state["sent_at"] = sent_at
    append_history(
        state,
        f"Approval request sent to {state['client_name']} via {state['preferred_channel']} at {sent_at}.",
        timestamp=sent_at,
    )

    message = _format_approval_message(state)
    email_error: str | None = None
    if state["preferred_channel"] == "email":
        try:
            _send_email_if_needed(state, message)
        except Exception as error:
            email_error = str(error)
            append_history(state, f"Resend delivery failed: {email_error}")

    _print_event(
        "SEND APPROVAL REQUEST",
        (
            f"Client: {state['client_name']}\n"
            f"Channel: {state['preferred_channel']}\n"
            f"Contact: {state['client_contact']}\n"
            f"Email delivery: {'queued via Resend' if email_error is None and state['preferred_channel'] == 'email' else email_error or 'mock only'}\n"
            f"Message:\n{message}"
        ),
    )

    save_script_state(state, response_processed=True)
    return state


def check_for_response(state: ScriptState) -> ScriptState:
    latest_record = get_script_record(state["script_id"])
    if latest_record is None:
        state["next_action"] = "wait"
        return state

    refreshed_state = _copy_state(latest_record)

    if refreshed_state["client_response"] and not latest_record["response_processed"]:
        refreshed_state["next_action"] = "classify_response"
        return refreshed_state

    elapsed_hours = hours_since(refreshed_state["sent_at"])

    if elapsed_hours >= 72:
        refreshed_state["next_action"] = "escalate"
        refreshed_state["escalation_reason"] = "sla_breach"
        return refreshed_state

    if elapsed_hours >= 48 and refreshed_state["follow_up_count"] < 2:
        refreshed_state["next_action"] = "send_followup"
        return refreshed_state

    if elapsed_hours >= 24 and refreshed_state["follow_up_count"] < 1:
        refreshed_state["next_action"] = "send_followup"
        return refreshed_state

    refreshed_state["next_action"] = "wait"
    return refreshed_state


def classify_response(state: ScriptState) -> ScriptState:
    classification = classify_client_response(state["client_response"])
    state["classification"] = classification
    append_history(state, f'Client response classified as "{classification}".')

    _print_event(
        "CLASSIFY RESPONSE",
        (
            f"Script ID: {state['script_id']}\n"
            f"Raw response: {state['client_response']}\n"
            f"Classification: {classification}"
        ),
    )

    save_script_state(state, response_processed=True)
    return state


def extract_revision_notes_node(state: ScriptState) -> ScriptState:
    notes = extract_revision_notes(state["client_response"])
    state["revision_notes"] = notes
    state["status"] = "needs_revision"
    append_history(state, "Revision notes extracted and routed to the scriptwriter.")

    _print_event(
        "EXTRACT REVISION NOTES",
        (
            f"Script ID: {state['script_id']}\n"
            f"Client: {state['client_name']}\n"
            f"Revision notes:\n{notes}"
        ),
    )

    save_script_state(state, response_processed=True)
    return state


def send_followup(state: ScriptState) -> ScriptState:
    if state.get("classification") == "unclear":
        message = (
            "Thanks for the quick reply. I want to make sure we interpret it correctly. "
            "Could you confirm if the script is approved, needs revisions, or should be discussed on a call?"
        )
        append_history(state, "Sent clarification follow-up after an unclear client response.")
        state["classification"] = ""
        delivery_label = "mock only"
        if state["preferred_channel"] == "email":
            try:
                _send_email_if_needed(
                    state,
                    f"Subject: Clarification Needed - {state['client_name']} - {state['script_id']}\n\nHi {state['client_name']},\n\n{message}\n\nThanks,\nScriptAgent",
                )
                delivery_label = "queued via Resend"
            except Exception as error:
                delivery_label = f"failed ({error})"
                append_history(state, f"Resend delivery failed: {error}")
        _print_event(
            "SEND FOLLOW-UP",
            (
                f"Script ID: {state['script_id']}\n"
                f"Type: clarification\n"
                f"Client: {state['client_name']}\n"
                f"Email delivery: {delivery_label}\n"
                f"Message:\n{message}"
            ),
        )
        state["status"] = "awaiting_response"
        save_script_state(state, response_processed=True)
        return state

    elapsed_hours = hours_since(state["sent_at"])
    message, target_follow_up_count = _format_followup_message(state, elapsed_hours)
    state["follow_up_count"] = max(state["follow_up_count"], target_follow_up_count)
    state["status"] = "awaiting_response"
    delivery_label = "mock only"

    if target_follow_up_count == 1:
        append_history(state, "Sent first follow-up after 24 hours with no response.")
    else:
        append_history(state, "Sent second follow-up after 48 hours with no response.")

    if state["preferred_channel"] == "email":
        try:
            _send_email_if_needed(
                state,
                f"Subject: Follow-up on Script Approval - {state['client_name']} - {state['script_id']}\n\nHi {state['client_name']},\n\n{message}\n\nThanks,\nScriptAgent",
            )
            delivery_label = "queued via Resend"
        except Exception as error:
            delivery_label = f"failed ({error})"
            append_history(state, f"Resend delivery failed: {error}")

    _print_event(
        "SEND FOLLOW-UP",
        (
            f"Script ID: {state['script_id']}\n"
            f"Client: {state['client_name']}\n"
            f"Follow-up count: {state['follow_up_count']}\n"
            f"Email delivery: {delivery_label}\n"
            f"Message:\n{message}"
        ),
    )

    save_script_state(state, response_processed=True)
    return state


def escalate(state: ScriptState) -> ScriptState:
    classification = state.get("classification", "")
    escalation_reason = cast(str, state.get("escalation_reason", ""))

    if classification == "rejected":
        state["status"] = "rejected"
        append_history(state, "Escalated to the account manager after client rejection.")
        alert_reason = "Client rejected the script."
    elif classification == "call_requested":
        state["status"] = "call_requested"
        append_history(state, "Escalated to the account manager to schedule a client call.")
        alert_reason = "Client requested a call before approving."
    else:
        state["status"] = "escalated"
        append_history(state, "Escalated to the account manager after 72 hours with no response.")
        alert_reason = "No client response within 72 hours."

    history_text = "\n".join(state["history"])
    _print_event(
        "ESCALATE",
        (
            f"Script ID: {state['script_id']}\n"
            f"Client: {state['client_name']}\n"
            f"Account Manager: {state['account_manager']}\n"
            f"Reason: {alert_reason}\n"
            f"Classification: {classification or escalation_reason or 'n/a'}\n"
            f"Response: {state['client_response'] or 'No response captured'}\n"
            f"History:\n{history_text}"
        ),
    )

    save_script_state(state, response_processed=True)
    return state


def update_tracker(state: ScriptState) -> ScriptState:
    state["status"] = "approved"
    append_history(state, "Moved to production queue.")

    _print_event(
        "UPDATE TRACKER",
        (
            f"Script ID: {state['script_id']}\n"
            f"Client: {state['client_name']}\n"
            "Result: Script approved and producer notified."
        ),
    )

    save_script_state(state, response_processed=True)
    return state
