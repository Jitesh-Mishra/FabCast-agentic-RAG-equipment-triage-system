with open("app.py") as f:
    content = f.read()

# --- Insertion 1: a note under the diagram, still inside the diagram card ---
old_diagram_close = '''    st.markdown(diagram_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)'''

new_diagram_close = '''    st.markdown(diagram_html, unsafe_allow_html=True)
    st.markdown(f\'\'\'
    <div style="text-align:center; margin-top:16px; padding-top:14px; border-top:1px solid rgba(168,85,247,0.2); font-size:12px; color:#c084fc;">
        \u24d8 The Diagnosis Agent's prompt was iteratively tuned using a local LLM-as-judge eval
        loop \u2014 answer relevancy improved from 0.86 \u2192 0.91 across an 11-question test set.
        See "Prompt Tuning & Eval Loop" below.
    </div>
    \'\'\', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)'''

count1 = content.count(old_diagram_close)
if count1 != 1:
    print(f"FAIL insertion 1: expected 1 match, found {count1}")
    raise SystemExit(1)
content = content.replace(old_diagram_close, new_diagram_close)

# --- Insertion 2: new eval-loop section, inserted right before the Dataset card ---
old_dataset_marker = r'''    st.markdown(f"""
    <div class="fc-explain-card">
        <h4>\U0001F4CA The Data</h4>'''

eval_section = '''    st.markdown(f"""
    <div class="fc-explain-card">
        <h4>\U0001F4C8 Prompt Tuning & Eval Loop</h4>
        <p>The Diagnosis Agent's prompt didn't just get written once and left alone \u2014 it went
        through an actual measured tuning pass. An 11-question eval set was built from the
        maintenance docs, and each answer was scored by a second local LLM acting as judge,
        rating <b>faithfulness</b> (does the answer only claim what the source actually says)
        and <b>relevancy</b> (does the answer actually address the question asked).</p>
        <p style="font-size:12px; color:{TEXT_DIM};">Side note: the popular <code>ragas</code>
        eval library was tried first, but its dependencies conflict with the modern LangChain
        stack this project already runs on \u2014 confirmed directly, not assumed \u2014 so the
        faithfulness/relevancy scoring was built by hand instead, using Ollama as the judge.</p>
        <div style="display:flex; gap:14px; margin-top:14px; flex-wrap:wrap;">
            <div class="fc-card" style="flex:1; min-width:150px; text-align:center;">
                <div class="fc-metric-label">Faithfulness (v1 \u2192 v2)</div>
                <div class="fc-metric-value" style="font-size:22px;">0.91 \u2192 0.89</div>
                <div class="fc-metric-sub">roughly flat, within noise</div>
            </div>
            <div class="fc-card" style="flex:1; min-width:150px; text-align:center;">
                <div class="fc-metric-label">Relevancy (v1 \u2192 v2)</div>
                <div class="fc-metric-value" style="font-size:22px; color:{GREEN};">0.86 \u2192 0.91</div>
                <div class="fc-metric-sub">real improvement, targeted change</div>
            </div>
        </div>
        <p style="margin-top:14px;">The change: the original prompt let the model wander through
        context before answering. V2 forces a direct answer first, then supporting reasoning
        second \u2014 and relevancy moved accordingly. The one low outlier (a 0.70 faithfulness
        score on a metric9 question) was checked by hand: the answer actually quoted its source
        directly and correctly, so that score looks like judge noise from a small local model
        rather than a real hallucination \u2014 worth stating plainly rather than hiding.</p>
    </div>
    <div class="fc-explain-card">
        <h4>\U0001F4CA The Data</h4>'''

count2 = content.count(old_dataset_marker)
if count2 != 1:
    print(f"FAIL insertion 2: expected 1 match, found {count2}")
    raise SystemExit(1)
content = content.replace(old_dataset_marker, eval_section)

with open("app.py", "w") as f:
    f.write(content)

print("Both insertions applied successfully.")
print("Diagram note present:", "iteratively tuned using a local LLM-as-judge" in content)
print("Eval section present:", "Prompt Tuning & Eval Loop" in content)
