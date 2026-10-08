"""Activity 3: The 90-Day Pilot Sprint — Case Study → Plan → Reality Check.

Flow:
    Phase 1 — See the NCRB case study (4 cards, expandable)
    Phase 2 — Plan your own project (4-stage form with problem-statement helper)
    Phase 3 — Groq Reality Check (JSON critique)
    Phase 4 — Download your Direction Plan

Design notes:
    - No SQLite. Everything lives in st.session_state.
    - Persistence is stubbed via _persist_plan() — add db.py later to enable.
    - Groq is optional. If AI mode is off, a rule-based fallback runs.
"""
import json
from datetime import datetime

import streamlit as st

from utils.groq_client import is_llm_available, critique_plan


# ===========================================================================
# CASE STUDY CONTENT
# ===========================================================================
CASE_STUDY = [
    {
        "stage": "1",
        "icon": "🎯",
        "title": "Question & Scope",
        "question": (
            "Why are student suicides rising in India, and how do patterns "
            "differ across states and genders from 2018 to 2022?"
        ),
        "did": [
            "Picked a specific question answerable with real data",
            "Ruled out age-wise breakdown (not in the source)",
            "Committed to 2018–2022 (no extrapolation)",
        ],
        "lesson": (
            "A good project starts with a question you can answer with the "
            "data you actually have — not the data you wish you had."
        ),
    },
    {
        "stage": "2",
        "icon": "📊",
        "title": "Data & Honesty",
        "question": (
            "Where did the data come from, and what's missing from it?"
        ),
        "did": [
            "Used 8 official NCRB CSVs via India Data Portal",
            "Documented every gap (no age breakdown; police-recorded undercount)",
            "Flagged Ladakh only appearing from 2020",
        ],
        "lesson": (
            "Every dataset has gaps. The professional move is to document "
            "them, not hide them."
        ),
    },
    {
        "stage": "3",
        "icon": "🛠️",
        "title": "Build & Show",
        "question": "What will you build, and what's the ONE thing people see?",
        "did": [
            "Streamlit + Plotly + Pandas — free stack, no APIs",
            "Two pages: main dashboard + student focus",
            "Fixed 5-bracket color scale on the map (honest comparison)",
        ],
        "lesson": (
            "The one technical decision that matters most is usually about "
            "honesty, not sophistication."
        ),
    },
    {
        "stage": "4",
        "icon": "🚧",
        "title": "Limits & Delivery",
        "question": "What are you NOT claiming, and how will people access it?",
        "did": [
            "Explicitly did NOT claim a student suicide rate (no youth denominator)",
            "Documented limitations on the page itself",
            "Deployed free on Streamlit Community Cloud",
        ],
        "lesson": (
            "A project isn't done when it works — it's done when people can "
            "use it and know what it doesn't say."
        ),
    },
]


# ===========================================================================
# RULE-BASED FALLBACK CRITIQUE (used when AI mode is off)
# ===========================================================================
def _fallback_critique(plan: dict) -> dict:
    """Simple heuristic critique when no LLM is available."""
    strengths, gaps = [], []

    # Question check
    q = plan.get("stage1_question", "")
    if len(q.split()) >= 8:
        strengths.append("Question is specific enough to be answerable.")
    else:
        gaps.append("Question is too short — add context (who, when, where).")

    # Scope check
    if plan.get("stage1_scope", "").strip():
        strengths.append("You defined what's out of scope — rare and valuable.")
    else:
        gaps.append("Stage 1 is missing 'out of scope' — that's how projects drift.")

    # Data check
    if plan.get("stage2_data", "").strip():
        strengths.append("Data source is named, not vague.")
    else:
        gaps.append("No data source named — this is where projects die in week 2.")

    if not plan.get("stage2_missing", "").strip():
        gaps.append(
            "Stage 2 is missing 'what's missing from your data' — the NCRB "
            "case study made this the centerpiece of its honesty."
        )

    # Build check
    if not plan.get("stage3_one_thing", "").strip():
        gaps.append(
            "You didn't name the ONE thing people see. Scope will expand "
            "uncontrollably without it."
        )

    # Limits check
    if not plan.get("stage4_not_claiming", "").strip():
        gaps.append(
            "Stage 4 is missing 'what you're NOT claiming'. This is what "
            "builds trust in your work."
        )

    # Grade
    gap_count = len(gaps)
    if gap_count <= 1:
        grade = "Strong"
    elif gap_count <= 3:
        grade = "Promising"
    elif gap_count <= 5:
        grade = "Needs Work"
    else:
        grade = "Fragile"

    # Kill risk
    risk_map = {
        "Data not available": "Data acquisition will block you by week 3. Start collecting now, before writing any code.",
        "Scope too big for 90 days": "Your scope is too broad. Cut it in half. Then cut it again.",
        "Ethical/sensitive topic": "Add a framing paragraph before week 6 — reviewers will ask.",
        "No one will use it": "Talk to 3 potential users before building anything.",
        "I'll get bored / lose motivation": "Set a weekly demo. Show someone every Friday.",
        "Technical blocker": "Prototype the risky technical piece in week 1, not week 8.",
    }
    kill_risk = risk_map.get(
        plan.get("stage4_risk", ""),
        "Undefined risk — name one before starting.",
    )

    next_step = (
        "Week 1: Write 3 sentences on what your project will NOT claim. "
        "If you can't, your scope is still too big."
    )

    return {
        "grade": grade,
        "strengths": strengths[:3] or ["Plan has structure — that's already ahead of most."],
        "gaps": gaps[:3] or ["No obvious gaps — but reread Stage 4 and sharpen it."],
        "kill_risk": kill_risk,
        "next_step": next_step,
        "ncrb_comparison": (
            "Your plan was graded against the NCRB Suicide Dashboard template — "
            "the 4 stages that made that project real. Rule-based critique only; "
            "enable AI mode for a deeper review."
        ),
    }


