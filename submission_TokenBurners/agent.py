from __future__ import annotations

from typing import Any, Optional, cast

from database import ScriptState, get_script
from nodes import (
    check_for_response,
    classify_response,
    escalate,
    extract_revision_notes_node,
    route_after_check,
    route_after_classify,
    route_from_start,
    send_approval_request,
    send_followup,
    update_tracker,
)


_GRAPH = None


def build_graph():
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as error:
        raise RuntimeError(
            "LangGraph is not installed yet. Run `pip install -r requirements.txt` first."
        ) from error

    # StateGraph is the LangGraph object that connects plain Python node functions.
    graph_builder = StateGraph(ScriptState)

    graph_builder.add_node("send_approval_request", send_approval_request)
    graph_builder.add_node("check_for_response", check_for_response)
    graph_builder.add_node("classify_response", classify_response)
    graph_builder.add_node("extract_revision_notes", extract_revision_notes_node)
    graph_builder.add_node("send_followup", send_followup)
    graph_builder.add_node("escalate", escalate)
    graph_builder.add_node("update_tracker", update_tracker)

    graph_builder.add_conditional_edges(
        START,
        route_from_start,
        {
            "send_approval_request": "send_approval_request",
            "check_for_response": "check_for_response",
        },
    )

    graph_builder.add_edge("send_approval_request", END)

    # Conditional edges are LangGraph's branching rules: they inspect state and pick the next node.
    graph_builder.add_conditional_edges(
        "check_for_response",
        route_after_check,
        {
            "classify_response": "classify_response",
            "send_followup": "send_followup",
            "escalate": "escalate",
            "wait": END,
        },
    )

    graph_builder.add_conditional_edges(
        "classify_response",
        route_after_classify,
        {
            "update_tracker": "update_tracker",
            "extract_revision_notes": "extract_revision_notes",
            "escalate": "escalate",
            "send_followup": "send_followup",
        },
    )

    graph_builder.add_edge("extract_revision_notes", END)
    graph_builder.add_edge("send_followup", END)
    graph_builder.add_edge("escalate", END)
    graph_builder.add_edge("update_tracker", END)

    return graph_builder.compile()


def get_agent_graph():
    global _GRAPH

    if _GRAPH is None:
        _GRAPH = build_graph()

    return _GRAPH


def run_script_agent(script_id: str) -> Optional[dict[str, Any]]:
    script = get_script(script_id)
    if script is None:
        return None

    graph = get_agent_graph()
    graph.invoke(cast(ScriptState, script))
    return get_script(script_id)
