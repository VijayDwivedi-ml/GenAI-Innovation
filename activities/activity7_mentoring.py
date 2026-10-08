"""Activity 7: Project Mentoring & Implementation.

No new form. Auto-pulls from Activity 3's plan and critique, then generates:
    1. A 90-day implementation checklist
    2. A who-to-ask-for-help directory
    3. An Empathy Map for the user
    4. A downloadable one-page Mentor Brief (pre-filled from Activity 3 + Empathy Map)
"""
from datetime import datetime

import streamlit as st


# ===========================================================================
# CONTENT
# ===========================================================================
CHECKLIST = [
    {
        "phase": "Weeks 1–4",
        "title": "Data & Scope",
        "tasks": [
            "Pull one year of data. Run .info() and .isnull().sum().",
            "Document every gap you find — write it down before coding.",
            "Rewrite your question as one sentence. If you can't, it's still too big.",
            "Identify ONE person who has done something similar and ask them 3 questions.",
        ],
    },
    {
        "phase": "Weeks 5–8",
        "title": "Build & Test",
        "tasks": [
            "Ship the smallest possible version — one chart, one page, one insight.",
            "Show it to 3 real users. Watch them use it. Don't explain.",
            "Fix only what breaks their understanding. Ignore everything else.",
            "Document what you're NOT claiming in the app itself.",
        ],
    },
    {
        "phase": "Weeks 9–12",
        "title": "Refine & Present",
        "tasks": [
            "Polish the one chart that matters. Kill the rest.",
            "Write a one-page summary: what you did, what you found, what you didn't.",
            "Deploy it somewhere public. A URL beats a screenshot.",
            "Present to one audience — class, team, or a mentor.",
        ],
    },
]

MENTOR_TYPES = [
    {
        "icon": "🎓",
        "type": "Academic Mentor",
        "who": "Your faculty guide or a professor in your department",
        "ask": "Question framing, literature grounding, methodology critique",
    },
    {
        "icon": "💼",
        "type": "Industry Mentor",
        "who": "Someone in the field via LinkedIn — 1 intro away",
        "ask": "Real-world relevance, what tools they actually use",
    },
    {
        "icon": "🧑‍💻",
        "type": "Peer / Community",
        "who": "Discord, Hugging Face, r/datascience, local meetups",
        "ask": "Debugging, tool recommendations, moral support",
    },
    {
        "icon": "🛠️",
        "type": "Tool Support",
        "who": "Groq forums, Streamlit docs, Plotly community",
        "ask": "Specific technical blockers, API issues",
    },
    {
        "icon": "🌐",
        "type": "Domain Expert",
        "who": "The person whose problem you're solving",
        "ask": "Whether your output is actually useful",
    },
]


# ===========================================================================
# MENTOR BRIEF BUILDER (auto-fills from Activity 3 + Empathy Map)
# ===========================================================================
def _build_mentor_brief() -> str:
    plan = st.session_state.get("a3_blueprint", {}) or {}
    critique = st.session_state.get("a3_critique", {}) or {}
    empathy = st.session_state.get("a7_empathy", {}) or {}
    name = st.session_state.get("participant_name", "") or "Participant"
    pid = st.session_state.get("participant_id", "—")

    lines = [
        "━" * 60,
        "MENTOR BRIEF",
        f"From: {name} ({pid})",
        f"Date: {datetime.now().strftime('%d %b %Y')}",
        "GenAI Innovation Studio · UGC-MMTTC Refresher Course",
        "━" * 60,
        "",
        "PROJECT TITLE",
        f"  {plan.get('stage1_question', '—')}",
        "",
        "PROBLEM STATEMENT",
        f"  {plan.get('stage1_scope', '—')}",
        "",
        "DATA SOURCE",
        f"  {plan.get('stage2_data', '—')}",
        "",
        "WHAT'S MISSING FROM THE DATA",
        f"  {plan.get('stage2_missing', '—')}",
        "",
        "WHAT I PLAN TO BUILD",
        f"  {plan.get('stage3_build', '—')}",
        "",
        "THE ONE THING PEOPLE WILL SEE",
        f"  {plan.get('stage3_one_thing', '—')}",
        "",
        "GENAI'S ROLE",
        f"  {plan.get('stage3_genai_role', '—')}",
        "",
        "WHAT I'M NOT CLAIMING",
        f"  {plan.get('stage4_not_claiming', '—')}",
        "",
        "HOW PEOPLE WILL ACCESS IT",
        f"  {plan.get('stage4_access', '—')}",
        "",
        "TOP RISK I'M WORRIED ABOUT",
        f"  {plan.get('stage4_risk', '—')}",
        "",
        "━" * 60,
        "EMPATHY MAP (who my user really is)",
        "━" * 60,
        "",
        f"  💬 Says:   {empathy.get('says', '—')}",
        f"  🤔 Thinks: {empathy.get('thinks', '—')}",
        f"  🏃 Does:   {empathy.get('does', '—')}",
        f"  ❤️ Feels:  {empathy.get('feels', '—')}",
        "",
        "━" * 60,
        "THE SPECIFIC ASK",
        "━" * 60,
        "",
        "I would like 30 minutes of your time to discuss:",
        "",
        "  1. Whether my problem statement is specific enough.",
        "  2. Whether my data source is credible for this question.",
        "  3. What would kill this project by week 3.",
        "",
        "If you can also suggest one person I should talk to, that would help.",
        "",
        "━" * 60,
        f"Reality Check grade: {critique.get('grade', '—')}",
        f"Next step per AI review: {critique.get('next_step', '—')}",
        "━" * 60,
    ]
    return "\n".join(lines)


