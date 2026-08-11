import sys

with open("app.py") as f:
    content = f.read()

marker_start = 'with tab2:'
marker_end = 'st.markdown("""\n    </div>\n    <div class="fc-explain-card">\n        <h4>📊 The Data'

start_idx = content.find(marker_start)
if start_idx == -1:
    print("FAIL: could not find 'with tab2:' marker")
    sys.exit(1)

# Find the end of the file (Tab 2 is the last block)
new_tab2 = '''with tab2:
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
        <div style="display:flex; gap:14px; flex-wrap:wrap; margin-top:12px;">
            <div class="fc-pipe-card" style="border-color:rgba(34,211,238,0.4);">
                <div class="fc-pipe-icon">🔍</div>
                <div class="fc-pipe-title" style="color:{CYAN};">Monitor Agent</div>
                <div class="fc-pipe-desc">Rule + BiLSTM hybrid detector</div>
            </div>
            <div class="fc-pipe-card" style="border-color:rgba(168,85,247,0.4);">
                <div class="fc-pipe-icon">📚</div>
                <div class="fc-pipe-title" style="color:{PURPLE};">Diagnosis Agent</div>
                <div class="fc-pipe-desc">RAG over 11 docs, Ollama + Chroma</div>
            </div>
            <div class="fc-pipe-card" style="border-color:rgba(255,176,32,0.4);">
                <div class="fc-pipe-icon">🎫</div>
                <div class="fc-pipe-title" style="color:{AMBER};">Ticket Agent</div>
                <div class="fc-pipe-desc">Drafts the structured work order</div>
            </div>
            <div class="fc-pipe-card" style="border-color:rgba(16,224,112,0.4);">
                <div class="fc-pipe-icon">✅</div>
                <div class="fc-pipe-title" style="color:{GREEN};">Human Gate</div>
                <div class="fc-pipe-desc">LangGraph interrupt — nothing ships without a click</div>
            </div>
        </div>
        <p style="margin-top:14px; color:{TEXT_DIM}; font-size:12px;">Runs entirely on free,
        local tooling — Ollama, DuckDB, Chroma. Zero API keys. Zero dollars.</p>
    </div>
    <div class="fc-explain-card">
        <h4 style="margin-bottom:14px;">🗺️ How It All Connects</h4>
    """, unsafe_allow_html=True)

    diagram = \'\'\'
    digraph G {
        bgcolor="#05080c"
        rankdir=LR
        nodesep=0.6
        ranksep=0.9
        fontname="Helvetica"
        node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=17 fontcolor="#f0f8ff" fillcolor="#0d141d" penwidth=2 margin="0.3,0.18"]
        edge [color="#9fb6c9" fontcolor="#c3d6e6" fontsize=13 fontname="Helvetica" penwidth=1.4]

        subgraph cluster_data {
            label="DATA"
            fontcolor="#9fb6c9" color="#3a4d5c" style="rounded,dashed" fontsize=15
            CSV [label="Kaggle CSV\\nDaily Readings" color="#9fb6c9"]
            DuckDB [label="DuckDB\\nsensor_readings" color="#9fb6c9"]
        }

        subgraph cluster_detect {
            label="DETECTION"
            fontcolor="#22d3ee" color="#155e75" style="rounded,dashed" fontsize=15
            Monitor [label="Monitor Agent\\nRule + BiLSTM" color="#22d3ee" penwidth=2.6]
            Decision [shape=diamond label="Anomaly?" color="#ffb020" fillcolor="#1a1409" fontsize=15]
        }

        subgraph cluster_response {
            label="AGENTIC RESPONSE"
            fontcolor="#c084fc" color="#5b21b6" style="rounded,dashed" fontsize=15
            Chroma [label="Chroma Vector Store\\n11 Maintenance Docs" shape=cylinder color="#c084fc"]
            Diagnosis [label="Diagnosis Agent\\nRAG + Ollama LLM" color="#c084fc" penwidth=2.6]
            Ticket [label="Ticket Agent\\nDrafts Work Order" color="#ffb020"]
            Human [label="Human Approval\\nLangGraph Interrupt" color="#34eb8f" fillcolor="#08150d" penwidth=2.6]
        }

        UI [label="Streamlit UI\\nLive Triage Console" color="#f0f8ff" penwidth=2.6 fillcolor="#0a1017"]

        CSV -> DuckDB -> Monitor -> Decision
        Decision -> UI [label="  no"]
        Decision -> Diagnosis [label="  yes"]
        Chroma -> Diagnosis
        Diagnosis -> Ticket -> Human -> UI
    }
    \'\'\'
    st.graphviz_chart(diagram, use_container_width=True)

    st.markdown(f"""
    </div>
    <div class="fc-explain-card">
        <h4>📊 The Data</h4>
        <p>The raw dataset is one CSV from Kaggle: 124,494 rows covering roughly 1,169
        devices reporting daily from January to November 2015, with nine raw sensor columns
        per device per day. No documentation, no context, just numbers.</p>
        <p>The live console doesn't watch all ~1,169 at once — nobody needs to find out how
        personally a free Streamlit server takes babysitting a thousand live agents at once.
        It monitors a curated fleet of 29: a handful of devices already confirmed as real
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
'''

content = content[:start_idx] + new_tab2

with open("app.py", "w") as f:
    f.write(content)

print("Tab 2 replaced. New file length:", len(content))
