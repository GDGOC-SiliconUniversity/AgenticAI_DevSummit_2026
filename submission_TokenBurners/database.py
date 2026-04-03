from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, NotRequired, Optional, TypedDict, cast

from dotenv import load_dotenv

load_dotenv()


class ScriptState(TypedDict):
    script_id: str
    script_text: str
    client_name: str
    client_contact: str
    account_manager: str
    preferred_channel: str
    sla_hours: int
    status: str
    follow_up_count: int
    client_response: str
    classification: str
    revision_notes: str
    history: list[str]
    sent_at: str
    version: int
    next_action: NotRequired[str]
    escalation_reason: NotRequired[str]


DEFAULT_DATABASE_PATH = "scriptagent.db"
STATE_COLUMNS = (
    "script_id",
    "script_text",
    "client_name",
    "client_contact",
    "account_manager",
    "preferred_channel",
    "sla_hours",
    "status",
    "follow_up_count",
    "client_response",
    "classification",
    "revision_notes",
    "history",
    "sent_at",
    "version",
)
ACTIVE_STATUSES = ("pending_send", "awaiting_response")


def get_database_path() -> str:
    return os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(
        get_database_path(),
        timeout=30,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL;")
    return connection


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso(timestamp: str) -> Optional[datetime]:
    if not timestamp:
        return None

    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed


def hours_since(timestamp: str, current_time: Optional[str] = None) -> float:
    start_time = parse_iso(timestamp)
    end_time = parse_iso(current_time) if current_time else datetime.now(timezone.utc)

    if start_time is None:
        return 0.0

    if end_time is None:
        end_time = datetime.now(timezone.utc)

    delta = end_time - start_time
    return delta.total_seconds() / 3600


def append_history(state: ScriptState, message: str, timestamp: Optional[str] = None) -> None:
    entry_time = timestamp or now_iso()
    history = list(state.get("history", []))
    history.append(f"[{entry_time}] {message}")
    state["history"] = history


def _normalize_history(raw_history: Any) -> list[str]:
    if isinstance(raw_history, list):
        return [str(item) for item in raw_history]

    if isinstance(raw_history, str):
        try:
            decoded = json.loads(raw_history)
        except json.JSONDecodeError:
            return [raw_history] if raw_history else []
        return [str(item) for item in decoded]

    return []


def _row_to_record(row: sqlite3.Row) -> dict[str, Any]:
    history = _normalize_history(row["history"])
    state: ScriptState = {
        "script_id": str(row["script_id"]),
        "script_text": str(row["script_text"]),
        "client_name": str(row["client_name"]),
        "client_contact": str(row["client_contact"]),
        "account_manager": str(row["account_manager"]),
        "preferred_channel": str(row["preferred_channel"]),
        "sla_hours": int(row["sla_hours"]),
        "status": str(row["status"]),
        "follow_up_count": int(row["follow_up_count"]),
        "client_response": str(row["client_response"] or ""),
        "classification": str(row["classification"] or ""),
        "revision_notes": str(row["revision_notes"] or ""),
        "history": history,
        "sent_at": str(row["sent_at"] or ""),
        "version": int(row["version"]),
    }

    return {
        **state,
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
        "response_processed": bool(row["response_processed"]),
    }


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    payload = cast(dict[str, Any], {key: record[key] for key in STATE_COLUMNS if key != "history"})
    payload["history"] = list(record["history"])
    payload["created_at"] = record["created_at"]
    payload["updated_at"] = record["updated_at"]
    return payload


def _persist_record(
    connection: sqlite3.Connection,
    state: ScriptState,
    *,
    created_at: str,
    updated_at: str,
    response_processed: bool,
) -> None:
    connection.execute(
        """
        INSERT INTO scripts (
            script_id,
            script_text,
            client_name,
            client_contact,
            account_manager,
            preferred_channel,
            sla_hours,
            status,
            follow_up_count,
            client_response,
            classification,
            revision_notes,
            history,
            sent_at,
            version,
            created_at,
            updated_at,
            response_processed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(script_id) DO UPDATE SET
            script_text = excluded.script_text,
            client_name = excluded.client_name,
            client_contact = excluded.client_contact,
            account_manager = excluded.account_manager,
            preferred_channel = excluded.preferred_channel,
            sla_hours = excluded.sla_hours,
            status = excluded.status,
            follow_up_count = excluded.follow_up_count,
            client_response = excluded.client_response,
            classification = excluded.classification,
            revision_notes = excluded.revision_notes,
            history = excluded.history,
            sent_at = excluded.sent_at,
            version = excluded.version,
            updated_at = excluded.updated_at,
            response_processed = excluded.response_processed
        """,
        (
            state["script_id"],
            state["script_text"],
            state["client_name"],
            state["client_contact"],
            state["account_manager"],
            state["preferred_channel"],
            state["sla_hours"],
            state["status"],
            state["follow_up_count"],
            state["client_response"],
            state["classification"],
            state["revision_notes"],
            json.dumps(state["history"]),
            state["sent_at"],
            state["version"],
            created_at,
            updated_at,
            int(response_processed),
        ),
    )


def init_database() -> None:
    connection = get_connection()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scripts (
                script_id TEXT PRIMARY KEY,
                script_text TEXT NOT NULL,
                client_name TEXT NOT NULL,
                client_contact TEXT NOT NULL,
                account_manager TEXT NOT NULL,
                preferred_channel TEXT NOT NULL,
                sla_hours INTEGER NOT NULL DEFAULT 48,
                status TEXT NOT NULL,
                follow_up_count INTEGER NOT NULL DEFAULT 0,
                client_response TEXT NOT NULL DEFAULT '',
                classification TEXT NOT NULL DEFAULT '',
                revision_notes TEXT NOT NULL DEFAULT '',
                history TEXT NOT NULL DEFAULT '[]',
                sent_at TEXT NOT NULL DEFAULT '',
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                response_processed INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def create_or_resubmit_script(submission: dict[str, Any]) -> dict[str, Any]:
    timestamp = now_iso()
    normalized_channel = str(submission["preferred_channel"]).strip().lower() or "email"
    connection = get_connection()

    try:
        existing_row = connection.execute(
            "SELECT * FROM scripts WHERE script_id = ?",
            (submission["script_id"],),
        ).fetchone()

        if existing_row:
            existing_record = _row_to_record(existing_row)
            version = int(existing_record["version"]) + 1
            created_at = str(existing_record["created_at"])
            history = list(existing_record["history"])
            history.append(f"[{timestamp}] Script resubmitted as version {version}.")
        else:
            version = 1
            created_at = timestamp
            history = [f"[{timestamp}] Script submission received."]

        state: ScriptState = {
            "script_id": str(submission["script_id"]),
            "script_text": str(submission["script_text"]),
            "client_name": str(submission["client_name"]),
            "client_contact": str(submission["client_contact"]),
            "account_manager": str(submission["account_manager"]),
            "preferred_channel": normalized_channel,
            "sla_hours": int(submission.get("sla_hours", 48) or 48),
            "status": "pending_send",
            "follow_up_count": 0,
            "client_response": "",
            "classification": "",
            "revision_notes": "",
            "history": history,
            "sent_at": "",
            "version": version,
        }

        _persist_record(
            connection,
            state,
            created_at=created_at,
            updated_at=timestamp,
            response_processed=True,
        )
        connection.commit()

        stored_row = connection.execute(
            "SELECT * FROM scripts WHERE script_id = ?",
            (submission["script_id"],),
        ).fetchone()
        return _public_record(_row_to_record(stored_row))
    finally:
        connection.close()


def save_script_state(state: ScriptState, response_processed: Optional[bool] = None) -> dict[str, Any]:
    timestamp = now_iso()
    connection = get_connection()

    try:
        existing_row = connection.execute(
            "SELECT * FROM scripts WHERE script_id = ?",
            (state["script_id"],),
        ).fetchone()

        created_at = timestamp
        processed_flag = True if response_processed is None else response_processed

        if existing_row:
            existing_record = _row_to_record(existing_row)
            created_at = str(existing_record["created_at"])
            if response_processed is None:
                processed_flag = bool(existing_record["response_processed"])

        _persist_record(
            connection,
            state,
            created_at=created_at,
            updated_at=timestamp,
            response_processed=processed_flag,
        )
        connection.commit()

        stored_row = connection.execute(
            "SELECT * FROM scripts WHERE script_id = ?",
            (state["script_id"],),
        ).fetchone()
        return _public_record(_row_to_record(stored_row))
    finally:
        connection.close()


def get_script_record(script_id: str) -> Optional[dict[str, Any]]:
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM scripts WHERE script_id = ?",
            (script_id,),
        ).fetchone()
        if row is None:
            return None
        return _row_to_record(row)
    finally:
        connection.close()


def get_script(script_id: str) -> Optional[dict[str, Any]]:
    record = get_script_record(script_id)
    if record is None:
        return None
    return _public_record(record)


def list_scripts() -> list[dict[str, Any]]:
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT * FROM scripts ORDER BY updated_at DESC"
        ).fetchall()
        return [_public_record(_row_to_record(row)) for row in rows]
    finally:
        connection.close()


