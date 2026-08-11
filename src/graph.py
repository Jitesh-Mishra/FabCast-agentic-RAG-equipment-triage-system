from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
import os
from langchain_groq import ChatGroq

from src.monitor import score_latest
from src.rag import retrieve

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, groq_api_key=os.environ.get("GROQ_API_KEY"))


class FabCastState(TypedDict):
    equipment_id: str
    anomaly: Optional[dict]
    diagnosis: Optional[str]
    citations: Optional[list]
    ticket_draft: Optional[str]
    human_decision: Optional[str]


# --- Nodes ---

def monitor_node(state: FabCastState) -> dict:
    result = score_latest(state["equipment_id"])
    print(f"[monitor] {state['equipment_id']}: is_anomaly={result['is_anomaly']} "
          f"severity={result['severity']:.3f} triggered_by={result.get('triggered_by')}")
    return {"anomaly": result}


def diagnosis_node(state: FabCastState) -> dict:
    anomaly = state["anomaly"]
    query = (
        f"Equipment {state['equipment_id']} flagged as anomalous. "
        f"Triggered by: {anomaly.get('triggered_by')}. "
        f"metric4 value: {anomaly.get('metric4_value')}. "
        f"severity score: {anomaly['severity']:.3f}."
    )
    docs = retrieve(query, k=3)
    context = "\n\n".join(f"[{d.metadata['source']}]\n{d.page_content}" for d in docs)

    prompt = f"""You are a maintenance triage assistant. An automated monitor flagged
equipment {state['equipment_id']} as at-risk (triggered by: {anomaly.get('triggered_by')}).

Use ONLY the context below to explain the likely cause. Cite which document
supports your explanation. If the context doesn't clearly explain this
specific case, say so honestly rather than guessing.

Context:
{context}

Write a 3-4 sentence diagnosis for a human reviewer."""

    response = llm.invoke(prompt)
    return {"diagnosis": response.content, "citations": [d.metadata["source"] for d in docs]}


def ticket_node(state: FabCastState) -> dict:
    prompt = f"""Draft a short, structured maintenance work order ticket.

Equipment: {state['equipment_id']}
Diagnosis: {state['diagnosis']}

Format as:
EQUIPMENT: ...
PRIORITY: (high/medium/low, based on the diagnosis)
LIKELY CAUSE: ...
RECOMMENDED ACTION: ...
CONFIDENCE: (state plainly whether this is a strong or weak signal)"""

    response = llm.invoke(prompt)
    return {"ticket_draft": response.content}


def route_after_monitor(state: FabCastState):
    return "diagnosis" if state["anomaly"]["is_anomaly"] else END


# --- Build graph ---
builder = StateGraph(FabCastState)
builder.add_node("monitor", monitor_node)
builder.add_node("diagnosis", diagnosis_node)
builder.add_node("ticket", ticket_node)

builder.set_entry_point("monitor")
builder.add_conditional_edges("monitor", route_after_monitor, {"diagnosis": "diagnosis", END: END})
builder.add_edge("diagnosis", "ticket")
builder.add_edge("ticket", END)

conn = sqlite3.connect("data/checkpoints.sqlite", check_same_thread=False)
checkpointer = SqliteSaver(conn)
graph = builder.compile(checkpointer=checkpointer, interrupt_after=["ticket"])