# ===========================================================================
# PERSISTENCE HOOK (no-op until db.py exists)
# ===========================================================================
def _persist_plan(plan: dict, critique: dict):
    """Optional persistence. Silently no-ops if db.py isn't installed yet."""
    try:
        from db import save_a3_plan  # type: ignore
        save_a3_plan(
            participant_id=st.session_state.participant_id,
            **plan,
            llm_grade=critique.get("grade"),
            llm_response=json.dumps(critique),
        )
    except ImportError:
        pass
    except Exception:
        pass


# ===========================================================================
# DOWNLOAD BUILDER
# ===========================================================================
def _build_download_text(plan: dict, critique: dict) -> str:
    """Build the downloadable Direction Plan as markdown text."""
    lines = [
        "━" * 60,
        "YOUR 90-DAY DIRECTION PLAN",
        f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
        "GenAI Innovation Studio · UGC-MMTTC Refresher Course",
        "━" * 60,
        "",
        "STAGE 1 — PROBLEM & USERS",
        f"  Question:      {plan.get('stage1_question', '—')}",
        f"  Out of scope:  {plan.get('stage1_scope', '—')}",
        "",
        "STAGE 2 — DATA & HONESTY",
        f"  Data source:   {plan.get('stage2_data', '—')}",
        f"  What's missing: {plan.get('stage2_missing', '—')}",
        "",
        "STAGE 3 — BUILD & SHOW",
        f"  What I'll build: {plan.get('stage3_build', '—')}",
        f"  The ONE thing:   {plan.get('stage3_one_thing', '—')}",
        f"  GenAI's role:    {plan.get('stage3_genai_role', '—')}",
        "",
        "STAGE 4 — LIMITS & DELIVERY",
        f"  Not claiming:  {plan.get('stage4_not_claiming', '—')}",
        f"  Access:        {plan.get('stage4_access', '—')}",
        f"  Top risk:      {plan.get('stage4_risk', '—')}",
        "",
        "━" * 60,
        f"REALITY CHECK  ·  Grade: {critique.get('grade', '—')}",
        "━" * 60,
        "",
        "Strengths:",
    ]
    for s in critique.get("strengths", []):
        lines.append(f"  • {s}")
    lines += ["", "Gaps:"]
    for g in critique.get("gaps", []):
        lines.append(f"  • {g}")
    lines += [
        "",
        "Kill Risk:",
        f"  {critique.get('kill_risk', '—')}",
        "",
        "Next Step:",
        f"  {critique.get('next_step', '—')}",
        "",
        "Reference: NCRB Suicide Data Dashboard (India, 2018–2022)",
        "━" * 60,
    ]
    return "\n".join(lines)