def list_active_script_ids() -> list[str]:
    placeholders = ", ".join("?" for _ in ACTIVE_STATUSES)
    connection = get_connection()
    try:
        rows = connection.execute(
            f"SELECT script_id FROM scripts WHERE status IN ({placeholders}) ORDER BY updated_at ASC",
            ACTIVE_STATUSES,
        ).fetchall()
        return [str(row["script_id"]) for row in rows]
    finally:
        connection.close()


def store_client_response(script_id: str, response: str) -> Optional[dict[str, Any]]:
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM scripts WHERE script_id = ?",
            (script_id,),
        ).fetchone()

        if row is None:
            return None

        record = _row_to_record(row)
        state = cast(ScriptState, {key: record[key] for key in STATE_COLUMNS if key != "history"})
        state["history"] = list(record["history"])
        state["client_response"] = response.strip()
        append_history(state, "Client response captured for review.")

        _persist_record(
            connection,
            state,
            created_at=str(record["created_at"]),
            updated_at=now_iso(),
            response_processed=False,
        )
        connection.commit()

        stored_row = connection.execute(
            "SELECT * FROM scripts WHERE script_id = ?",
            (script_id,),
        ).fetchone()
        return _public_record(_row_to_record(stored_row))
    finally:
        connection.close()


def seed_scripts(records: list[dict[str, Any]]) -> None:
    if not records:
        return

    connection = get_connection()
    try:
        for record in records:
            state: ScriptState = {
                "script_id": str(record["script_id"]),
                "script_text": str(record["script_text"]),
                "client_name": str(record["client_name"]),
                "client_contact": str(record["client_contact"]),
                "account_manager": str(record["account_manager"]),
                "preferred_channel": str(record["preferred_channel"]),
                "sla_hours": int(record["sla_hours"]),
                "status": str(record["status"]),
                "follow_up_count": int(record["follow_up_count"]),
                "client_response": str(record.get("client_response", "")),
                "classification": str(record.get("classification", "")),
                "revision_notes": str(record.get("revision_notes", "")),
                "history": list(record.get("history", [])),
                "sent_at": str(record.get("sent_at", "")),
                "version": int(record.get("version", 1)),
            }
            _persist_record(
                connection,
                state,
                created_at=str(record.get("created_at", now_iso())),
                updated_at=str(record.get("updated_at", now_iso())),
                response_processed=bool(record.get("response_processed", True)),
            )

        connection.commit()
    finally:
        connection.close()


def is_database_empty() -> bool:
    connection = get_connection()
    try:
        row = connection.execute("SELECT COUNT(*) AS count FROM scripts").fetchone()
        return int(row["count"]) == 0
    finally:
        connection.close()
