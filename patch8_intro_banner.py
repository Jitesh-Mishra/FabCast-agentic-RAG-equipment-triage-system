with open("app.py") as f:
    content = f.read()

old = '''with tab1:
    st.write("")
    cc1, cc2, cc3 = st.columns([2, 1, 2])'''

new = '''with tab1:
    st.write("")

    if "show_intro" not in st.session_state:
        st.session_state.show_intro = True

    if st.session_state.show_intro:
        st.markdown(f\"\"\"
        <div style="display:flex; gap:14px; margin-bottom:18px; flex-wrap:wrap;">
            <div class="fc-card" style="flex:1; min-width:220px; border-color:{CYAN}55;">
                <div style="font-size:22px; margin-bottom:8px;">\U0001F3AF</div>
                <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:14px; color:{CYAN}; letter-spacing:0.05em;">WHAT IT IS</div>
                <div style="font-size:12.5px; color:{TEXT}; margin-top:6px; line-height:1.5;">
                    FabCast \u2014 agentic AI for predictive equipment maintenance. Detects at-risk
                    devices from sensor data, diagnoses the failure pattern with evidence, and
                    drafts a maintenance ticket \u2014 with a human always in the loop before any
                    action is taken.
                </div>
            </div>
            <div class="fc-card" style="flex:1; min-width:220px; border-color:{PURPLE}55;">
                <div style="font-size:22px; margin-bottom:8px;">\U0001F517</div>
                <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:14px; color:{PURPLE}; letter-spacing:0.05em;">HOW IT WORKS</div>
                <div style="font-size:12.5px; color:{TEXT}; margin-top:6px; line-height:1.5;">
                    Agentic RAG under the hood. A chain of agents \u2014 Monitor \u2192 Diagnosis \u2192
                    Ticket \u2014 each hands off to the next, retrieving grounded evidence from a
                    maintenance knowledge base at every step instead of guessing from memory.
                </div>
            </div>
            <div class="fc-card" style="flex:1; min-width:220px; border-color:{AMBER}55;">
                <div style="font-size:22px; margin-bottom:8px;">\u25B6\ufe0f</div>
                <div style="font-family:'Rajdhani',sans-serif; font-weight:700; font-size:14px; color:{AMBER}; letter-spacing:0.05em;">HOW TO START</div>
                <div style="font-size:12.5px; color:{TEXT}; margin-top:6px; line-height:1.5;">
                    Data arrives once a day per device, not in real time \u2014 click
                    <b>"Next Timeframe"</b> below to replay that daily monitoring cycle and
                    watch FabCast catch risk as it happens.
                </div>
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)
        if st.button("Got it, hide this", key="dismiss_intro"):
            st.session_state.show_intro = False
            st.rerun()
        st.write("")

    cc1, cc2, cc3 = st.columns([2, 1, 2])'''

count = content.count(old)
if count != 1:
    print(f"FAIL: expected 1 match, found {count}")
    raise SystemExit(1)

content = content.replace(old, new)
with open("app.py", "w") as f:
    f.write(content)

print("Patched successfully.")
print("Intro banner present:", "WHAT IT IS" in content)
print("Dismiss button present:", "dismiss_intro" in content)