# ===========================================================================
# RENDER — MAIN ENTRY
# ===========================================================================
def render():
    st.markdown("## 🚀 Activity 3: The 90-Day Pilot Sprint")
    st.caption(
        "See a real project. Plan your own. Get an honest Reality Check."
    )

    # ------------------ PHASE 1: CASE STUDY ------------------
    _render_case_study()

    st.divider()

    # ------------------ PHASE 2: YOUR PLAN ------------------
    _render_plan_form()

    # ------------------ PHASE 3: REALITY CHECK ------------------
    if st.session_state.get("a3_blueprint") and st.session_state.get("a3_critique"):
        st.divider()
        _render_report()

    # ------------------ NAVIGATION ------------------
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➡️ Next: Ethics", use_container_width=True, type="primary"):
            st.session_state.current_page = "4️⃣ The AI Ethics Hot Seat"
            st.rerun()


# ===========================================================================
# PHASE 1 — CASE STUDY CARDS
# ===========================================================================
def _render_case_study():
    st.markdown("### 📖 Phase 1 — See the real one")
    st.caption(
        "Before you plan, look at how a real project was scoped. "
        "This is the NCRB Suicide Data Dashboard — a project that shipped."
    )

    with st.expander("ℹ️ About this case study (30 sec read)", expanded=False):
        st.markdown(
            """
            A **free, interactive Streamlit dashboard** on India's official
            NCRB suicide data (2018–2022). State-wise maps, gender breakdowns,
            a dedicated student-suicide page, and honest documentation of what
            the data can and cannot say.

            **Built with:** Python · Streamlit · Plotly · Pandas · 8 public CSVs.
            **No paid services. No APIs. No database.**

            Every stage below is how the project actually happened — and it's
            the template you'll use for your own plan.
            """
        )

    for card in CASE_STUDY:
        with st.expander(
            f"{card['icon']}  Stage {card['stage']} — {card['title']}",
            expanded=False,
        ):
            st.markdown(f"**The question:** _{card['question']}_")
            st.markdown("**What we did:**")
            for item in card["did"]:
                st.markdown(f"- {item}")
            st.info(f"💡 **Lesson:** {card['lesson']}")


