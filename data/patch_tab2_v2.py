with open("app.py") as f:
    content = f.read()

marker = 'with tab2:'
idx = content.find(marker)
if idx == -1:
    print("FAIL: 'with tab2:' not found")
    raise SystemExit(1)

content = content[:idx]

new_tab2 = '''with tab2:
    st.write("")
    st.markdown(f"""
    <div class="fc-explain-card">
        <h4>\U0001F916 So, What Is This Thing?</h4>
        <p>FabCast watches equipment sensor readings, flags what looks off, digs up relevant
        context to explain <i>why</i>, drafts a maintenance ticket \u2014 then stops and waits for
        a human to approve it. The point isn't sci-fi-precise failure prediction (nothing on
        this dataset can do that). It's the less flashy, more useful pattern most agent demos
        skip: detect \u2192 retrieve \u2192 reason \u2192 defer to a human.</p>
    </div>
    <div class="fc-explain-card">
        <h4>\u2699\ufe0f What's Actually Running Under The Hood</h4>
    """, unsafe_allow_html=True)

    def pipeline_card(number, icon, title, desc, color):
        st.markdown(f\"\"\"
        <div class="fc-card" style="border-color:{color}80; text-align:center; padding:22px 14px; height:150px;">
            <div style="color:{color}; font-family:'Rajdhani',sans-serif; font-weight:700; font-size:11px; letter-spacing:0.18em; margin-bottom:10px;">STEP {number}</div>
            <div style="font-size:30px; margin-bottom:8px;">{icon}</div>
            <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:15px; color:{TEXT}; letter-spacing:0.03em;">{title}</div>
            <div style="color:{TEXT_DIM}; font-size:11px; margin-top:6px; line-height:1.4;">{desc}</div>
        </div>
        \"\"\", unsafe_allow_html=True)

    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1: pipeline_card("01", "\U0001F50D", "Monitor Agent", "Rule + BiLSTM hybrid detector", CYAN)
    with pc2: pipeline_card("02", "\U0001F4DA", "Diagnosis Agent", "RAG over 11 docs, Ollama + Chroma", PURPLE)
    with pc3: pipeline_card("03", "\U0001F3AB", "Ticket Agent", "Drafts the structured work order", AMBER)
    with pc4: pipeline_card("04", "\u2705", "Human Gate", "LangGraph interrupt \u2014 nothing ships without a click", GREEN)

    st.write("")
    st.caption("Runs entirely on free, local tooling \u2014 Ollama, DuckDB, Chroma. Zero API keys. Zero dollars.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="fc-explain-card"><h4 style="margin-bottom:16px;">\U0001F5FA\ufe0f How It All Connects</h4>', unsafe_allow_html=True)

    diagram = \'\'\'
    digraph G {
        bgcolor="#05080c"
        rankdir=LR
        nodesep=0.75
        ranksep=1.3
        size="18,11"
        fontname="Helvetica"
        node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=20 fontcolor="#f5faff" fillcolor="#0d141d" penwidth=2.2 margin="0.38,0.24"]
        edge [color="#a9c1d6" fontcolor="#d3e4f0" fontsize=15 fontname="Helvetica" penwidth=1.6]

        subgraph cluster_data {
            label="DATA"
            fontcolor="#a9c1d6" color="#3a4d5c" style="rounded,dashed" fontsize=18 penwidth=1.5
            CSV [label="Kaggle CSV\\nDaily Readings" color="#a9c1d6"]
            DuckDB [label="DuckDB\\nsensor_readings" color="#a9c1d6"]
        }

        subgraph cluster_detect {
            label="DETECTION"
            fontcolor="#22d3ee" color="#155e75" style="rounded,dashed" fontsize=18 penwidth=1.5
            Monitor [label="Monitor Agent\\nRule + BiLSTM" color="#22d3ee" penwidth=3]
            Decision [shape=diamond label="Anomaly?" color="#ffb020" fillcolor="#1a1409" fontsize=18]
        }

        subgraph cluster_response {
            label="AGENTIC RESPONSE"
            fontcolor="#c084fc" color="#5b21b6" style="rounded,dashed" fontsize=18 penwidth=1.5
            Chroma [label="Chroma Vector Store\\n11 Maintenance Docs" shape=cylinder color="#c084fc"]
            Diagnosis [label="Diagnosis Agent\\nRAG + Ollama LLM" color="#c084fc" penwidth=3]
            Ticket [label="Ticket Agent\\nDrafts Work Order" color="#ffb020"]
            Human [label="Human Approval\\nLangGraph Interrupt" color="#34eb8f" fillcolor="#08150d" penwidth=3]
        }

        UI [label="Streamlit UI\\nLive Triage Console" color="#f5faff" penwidth=3 fillcolor="#0a1017"]

        CSV -> DuckDB -> Monitor -> Decision
        Decision -> UI [label="  no"]
        Decision -> Diagnosis [label="  yes"]
        Chroma -> Diagnosis
        Diagnosis -> Ticket -> Human -> UI
    }
    \'\'\'
    st.graphviz_chart(diagram)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="fc-explain-card">
        <h4>\U0001F4CA The Data</h4>
        <p>The raw dataset is one CSV from Kaggle: 124,494 rows covering roughly 1,169
        devices reporting daily from January to November 2015, with nine raw sensor columns
        per device per day. No documentation, no context, just numbers.</p>
        <p>The live console doesn't watch all ~1,169 at once \u2014 nobody needs to find out how
        personally a free Streamlit server takes babysitting a thousand live agents at once.
        It monitors a curated fleet of 29: a handful of devices already confirmed as real
        historical troublemakers in the data, plus twenty-five more thrown in for variety.</p>
        <p>Separately, on the detection side: of the nine raw metrics each device reports,
        the detector only actually trusts a subset of them \u2014 the rest ranged from pure noise
        to a column that turned out to be a duplicate of another one. Full breakdown of which
        metrics and why is in the model-selection writeup.</p>
        <p>The 11 maintenance documents powering the RAG layer don't come from the dataset
        either \u2014 obviously, it's a CSV, not a wiki. I had Claude write them, grounded in real
        patterns I found by hand-checking actual failure cases first, not just invented from
        nothing, so the Diagnosis Agent has something legitimate to retrieve from.</p>
        <p><a href="https://www.kaggle.com/datasets/hiimanshuagarwal/predictive-maintenance-dataset" target="_blank" style="color:#22d3ee;">
        \u2192 Predictive Maintenance Dataset, Himanshu Agarwal, Kaggle</a></p>
    </div>
    """, unsafe_allow_html=True)
'''

content = content + new_tab2

with open("app.py", "w") as f:
    f.write(content)

print("Tab 2 replaced successfully. File length:", len(content))