# ===========================================================================
# RENDER
# ===========================================================================
def render():
    st.markdown("## 🎓 Activity 7: Project Mentoring & Implementation")
    st.caption(
        "Your plan is done. Here's how to actually ship it — "
        "and who to call when you get stuck."
    )

    # ---- Did the participant complete Activity 3? ----
    plan = st.session_state.get("a3_blueprint") or {}

    if not plan:
        st.warning(
            "⚠️ Complete **Activity 3 — The 90-Day Pilot Sprint** first. "
            "This page auto-fills from your plan there."
        )
        if st.button("→ Go to Activity 3", use_container_width=True, type="primary"):
            st.session_state.current_page = "3️⃣ The 90-Day Pilot Sprint"
            st.rerun()
        return

    st.success("✅ Your Activity 3 plan has been loaded. Everything below is auto-filled.")

    st.divider()

    # ---- Section 1: 90-day checklist ----
    _render_checklist()

    st.divider()

    # ---- Section 2: Mentor directory ----
    _render_mentor_directory()

    st.divider()

    # ---- Section 3: Empathy Map ----
    _render_empathy_map()

    st.divider()

    # ---- Section 4: Mentor Brief ----
    _render_mentor_brief()

    st.divider()

    # ---- Navigation ----
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔁 Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "📊 Live Dashboard"
            st.rerun()
    with col2:
        st.caption(f"Session: `{st.session_state.participant_id}`")


# ===========================================================================
# SECTION 1 — CHECKLIST
# ===========================================================================
def _render_checklist():
    st.markdown("### 📅 Your 90-day implementation checklist")
    st.caption("Three phases. Twelve weeks. One project that ships.")

    cols = st.columns(3)
    for i, phase in enumerate(CHECKLIST):
        with cols[i]:
            st.markdown(
                f"""
                <div class="activity-card">
                    <div class="badge-soft badge">{phase['phase']}</div>
                    <h3 style="margin-top:0.75rem;">{phase['title']}</h3>
                    <ul style="margin-top:1rem; line-height:1.8; color:#1F2937; font-size:0.92rem;">
                        {''.join(f'<li>{t}</li>' for t in phase['tasks'])}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ===========================================================================
# SECTION 2 — MENTOR DIRECTORY
# ===========================================================================
def _render_mentor_directory():
    st.markdown("### 👥 Who to ask for help")
    st.caption("You don't need to know everything. You need to know who to call.")

    for mentor in MENTOR_TYPES:
        with st.expander(f"{mentor['icon']}  {mentor['type']}", expanded=False):
            st.markdown(f"**Who:** {mentor['who']}")
            st.markdown(f"**Ask them about:** {mentor['ask']}")


# ===========================================================================
# SECTION 3 — EMPATHY MAP
# ===========================================================================
def _render_empathy_map():
    st.markdown("### 🧠 Your Empathy Map")
    st.caption(
        "Four boxes. Put yourself in your user's shoes for 2 minutes. "
        "This is what separates a real project from an assignment."
    )

    existing = st.session_state.get("a7_empathy", {})

    col1, col2 = st.columns(2)
    with col1:
        says = st.text_area(
            "💬 SAYS — What does your user say out loud?",
            value=existing.get("says", ""),
            height=100,
            placeholder="e.g., 'I waste 2 hours every day on this task.'",
            key="a7_says",
        )
        does = st.text_area(
            "🏃 DOES — What do they actually do today?",
            value=existing.get("does", ""),
            height=100,
            placeholder="e.g., They copy-paste between 3 browser tabs.",
            key="a7_does",
        )
    with col2:
        thinks = st.text_area(
            "🤔 THINKS — What do they think but not say?",
            value=existing.get("thinks", ""),
            height=100,
            placeholder="e.g., 'There must be a better way, but nobody asked.'",
            key="a7_thinks",
        )
        feels = st.text_area(
            "❤️ FEELS — What emotions are underneath?",
            value=existing.get("feels", ""),
            height=100,
            placeholder="e.g., Frustrated, overlooked, tired.",
            key="a7_feels",
        )

    if st.button("💾 Save Empathy Map", use_container_width=True):
        st.session_state.a7_empathy = {
            "says": says.strip(),
            "thinks": thinks.strip(),
            "does": does.strip(),
            "feels": feels.strip(),
        }
        st.success("Empathy map saved. It will appear in your Mentor Brief.")
        st.rerun()


# ===========================================================================
# SECTION 4 — MENTOR BRIEF
# ===========================================================================
def _render_mentor_brief():
    st.markdown("### 📄 Your one-page Mentor Brief")
    st.caption(
        "Auto-filled from your Activity 3 plan and your Empathy Map. "
        "Send this to anyone you want to mentor you. No re-typing."
    )

    brief_text = _build_mentor_brief()

    with st.expander("👀 Preview the brief", expanded=False):
        st.code(brief_text, language="text")

    st.download_button(
        "💾 Download Mentor Brief (.md)",
        data=brief_text,
        file_name=f"mentor_brief_{st.session_state.participant_id}.md",
        mime="text/markdown",
        use_container_width=True,
        type="primary",
    )

    st.info(
        "💡 **How to use it:** Send this to a potential mentor along with a "
        "short email. Ask for 30 minutes. Come prepared with the 3 questions "
        "in the brief. Most people say yes to a specific, well-prepared ask."
    )