from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

from agent import run_script_agent
from database import (
    create_or_resubmit_script,
    get_script,
    init_database,
    is_database_empty,
    list_active_script_ids,
    list_scripts,
    seed_scripts,
    store_client_response,
)
from mock_clients import build_demo_scripts


def get_poll_interval_seconds() -> int:
    raw_value = os.getenv("POLL_INTERVAL_SECONDS", "10").strip()

    try:
        return max(1, int(raw_value))
    except ValueError:
        return 10


class SubmitScriptRequest(BaseModel):
    script_id: str = Field(..., min_length=1)
    script_text: str = Field(..., min_length=1)
    client_name: str = Field(..., min_length=1)
    client_contact: str = Field(..., min_length=1)
    account_manager: str = Field(..., min_length=1)
    preferred_channel: Literal["email", "whatsapp"]
    sla_hours: int = Field(default=48, ge=1)


class ClientResponseRequest(BaseModel):
    script_id: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)


class ScriptResponse(BaseModel):
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
    created_at: str
    updated_at: str


class DashboardResponse(BaseModel):
    scripts: list[ScriptResponse]


async def run_agent_sweep() -> None:
    for script_id in list_active_script_ids():
        try:
            run_script_agent(script_id)
        except Exception as error:
            print(f"[poller] Failed to process {script_id}: {error}")


async def poll_active_scripts(stop_event: asyncio.Event) -> None:
    interval_seconds = get_poll_interval_seconds()

    while not stop_event.is_set():
        await run_agent_sweep()

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()

    if is_database_empty():
        seed_scripts(build_demo_scripts())
        print("[startup] Seeded demo scripts.")

    await run_agent_sweep()

    stop_event = asyncio.Event()
    poller_task = asyncio.create_task(poll_active_scripts(stop_event))

    try:
        yield
    finally:
        stop_event.set()
        await poller_task


app = FastAPI(
    title="ScriptAgent",
    description="Content approval loop automator built with FastAPI, SQLite, and LangGraph.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "ScriptAgent is running."}


@app.post("/submit", response_model=ScriptResponse)
def submit_script(request: SubmitScriptRequest) -> dict:
    create_or_resubmit_script(request.model_dump())
    updated_script = run_script_agent(request.script_id)

    if updated_script is None:
        raise HTTPException(status_code=500, detail="Script was created but could not be processed.")

    return updated_script


@app.post("/respond", response_model=ScriptResponse)
def respond_to_script(request: ClientResponseRequest) -> dict:
    existing_script = get_script(request.script_id)
    if existing_script is None:
        raise HTTPException(status_code=404, detail="Script not found.")

    if existing_script["status"] in {"approved", "rejected", "needs_revision", "call_requested"}:
        raise HTTPException(
            status_code=409,
            detail=f"Script is already in final status '{existing_script['status']}'. Resubmit it to start a new version.",
        )

    stored_script = store_client_response(request.script_id, request.response)
    if stored_script is None:
        raise HTTPException(status_code=404, detail="Script not found.")

    updated_script = run_script_agent(request.script_id)
    if updated_script is None:
        raise HTTPException(status_code=500, detail="Client response was stored but could not be processed.")

    return updated_script


@app.get("/status/{script_id}", response_model=ScriptResponse)
def get_status(script_id: str) -> dict:
    script = get_script(script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found.")
    return script


@app.get("/dashboard", response_model=DashboardResponse)
def dashboard() -> dict[str, list[dict]]:
    return {"scripts": list_scripts()}