# ===========================================================================
# PHASE 2 — PLAN FORM (with problem-statement helper)
# ===========================================================================
def _render_plan_form():
    st.markdown("### 📝 Phase 2 — Plan yours")
    st.caption(
        "Four stages. One page. This is your 90-day direction — not a wish list."
    )

    blueprint = st.session_state.get("a3_blueprint", {})

    with st.form("plan_form", clear_on_submit=False):
        # ---------- STAGE 1 ----------
        st.markdown("#### 🎯 Stage 1 — Problem & Users")

        with st.expander("💡 Need help phrasing it? Use this template", expanded=False):
            st.markdown(
                """
                **IBM's proven problem-statement formula:**

                > *How can we help **[a specific user or group]** find a way to
                > **[do what]** so that they can **[a measurable outcome]**?*

                **Example:**
                > How can we help **district court clerks in Tier-2 cities**
                > find a way to **auto-index case files** so that they can
                > **reduce manual review time by 60%**?

                **Why it works:** It forces you to name the user, the action,
                and the measurable outcome — all three must be present.
                """
            )

        q1 = st.text_area(
            "What specific question will your project answer in 90 days?",
            value=blueprint.get("stage1_question", ""),
            height=80,
            placeholder="How can we help [who] find a way to [do what] so that they can [outcome]?",
            help="'AI in education' is a topic. A question has a subject, a timeframe, and a measurable angle.",
        )
        q2 = st.text_input(
            "What are you explicitly NOT doing? (out of scope)",
            value=blueprint.get("stage1_scope", ""),
            placeholder="e.g., I'm not covering postgraduate students or international learners.",
        )

        st.divider()

        # ---------- STAGE 2 ----------
        st.markdown("#### 📊 Stage 2 — Data & Honesty")
        d1 = st.text_input(
            "Where will your data come from?",
            value=blueprint.get("stage2_data", ""),
            placeholder="e.g., 3 years of attendance records from my institution",
            help="A 200-row real CSV beats a 2M-row dataset you don't understand.",
        )
        d2 = st.text_area(
            "What's missing or unreliable about it?",
            value=blueprint.get("stage2_missing", ""),
            height=80,
            placeholder="e.g., Attendance has gaps during exam weeks; names vary across years.",
        )

        st.divider()

        # ---------- STAGE 3 ----------
        st.markdown("#### 🛠️ Stage 3 — Build & Show")
        b1 = st.text_area(
            "What will you build? (2–3 sentences max)",
            value=blueprint.get("stage3_build", ""),
            height=80,
            placeholder="e.g., A Streamlit dashboard with one map and one trend chart.",
        )
        b2 = st.text_input(
            "The ONE thing people will see first",
            value=blueprint.get("stage3_one_thing", ""),
            placeholder="e.g., A single map showing dropout hotspots by district.",
        )
        b3 = st.selectbox(
            "Where does GenAI help?",
            [
                "Summarize sources",
                "Generate hypotheses",
                "Draft narratives",
                "Write/refactor code",
                "Clean and transform data",
            ],
            index=0,
        )

        st.divider()

        # ---------- STAGE 4 ----------
        st.markdown("#### 🚧 Stage 4 — Limits & Delivery")
        l1 = st.text_area(
            "What are you honestly NOT claiming?",
            value=blueprint.get("stage4_not_claiming", ""),
            height=80,
            placeholder="e.g., I'm not claiming causation — only observed patterns.",
            help="The best projects say what they don't do. It builds trust.",
        )
        l2 = st.text_input(
            "How will people access it?",
            value=blueprint.get("stage4_access", ""),
            placeholder="e.g., Streamlit Cloud link shared via email",
        )
        l3 = st.selectbox(
            "Top risk you're worried about",
            [
                "Data not available",
                "Scope too big for 90 days",
                "Ethical/sensitive topic",
                "No one will use it",
                "I'll get bored / lose motivation",
                "Technical blocker",
            ],
            index=0,
        )

        st.divider()

        submitted = st.form_submit_button(
            "🔍 Run my Reality Check",
            use_container_width=True,
            type="primary",
        )

    # ---------- HANDLE SUBMISSION ----------
    if submitted:
        plan = {
            "stage1_question": q1.strip(),
            "stage1_scope": q2.strip(),
            "stage2_data": d1.strip(),
            "stage2_missing": d2.strip(),
            "stage3_build": b1.strip(),
            "stage3_one_thing": b2.strip(),
            "stage3_genai_role": b3,
            "stage4_not_claiming": l1.strip(),
            "stage4_access": l2.strip(),
            "stage4_risk": l3,
        }

        if not plan["stage1_question"]:
            st.warning("Please fill in Stage 1 — the question is the whole point.")
            return

        with st.spinner("Running your Reality Check…"):
            if is_llm_available():
                critique = critique_plan(plan)
            else:
                critique = _fallback_critique(plan)

        st.session_state.a3_blueprint = plan
        st.session_state.a3_critique = critique
        st.session_state.a3_submitted = True

        _persist_plan(plan, critique)

        st.rerun()


# ===========================================================================
# PHASE 3 — REPORT CARD
# ===========================================================================
def _render_report():
    plan = st.session_state.a3_blueprint
    critique = st.session_state.a3_critique

    st.markdown("### 📋 Phase 3 — Your Reality Check")

    grade = critique.get("grade", "—")
    grade_emoji = {
        "Strong": "🟢",
        "Promising": "🟡",
        "Needs Work": "🟠",
        "Fragile": "🔴",
    }.get(grade, "⚪")

    st.markdown(
        f"""
        <div class="report-card">
            <div class="report-grade">
                GRADE: <span class="grade-value">{grade}</span> {grade_emoji}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### ✅ Strengths")
    for s in critique.get("strengths", []):
        st.markdown(f"- {s}")

    st.markdown("#### ⚠️ Gaps")
    for g in critique.get("gaps", []):
        st.markdown(f"- {g}")

    st.markdown("#### 🚨 Kill Risk")
    st.warning(critique.get("kill_risk", "—"))

    st.markdown("#### 🎯 Next Step")
    st.success(critique.get("next_step", "—"))

    st.markdown("#### 📎 How this compares to the NCRB template")
    st.caption(critique.get("ncrb_comparison", "—"))

    st.divider()
    st.markdown("### 📄 Phase 4 — Your Direction Plan")
    download_text = _build_download_text(plan, critique)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            "💾 Download as .md",
            data=download_text,
            file_name=f"direction_plan_{st.session_state.participant_id}.md",
            mime="text/markdown",
            use_container_width=True,
            type="primary",
        )
    with col2:
        if st.button("🔁 Revise my plan", use_container_width=True):
            st.session_state.a3_submitted = False
            st.session_state.a3_critique = None
            st.rerun()