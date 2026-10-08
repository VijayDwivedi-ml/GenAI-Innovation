"""Activity 4: The AI Ethics Hot Seat.

A scenario-based decision game that forces participants to confront
real-world dilemmas in responsible Generative AI deployment.
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime


# ---------------------------------------------------------------------------
# SCENARIO BANK — 5 real-world dilemmas
# ---------------------------------------------------------------------------
SCENARIOS = [
    {
        "id": "edu_bias",
        "title": "The Biased Tutor",
        "domain": "🎓 Education",
        "text": (
            "You've deployed a GenAI tutor across 40 schools. Grades are up 30%. "
            "Six weeks in, an audit reveals the model gives subtly weaker explanations "
            "to girls than to boys on STEM topics — same accuracy, different depth. "
            "No policy violation has occurred yet. What do you do?"
        ),
        "options": [
            {"label": "🚀 Ship & monitor", "desc": "Keep it live, add monitoring, fix in next release."},
            {"label": "🛠️ Fix first", "desc": "Pause rollout, retrain on balanced data, re-deploy."},
            {"label": "🔍 Investigate", "desc": "Halt new deployments, study root cause before deciding."},
            {"label": "🛑 Kill it", "desc": "Pull the product entirely — the risk isn't worth it."},
        ],
        "consensus": "🛠️ Fix first",
        "consensus_reason": (
            "Industry consensus (NIST AI RMF, EU AI Act) leans toward pausing, "
            "auditing, and re-deploying with bias mitigation — not shipping and "
            "hoping, but also not abandoning a system that's delivering real value."
        ),
        "consequences": {
            "🚀 Ship & monitor": "3 months later, a parent files a discrimination complaint. The school board pulls the contract. Trust is gone.",
            "🛠️ Fix first": "You pause for 3 weeks. Teachers grumble, but a retrained model ships with 1% accuracy gain AND fairness parity.",
            "🔍 Investigate": "You spend 6 weeks studying root cause. Competitors ship first. You lose 2 school districts to a faster rival.",
            "🛑 Kill it": "You pull the product. 40 schools lose a tool that was helping thousands. The bias problem goes unfixed industry-wide.",
        },
    },
    {
        "id": "health_rare",
        "title": "The 95% Diagnostic",
        "domain": "🏥 Healthcare",
        "text": (
            "Your GenAI diagnostic tool is 95% accurate on common diseases — "
            "outperforming most junior doctors. But it's only 40% accurate on rare "
            "diseases, which affect 1 in 10,000 patients. The tool is already saving "
            "lives in urban hospitals. A rural clinic wants to deploy it. What do you do?"
        ),
        "options": [
            {"label": "🚀 Deploy everywhere", "desc": "95% accuracy is better than nothing. Ship it."},
            {"label": "⚠️ Deploy with warnings", "desc": "Ship to rural clinics but flag rare-disease uncertainty."},
            {"label": "🎯 Urban only", "desc": "Restrict to hospitals with specialists who can catch errors."},
            {"label": "🛑 Don't deploy", "desc": "Wait until rare-disease accuracy improves."},
        ],
        "consensus": "⚠️ Deploy with warnings",
        "consensus_reason": (
            "The right answer balances benefit and harm. A tool that saves lives "
            "shouldn't be withheld, but it MUST be transparent about its limits — "
            "especially where specialists are scarce."
        ),
        "consequences": {
            "🚀 Deploy everywhere": "A rare-disease patient is misdiagnosed. The tool's confidence score misled the rural doctor. Lawsuit filed.",
            "⚠️ Deploy with warnings": "Rural doctors use it as a second opinion, not a first. Rare cases get escalated. Lives saved on both ends.",
            "🎯 Urban only": "Rural patients lose access to a life-saving tool. Health inequality widens. Regulators ask why.",
            "🛑 Don't deploy": "100,000 common-disease diagnoses are delayed. Some patients die waiting for a 'perfect' tool.",
        },
    },
    {
        "id": "hiring_gap",
        "title": "The Career-Gap Filter",
        "domain": "💼 Hiring",
        "text": (
            "Your GenAI resume screener reduces hiring time by 70%. An internal audit "
            "shows it filters out 80% of candidates with career gaps — mostly women "
            "returning from maternity leave. The model wasn't trained on gender, but "
            "it learned the pattern from historical data. Legal has flagged it. What do you do?"
        ),
        "options": [
            {"label": "🚀 Keep using it", "desc": "It's not intentionally biased — no legal violation."},
            {"label": "⚖️ Retrain on balanced data", "desc": "Fix the model, re-audit, then redeploy."},
            {"label": "👤 Human-in-the-loop", "desc": "Keep the AI but require human review of every rejection."},
            {"label": "🛑 Scrap the tool", "desc": "Revert to manual screening until a fair solution exists."},
        ],
        "consensus": "⚖️ Retrain on balanced data",
        "consensus_reason": (
            "The model isn't malicious — it's mirroring historical bias. The fix is "
            "retraining + auditing, not abandoning a tool that saves 70% of hiring time."
        ),
        "consequences": {
            "🚀 Keep using it": "A class-action lawsuit lands 6 months later. The company settles for millions. Reputation damaged.",
            "⚖️ Retrain on balanced data": "Retraining takes 4 weeks. Hiring slows temporarily, but fairness improves and legal risk drops to zero.",
            "👤 Human-in-the-loop": "Recruiters drown in manual reviews. Hiring time goes back up 60%. The AI is now a bottleneck, not a help.",
            "🛑 Scrap the tool": "Hiring time triples. Managers complain. The bias problem returns to humans — who have the SAME bias.",
        },
    },
    {
        "id": "finance_firsttime",
        "title": "The Fair-but-Harsh Loan Model",
        "domain": "💰 Finance",
        "text": (
            "Your GenAI loan-approval model is statistically fair across race, gender, "
            "and geography — a genuine achievement. But it rejects 40% of first-time "
            "applicants due to thin credit history. Your CEO wants to relax the "
            "threshold to hit growth targets. Compliance says no. What do you do?"
        ),
        "options": [
            {"label": "📈 Relax threshold", "desc": "Business needs growth. Approve more first-timers."},
            {"label": "🛡️ Hold the line", "desc": "Fairness matters more than quarterly growth."},
            {"label": "🤝 Alternative scoring", "desc": "Build a secondary model for thin-file applicants."},
            {"label": "⏸️ Pause & study", "desc": "Freeze deployment until we understand the trade-off."},
        ],
        "consensus": "🤝 Alternative scoring",
        "consensus_reason": (
            "The answer isn't 'fair vs. growth' — it's 'find a third way.' "
            "Alternative-data models (rent, utilities, gig income) can serve "
            "thin-file applicants without breaking fairness."
        ),
        "consequences": {
            "📈 Relax threshold": "Default rates spike 3x. Regulators investigate. The model's fairness reputation is destroyed.",
            "🛡️ Hold the line": "40% of first-time applicants — disproportionately young and minority — are locked out. Growth stalls.",
            "🤝 Alternative scoring": "6-month build. New model serves thin-file applicants at 2x approval rate with no fairness regression.",
            "⏸️ Pause & study": "Competitors grab market share. The study confirms what you already knew. Time wasted.",
        },
    },
    {
        "id": "media_deepfake",
        "title": "The Overzealous Deepfake Detector",
        "domain": "📰 Media",
        "text": (
            "Your newsroom deployed a GenAI deepfake detector. It catches 98% of fakes. "
            "But it falsely flags 10% of legitimate journalism as synthetic — often "
            "minority voices and non-native English speakers. Editors are losing trust. "
            "The tool has already prevented 3 major misinformation events. What do you do?"
        ),
        "options": [
            {"label": "🚀 Keep it as-is", "desc": "Preventing fakes outweighs false positives."},
            {"label": "🎚️ Raise threshold", "desc": "Tune for fewer false positives, accept more fakes slipping through."},
            {"label": "🧑‍⚖️ Human review layer", "desc": "Flagged content goes to a human editor before rejection."},
            {"label": "🛑 Disable it", "desc": "The tool is doing more harm than good."},
        ],
        "consensus": "🧑‍⚖️ Human review layer",
        "consensus_reason": (
            "No AI detector is perfect. The ethical move is human-in-the-loop — "
            "automation for speed, humans for judgment. This protects both truth "
            "and voices that history has silenced."
        ),
        "consequences": {
            "🚀 Keep it as-is": "A Pulitzer-winning journalist is falsely flagged. The newsroom's credibility collapses. Retractions follow.",
            "🎚️ Raise threshold": "A coordinated deepfake campaign slips through. 3 million people see fake news. Trust in media drops.",
            "🧑‍⚖️ Human review layer": "Editors are busier, but false positives drop 90%. Real fakes still caught. Trust rebuilt.",
            "🛑 Disable it": "Deepfakes flood the platform unchecked. The 3 events you prevented become 30. Chaos.",
        },
    },
]


# ---------------------------------------------------------------------------
# RENDER FUNCTION
# ---------------------------------------------------------------------------
def render():
    st.markdown("## 🎭 Activity 4: The AI Ethics Hot Seat")
    st.caption("Innovation with responsibility — every decision has a consequence.")

    # Progress indicator
    total = len(SCENARIOS)
    idx = st.session_state.a4_index
    done = len(st.session_state.a4_choices)

    st.progress(done / total, text=f"Scenario {min(done + 1, total)} of {total}")

    # All scenarios complete → summary screen
    if idx >= total:
        _render_summary()
        return

    scenario = SCENARIOS[idx]

    # Scenario card
    st.markdown(
        f"""
        <div class="activity-card">
            <div style="color:#8B5CF6; font-size:0.85rem; font-weight:600; letter-spacing:0.05em;">
                {scenario['domain']} · SCENARIO {idx + 1}
            </div>
            <h3 style="color:#FAFAFA; margin-top:0.5rem;">{scenario['title']}</h3>
            <p style="color:#D1D5DB; font-size:1.02rem; line-height:1.6;">
                {scenario['text']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------------
    # Persist the choice per scenario in session state so the reveal
    # survives reruns and the "Next scenario" button stays alive.
    # ---------------------------------------------------------------
    choice_key = f"a4_choice_{scenario['id']}"
    if choice_key not in st.session_state:
        st.session_state[choice_key] = None

    current_choice = st.session_state[choice_key]

    # ---------------- DECISION SCREEN ----------------
    if current_choice is None:
        st.markdown("### 🤔 What do you do?")
        cols = st.columns(2)
        for i, opt in enumerate(scenario["options"]):
            with cols[i % 2]:
                if st.button(
                    f"**{opt['label']}**\n\n{opt['desc']}",
                    key=f"a4_opt_{idx}_{i}",
                    use_container_width=True,
                ):
                    st.session_state[choice_key] = opt["label"]
                    # Record the choice ONCE
                    st.session_state.a4_choices.append({
                        "scenario_id": scenario["id"],
                        "scenario_title": scenario["title"],
                        "choice": opt["label"],
                        "timestamp": datetime.now().isoformat(),
                    })
                    st.rerun()

    # ---------------- REVEAL SCREEN ----------------
    else:
        _render_reveal(scenario, current_choice)


# ---------------------------------------------------------------------------
# REVEAL SCREEN
# ---------------------------------------------------------------------------
def _render_reveal(scenario, chosen):
    """Show the outcome, consensus, and let the user reflect."""

    st.divider()
    st.markdown("### 🎬 The Consequences")

    consequence = scenario["consequences"].get(chosen, "No data available.")
    st.warning(f"**Your choice: {chosen}**\n\n{consequence}")

    is_consensus = chosen == scenario["consensus"]
    if is_consensus:
        st.success(f"✅ You aligned with the {scenario['consensus']} consensus.")
    else:
        st.info(f"📊 **Industry consensus:** {scenario['consensus']}")

    st.caption(scenario["consensus_reason"])

    _render_choice_chart(scenario, chosen)

    with st.expander("✍️ Quick reflection (optional)"):
        st.text_area(
            "What would you do differently next time?",
            key=f"a4_reflect_{scenario['id']}",
            height=80,
            placeholder="One sentence is enough…",
        )

    st.divider()
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➡️ Next scenario", use_container_width=True, type="primary"):
            st.session_state.a4_index += 1
            st.rerun()


# ---------------------------------------------------------------------------
# CHOICE DISTRIBUTION CHART
# ---------------------------------------------------------------------------
def _render_choice_chart(scenario, chosen):
    """Show how the user's choice compares to the option set."""
    labels = [opt["label"] for opt in scenario["options"]]
    colors = ["#6366F1" if lbl == chosen else "#2D3142" for lbl in labels]
    values = [1 if lbl == chosen else 0 for lbl in labels]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=colors),
            text=["← You" if lbl == chosen else "" for lbl in labels],
            textposition="outside",
        )
    )
    fig.update_layout(
        showlegend=False,
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=11)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# SUMMARY SCREEN (after all 5 scenarios)
# ---------------------------------------------------------------------------
def _render_summary():
    st.success("🎉 You've completed all 5 ethics scenarios!")
    st.markdown("### 🧭 Your Decision Profile")

    choices = st.session_state.a4_choices
    if not choices:
        st.info("No decisions recorded yet.")
        return

    # Timeline of choices
    for i, c in enumerate(choices, 1):
        st.markdown(f"**{i}. {c['scenario_title']}** — *{c['choice']}*")

    st.divider()

    # Aggregate insight
    consensus_count = sum(
        1 for c in choices
        if c["choice"] == next(
            (s["consensus"] for s in SCENARIOS if s["id"] == c["scenario_id"]),
            None,
        )
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Scenarios completed", f"{len(choices)}/{len(SCENARIOS)}")
    with col2:
        st.metric("Consensus matches", f"{consensus_count}/{len(choices)}")
    with col3:
        pct = round(100 * consensus_count / max(len(choices), 1))
        st.metric("Alignment score", f"{pct}%")

    st.divider()

    # Discussion prompt
    st.markdown("### 💬 Take it to the room")
    st.info(
        "**Discuss with your neighbour:** Which scenario felt hardest? "
        "Why do you think that is? Was there a 'right' answer, or just trade-offs?"
    )

    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Restart Activity 4", use_container_width=True):
            _reset_activity()
            st.rerun()
    with col2:
        if st.button("📊 Go to Live Dashboard", use_container_width=True, type="primary"):
            st.session_state.current_page = "📊 Live Dashboard"
            st.rerun()


# ---------------------------------------------------------------------------
# RESET HELPER
# ---------------------------------------------------------------------------
def _reset_activity():
    """Clear all Activity 4 state for a fresh run."""
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith("a4_")]
    for k in keys_to_clear:
        del st.session_state[k]
    st.session_state.a4_index = 0
    st.session_state.a4_choices = []