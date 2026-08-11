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
        <div class="fc-card" style="border-color:{color}80; text-align:center; padding:22px 14px; min-height:175px;">
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
    with pc4: pipeline_card("04", "\u2705", "Human Gate", "LangGraph interrupt, human clicks approve", GREEN)

    st.write("")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="fc-explain-card"><h4 style="margin-bottom:18px;">\U0001F5FA\ufe0f How It All Connects</h4>', unsafe_allow_html=True)

    def dbox(title, sub, color, width=190):
        return f\"\"\"<div style="border:2.5px solid {color}; border-radius:10px; background:#0d141d;
            padding:16px 14px; min-width:{width}px; text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:17px; color:#f5faff;">{title}</div>
            <div style="font-size:12px; color:#8fa5ba; margin-top:5px;">{sub}</div>
        </div>\"\"\"

    def darrow(vertical=False):
        if vertical:
            return '<div style="font-size:26px; color:#a9c1d6; text-align:center; padding:4px 0;">\u2193</div>'
        return '<div style="font-size:24px; color:#a9c1d6; padding:0 6px;">\u2192</div>'

    def row_label(text, color):
        return f'<div style="color:{color}; font-family:\\'Rajdhani\\',sans-serif; font-weight:700; font-size:14px; letter-spacing:0.25em; margin-bottom:10px;">{text}</div>'

    diagram_html = f\"\"\"
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
            no \u2192 shown directly on dashboard &nbsp;&nbsp;\u00b7&nbsp;&nbsp; yes \u2193 continues below
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
    \"\"\"
    st.markdown(diagram_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="fc-explain-card">
        <h4>\U0001F4CA The Data</h4>
        <p>The raw dataset is one CSV from Kaggle: 124,494 rows covering roughly 1,169
        devices reporting daily from January to November 2015, with nine raw sensor columns
        per device per day. No documentation, no context, just numbers.</p>
        <p>The live console doesn't watch all ~1,169 at once \u2014 nobody needs to find out how
        personally a Streamlit server takes babysitting a thousand live agents at once. It
        monitors a curated fleet of 29: a handful of devices already confirmed as real
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
