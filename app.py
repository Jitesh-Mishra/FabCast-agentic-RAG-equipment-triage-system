import time
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()  # local dev: reads GROQ_API_KEY from a .env file if present
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass  # no secrets.toml locally -- fine, .env above already covered it

import duckdb
import pandas as pd
from datetime import timedelta
from src.graph import graph
from src.monitor import score_latest, score_as_of, get_issue_onset

st.set_page_config(page_title="FabCast", layout="wide", initial_sidebar_state="collapsed")

CYAN = "#22d3ee"; CYAN_DIM = "rgba(34,211,238,0.35)"
AMBER = "#ffb020"; AMBER_DIM = "rgba(255,176,32,0.35)"
GREEN = "#10e070"; RED = "#ff4757"; PURPLE = "#a855f7"
BG = "#05080c"; PANEL = "#0d141d"; PANEL_BORDER = "rgba(34,211,238,0.18)"
TEXT = "#dceeff"; TEXT_DIM = "#6f8aa3"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
.stApp {{
    background:
        repeating-linear-gradient(0deg, rgba(34,211,238,0.025) 0px, rgba(34,211,238,0.025) 1px, transparent 1px, transparent 40px),
        repeating-linear-gradient(90deg, rgba(34,211,238,0.025) 0px, rgba(34,211,238,0.025) 1px, transparent 1px, transparent 40px),
        radial-gradient(ellipse at top left, #0a1622 0%, {BG} 55%);
    color: {TEXT};
}}
* {{ font-family: 'JetBrains Mono', monospace; }}
h1, h2, h3, .fc-display {{ font-family: 'Rajdhani', sans-serif; letter-spacing: 0.03em; }}
#MainMenu, header, footer {{ visibility: hidden; }}

.fc-hero {{ padding: 18px 0 10px 0; margin-bottom: 8px; border-bottom: 1px solid {PANEL_BORDER}; }}
.fc-title {{ font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 42px; color: {TEXT}; letter-spacing: 0.08em; margin: 0; text-shadow: 0 0 18px {CYAN_DIM}, 0 0 40px {CYAN_DIM}; }}
.fc-title span {{ color: {CYAN}; }}
.fc-subtitle {{ color: {TEXT_DIM}; font-size: 13px; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 2px; }}

.fc-card {{ background: linear-gradient(160deg, {PANEL} 0%, #0a1017 100%); border: 1px solid {PANEL_BORDER}; border-radius: 10px; padding: 18px 20px; }}

.fc-pill {{ display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 999px; font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 500; }}
.fc-pill-scanning {{ background: rgba(34,211,238,0.1); border: 1px solid {CYAN}; color: {CYAN}; }}
.fc-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
.fc-dot-cyan {{ background: {CYAN}; box-shadow: 0 0 8px {CYAN}; animation: pulseDot 1.4s ease-in-out infinite; }}
@keyframes pulseDot {{ 0%,100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.4; transform: scale(0.7); }} }}

.fc-alert-card {{ background: linear-gradient(160deg, #1a1409 0%, #0d0a05 100%); border: 1px solid {AMBER}; border-radius: 14px; padding: 24px 26px; box-shadow: 0 0 30px rgba(255,176,32,0.15); animation: fadeInUp 0.4s ease; margin-bottom: 22px; }}
@keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

.fc-alert-header {{ text-align: center; margin-bottom: 18px; }}
.fc-alert-eq {{ font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 26px; color: {AMBER}; letter-spacing: 0.06em; text-shadow: 0 0 14px {AMBER_DIM}; }}
.fc-alert-sub {{ color: {TEXT_DIM}; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 4px; }}

.fc-metric-box {{ background: rgba(0,0,0,0.25); border: 1px solid {PANEL_BORDER}; border-radius: 8px; padding: 10px 6px; text-align: center; }}
.fc-metric-box-hot {{ border-color: {AMBER}; box-shadow: 0 0 10px {AMBER_DIM}; }}
.fc-metric-box-label {{ color: {TEXT_DIM}; font-size: 10px; letter-spacing: 0.1em; }}
.fc-metric-box-value {{ font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 18px; color: {TEXT}; margin-top: 2px; }}
.fc-metric-box-hot .fc-metric-box-value {{ color: {AMBER}; }}

.fc-section-label {{ font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; font-weight: 700; margin: 14px 0 6px 0; display: block; }}

.fc-explain-card {{ background: linear-gradient(160deg, {PANEL} 0%, #0a1017 100%); border: 1px solid {PANEL_BORDER}; border-radius: 10px; padding: 20px 24px; margin-bottom: 16px; }}
.fc-explain-card h4 {{ color: {CYAN}; font-family: 'Rajdhani', sans-serif; font-size: 17px; letter-spacing: 0.05em; margin-top:0; }}
.fc-explain-card p, .fc-explain-card li {{ color: {TEXT}; font-size: 14px; line-height: 1.65; }}
.fc-explain-card li {{ margin-bottom: 6px; }}

div[data-testid="stButton"] > button {{ background: linear-gradient(160deg, #0d1a22 0%, #060c11 100%) !important; border: 1px solid {CYAN} !important; color: {CYAN} !important; border-radius: 8px !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; transition: all 0.2s ease !important; }}
div[data-testid="stButton"] > button:hover {{ box-shadow: 0 0 20px {CYAN_DIM} !important; transform: translateY(-1px); }}
div[data-testid="stButton"] > button[kind="primary"] {{ background: linear-gradient(160deg, {CYAN} 0%, #0891a8 100%) !important; color: #05080c !important; box-shadow: 0 0 16px {CYAN_DIM} !important; }}

.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {PANEL_BORDER}; }}
.stTabs [data-baseweb="tab"] {{ font-family: 'Rajdhani', sans-serif; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: {TEXT_DIM}; font-size: 14px; }}
.stTabs [aria-selected="true"] {{ color: {CYAN} !important; text-shadow: 0 0 10px {CYAN_DIM}; }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="fc-hero">
    <div class="fc-title">FAB<span>CAST</span></div>
    <div class="fc-subtitle">Agentic Equipment Telemetry Triage &nbsp;·&nbsp; Hybrid Detection &nbsp;·&nbsp; Human-in-the-Loop</div>
</div>
""", unsafe_allow_html=True)

def get_all_metrics(equipment_id, as_of_date):
    con = duckdb.connect("data/fabcast.duckdb", read_only=True)
    row = con.sql(f"""
        SELECT metric, value FROM sensor_readings
        WHERE equipment_id = '{equipment_id}' AND timestamp <= '{as_of_date}'
        QUALIFY ROW_NUMBER() OVER (PARTITION BY metric ORDER BY timestamp DESC) = 1
    """).df()
    con.close()
    return dict(zip(row["metric"], row["value"]))

if "devices" not in st.session_state:
    con = duckdb.connect("data/fabcast.duckdb", read_only=True)
    all_devices = con.sql("SELECT DISTINCT equipment_id FROM sensor_readings").df()["equipment_id"].tolist()
    date_bounds = con.sql("SELECT MIN(timestamp) mn, MAX(timestamp) mx FROM sensor_readings").df()
    con.close()

    st.session_state.devices = sorted(all_devices)
    known_interesting = ["S1F09DZQ", "W1F1CB5E", "S1F0GG8X", "W1F0M02P"]
    known_interesting = [d for d in known_interesting if d in all_devices]
    others = [d for d in st.session_state.devices if d not in known_interesting][:25]
    st.session_state.monitored_devices = known_interesting + others

    st.session_state.min_date = pd.Timestamp(date_bounds["mn"].iloc[0])
    st.session_state.max_date = pd.Timestamp(date_bounds["mx"].iloc[0])
    st.session_state.current_date = st.session_state.min_date
    st.session_state.pending_tickets = {}
    st.session_state.resolved_log = []
    st.session_state.nominal_count = 0

tab1, tab2 = st.tabs(["◉ Live Triage Console", "◈ Project Explanation"])

# =====================================================================
# TAB 1 — LIVE TRIAGE CONSOLE
# =====================================================================
with tab1:
    st.write("")

    if "show_intro" not in st.session_state:
        st.session_state.show_intro = True

    if st.session_state.show_intro:
        st.markdown(f"""
        <div style="display:flex; gap:14px; margin-bottom:18px; flex-wrap:wrap;">
            <div class="fc-card" style="flex:1; min-width:220px; border-color:{CYAN}55;">
                <div style="font-size:22px; margin-bottom:8px;">🎯</div>
                <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:14px; color:{CYAN}; letter-spacing:0.05em;">WHAT IT IS</div>
                <div style="font-size:12.5px; color:{TEXT}; margin-top:6px; line-height:1.5;">
                    FabCast — agentic AI for predictive equipment maintenance. Detects at-risk
                    devices from sensor data, diagnoses the failure pattern with evidence, and
                    drafts a maintenance ticket — with a human always in the loop before any
                    action is taken.
                </div>
            </div>
            <div class="fc-card" style="flex:1; min-width:220px; border-color:{PURPLE}55;">
                <div style="font-size:22px; margin-bottom:8px;">🔗</div>
                <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:14px; color:{PURPLE}; letter-spacing:0.05em;">HOW IT WORKS</div>
                <div style="font-size:12.5px; color:{TEXT}; margin-top:6px; line-height:1.5;">
                    Agentic RAG under the hood. A chain of agents — Monitor → Diagnosis →
                    Ticket — each hands off to the next, retrieving grounded evidence from a
                    maintenance knowledge base at every step instead of guessing from memory.
                </div>
            </div>
            <div class="fc-card" style="flex:1; min-width:220px; border-color:{AMBER}55;">
                <div style="font-size:22px; margin-bottom:8px;">▶️</div>
                <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:14px; color:{AMBER}; letter-spacing:0.05em;">HOW TO START</div>
                <div style="font-size:12.5px; color:{TEXT}; margin-top:6px; line-height:1.5;">
                    Data arrives once a day per device, not in real time — click
                    <b>"Next Timeframe"</b> below to replay that daily monitoring cycle and
                    watch FabCast catch risk as it happens.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Got it, hide this", key="dismiss_intro"):
            st.session_state.show_intro = False
            st.rerun()
        st.write("")

    cc1, cc2, cc3 = st.columns([2, 1, 2])
    with cc1:
        st.markdown(f'<span class="fc-pill fc-pill-scanning"><span class="fc-dot fc-dot-cyan"></span>'
                     f'SIMULATED DATE: {st.session_state.current_date.date()}</span>', unsafe_allow_html=True)
    with cc2:
        step = st.selectbox("Advance by", ["1 day", "7 days", "30 days"], index=1, label_visibility="collapsed")
    with cc3:
        if st.button("▶ NEXT TIMEFRAME", type="primary"):
            days = {"1 day": 1, "7 days": 7, "30 days": 30}[step]
            new_date = st.session_state.current_date + timedelta(days=days)
            st.session_state.current_date = min(new_date, st.session_state.max_date)

            nominal = 0
            total_devices = len(st.session_state.monitored_devices)
            progress_box = st.empty()
            progress_bar = st.progress(0)

            for i, d in enumerate(st.session_state.monitored_devices):
                records_so_far = (i + 1) * 14 * 4
                progress_box.markdown(
                    f'<div style="color:{CYAN};font-size:13px;letter-spacing:0.05em;">'
                    f'🔍 SEARCHING <b>{d}</b> — device {i+1}/{total_devices} · '
                    f'analyzing 4 signal metrics across a 14-day window · '
                    f'{records_so_far:,} data points evaluated so far</div>',
                    unsafe_allow_html=True,
                )
                result = score_as_of(d, st.session_state.current_date.date())
                already_pending = any(v["device"] == d for v in st.session_state.pending_tickets.values())
                if result["is_anomaly"] and not already_pending:
                    onset = get_issue_onset(d, st.session_state.current_date.date())
                    config = {"configurable": {"thread_id": f"{d}__{st.session_state.current_date.date()}"}}
                    graph.invoke({"equipment_id": d}, config=config)
                    time.sleep(2)  # brief pacing so a burst of flagged devices doesn't trip Groq's per-minute rate limit
                    st.session_state.pending_tickets[config["configurable"]["thread_id"]] = {
                        "device": d, "config": config,
                        "scan_date": st.session_state.current_date.date(),
                        "onset_date": onset.get("onset_date"),
                    }
                elif not result["is_anomaly"]:
                    nominal += 1
                progress_bar.progress((i + 1) / total_devices)

            progress_box.empty()
            progress_bar.empty()
            st.session_state.nominal_count = nominal
            st.rerun()

    if st.session_state.current_date >= st.session_state.max_date:
        st.caption("⚠ Reached the end of available simulation data.")

    st.caption(f"Monitoring {len(st.session_state.monitored_devices)} devices — "
               f"{st.session_state.nominal_count} nominal, {len(st.session_state.pending_tickets)} awaiting review")

    st.write("")
    n_alerts = len(st.session_state.pending_tickets)
    st.markdown(f'<div class="fc-section-label" style="color:{AMBER};">'
                f'{"ACTIVE ALERTS (" + str(n_alerts) + ")" if n_alerts else "NO ACTIVE ALERTS"}</div>',
                unsafe_allow_html=True)
    if not st.session_state.pending_tickets:
        st.caption("All monitored devices nominal. Advance the timeframe to continue monitoring.")

    for thread_id, meta in list(st.session_state.pending_tickets.items()):
        config = meta["config"]
        device = meta["device"]
        state = graph.get_state(config).values
        readings = get_all_metrics(device, meta["scan_date"])
        hot_metrics = {"metric2", "metric4", "metric7", "metric9"}
        onset_txt = meta.get("onset_date") or "pattern-based (no single onset date)"

        st.markdown(f"""
        <div class="fc-alert-card">
            <div class="fc-alert-header">
                <div class="fc-alert-eq">⚠ EQUIPMENT {device} — POTENTIAL FAILURE</div>
                <div class="fc-alert-sub">Issue began: {onset_txt} &nbsp;·&nbsp; Detected during scan: {meta['scan_date']} &nbsp;·&nbsp; triggered by: {state['anomaly'].get('triggered_by', 'n/a')}</div>
            </div>
        """, unsafe_allow_html=True)

        for row_start in [1, 4, 7]:
            cols = st.columns(3)
            for i, m_idx in enumerate(range(row_start, row_start + 3)):
                metric_name = f"metric{m_idx}"
                val = readings.get(metric_name, 0)
                hot_cls = "fc-metric-box-hot" if metric_name in hot_metrics and val and float(val) > 0 else ""
                with cols[i]:
                    st.markdown(f'<div class="fc-metric-box {hot_cls}">'
                                f'<div class="fc-metric-box-label">METRIC {m_idx}</div>'
                                f'<div class="fc-metric-box-value">{val:,.0f}</div></div>', unsafe_allow_html=True)
            st.write("")

        st.markdown(f'<div class="fc-section-label" style="color:{CYAN};">DIAGNOSIS</div>', unsafe_allow_html=True)
        st.write(state.get("diagnosis"))
        st.caption(f"Sources: {', '.join(state.get('citations', []))}")

        edited_ticket = st.text_area("Draft ticket (editable)", state.get("ticket_draft", ""), height=160, key=f"ticket_{thread_id}")

        b1, b2 = st.columns(2)
        if b1.button("✓ APPROVE & SUBMIT", type="primary", key=f"approve_{thread_id}", use_container_width=True):
            graph.update_state(config, {"human_decision": "approved", "ticket_draft": edited_ticket})
            graph.invoke(None, config=config)
            st.session_state.resolved_log.insert(0, (device, str(meta["onset_date"] or meta["scan_date"]), "approved"))
            del st.session_state.pending_tickets[thread_id]
            st.rerun()
        if b2.button("✗ REJECT", key=f"reject_{thread_id}", use_container_width=True):
            graph.update_state(config, {"human_decision": "rejected"})
            st.session_state.resolved_log.insert(0, (device, str(meta["onset_date"] or meta["scan_date"]), "rejected"))
            del st.session_state.pending_tickets[thread_id]
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.resolved_log:
        st.write("")
        st.markdown(f'<div class="fc-section-label" style="color:{CYAN};">RESOLVED THIS SESSION</div>', unsafe_allow_html=True)
        for d, dt, decision in st.session_state.resolved_log[:10]:
            icon = "✅" if decision == "approved" else "🚫"
            st.caption(f"{icon} {d} — {dt} — {decision}")

# =====================================================================
# TAB 2 — PROJECT EXPLANATION
# =====================================================================
with tab2:
    st.write("")
    st.markdown(f"""
    <div class="fc-explain-card">
        <h4>🤖 So, What Is This Thing?</h4>
        <p>FabCast watches equipment sensor readings, flags what looks off, digs up relevant
        context to explain <i>why</i>, drafts a maintenance ticket — then stops and waits for
        a human to approve it. The point isn't sci-fi-precise failure prediction (nothing on
        this dataset can do that). It's the less flashy, more useful pattern most agent demos
        skip: detect → retrieve → reason → defer to a human.</p>
    </div>
    <div class="fc-explain-card">
        <h4>⚙️ What's Actually Running Under The Hood</h4>
    """, unsafe_allow_html=True)

    def pipeline_card(number, icon, title, desc, color):
        st.markdown(f"""
        <div class="fc-card" style="border-color:{color}80; text-align:center; padding:22px 14px; min-height:175px;">
            <div style="color:{color}; font-family:'Rajdhani',sans-serif; font-weight:700; font-size:11px; letter-spacing:0.18em; margin-bottom:10px;">STEP {number}</div>
            <div style="font-size:30px; margin-bottom:8px;">{icon}</div>
            <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:15px; color:{TEXT}; letter-spacing:0.03em;">{title}</div>
            <div style="color:{TEXT_DIM}; font-size:11px; margin-top:6px; line-height:1.4;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1: pipeline_card("01", "🔍", "Monitor Agent", "Rule + BiLSTM hybrid detector", CYAN)
    with pc2: pipeline_card("02", "📚", "Diagnosis Agent", "RAG over 11 docs, Ollama + Chroma", PURPLE)
    with pc3: pipeline_card("03", "🎫", "Ticket Agent", "Drafts the structured work order", AMBER)
    with pc4: pipeline_card("04", "✅", "Human Gate", "LangGraph interrupt, human clicks approve", GREEN)

    st.write("")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="fc-explain-card"><h4 style="margin-bottom:18px;">🗺️ How It All Connects</h4>', unsafe_allow_html=True)

    def dbox(title, sub, color, width=190):
        return f"""<div style="border:2.5px solid {color}; border-radius:10px; background:#0d141d;
            padding:16px 14px; min-width:{width}px; text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:17px; color:#f5faff;">{title}</div>
            <div style="font-size:12px; color:#8fa5ba; margin-top:5px;">{sub}</div>
        </div>"""

    def darrow(vertical=False):
        if vertical:
            return '<div style="font-size:26px; color:#a9c1d6; text-align:center; padding:4px 0;">↓</div>'
        return '<div style="font-size:24px; color:#a9c1d6; padding:0 6px;">→</div>'

    def row_label(text, color):
        return f'<div style="color:{color}; font-family:\'Rajdhani\',sans-serif; font-weight:700; font-size:14px; letter-spacing:0.25em; margin-bottom:10px;">{text}</div>'

    diagram_html = f"""
    <div style="display:flex; flex-direction:column; align-items:center; gap:4px; padding:10px 0;">

        {row_label("DATA", "#9fb6c9")}
        <div style="display:flex; align-items:center; justify-content:center;">
            {dbox("Kaggle CSV", "Daily Readings", "#9fb6c9")}
            {darrow()}
            {dbox("DuckDB", "sensor_readings", "#9fb6c9")}
        </div>

        {darrow(vertical=True)}

        {row_label("DETECTION", "#22d3ee")}
        <div style="display:flex; align-items:center; justify-content:center;">
            {dbox("Monitor Agent", "Rule + BiLSTM", "#22d3ee")}
            {darrow()}
            {dbox("Anomaly?", "decision point", "#ffb020")}
        </div>
        <div style="font-size:12px; color:#6f8aa3; margin:10px 0;">
            no → shown directly on dashboard &nbsp;&nbsp;·&nbsp;&nbsp; yes ↓ continues below
        </div>

        {darrow(vertical=True)}

        {row_label("AGENTIC RESPONSE", "#c084fc")}
        <div style="display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:2px;">
            {dbox("Chroma", "11 Maintenance Docs", "#c084fc", 170)}
            {darrow()}
            {dbox("Diagnosis Agent", "RAG + Ollama LLM", "#c084fc", 190)}
            {darrow()}
            {dbox("Ticket Agent", "Drafts Work Order", "#ffb020", 180)}
            {darrow()}
            {dbox("Human Approval", "LangGraph Interrupt", "#34eb8f", 190)}
        </div>

        {darrow(vertical=True)}

        {dbox("Streamlit UI", "Live Triage Console", "#f5faff", 220)}
    </div>
    """
    diagram_html = "\n".join(line.strip() for line in diagram_html.strip().split("\n"))
    st.markdown(diagram_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="fc-explain-card">
        <h4>📊 The Data</h4>
        <p>The raw dataset is one CSV from Kaggle: 124,494 rows covering roughly 1,169
        devices reporting daily from January to November 2015, with nine raw sensor columns
        per device per day. No documentation, no context, just numbers.</p>
        <p>The live console doesn't watch all ~1,169 at once — nobody needs to find out how
        personally a Streamlit server takes babysitting a thousand live agents at once. It
        monitors a curated fleet of 29: a handful of devices already confirmed as real
        historical troublemakers in the data, plus twenty-five more thrown in for variety.</p>
        <p>Separately, on the detection side: of the nine raw metrics each device reports,
        the detector only actually trusts a subset of them — the rest ranged from pure noise
        to a column that turned out to be a duplicate of another one. Full breakdown of which
        metrics and why is in the model-selection writeup.</p>
        <p>The 11 maintenance documents powering the RAG layer don't come from the dataset
        either — obviously, it's a CSV, not a wiki. I had Claude write them, grounded in real
        patterns I found by hand-checking actual failure cases first, not just invented from
        nothing, so the Diagnosis Agent has something legitimate to retrieve from.</p>
        <p><a href="https://www.kaggle.com/datasets/hiimanshuagarwal/predictive-maintenance-dataset" target="_blank" style="color:#22d3ee;">
        → Predictive Maintenance Dataset, Himanshu Agarwal, Kaggle</a></p>
    </div>
    """, unsafe_allow_html=True)
