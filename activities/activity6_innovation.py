"""Activity 6: AI Innovation & Entrepreneurship.

Flip the 4-stage research template into a venture lens:
    Stage 1: Problem & Customer
    Stage 2: Unfair Advantage
    Stage 3: Product & Wedge
    Stage 4: Business Model & Moat

Includes a Priority Grid widget to help participants position their idea.
"""
import json
from datetime import datetime

import streamlit as st

from utils.groq_client import is_llm_available, critique_venture


# ===========================================================================
# CASE STUDY — Sarvam AI
# ===========================================================================
SARVAM_CASE = {
    "name": "Sarvam AI",
    "tagline": "India's sovereign AI — built from scratch, for India",
    "founded": "2023 · IIT Madras incubated · AI4Bharat lineage",
    "milestones": [
        ("Apr 2025", "Selected for IndiaAI Mission — granted 4,096 H100 GPUs (₹246.72 cr)"),
        ("Feb 2026", "Released Sarvam 30B & Sarvam 105B — trained from scratch, Apache 2.0"),
        ("Jun 2026", "$234M Series B at $1.5B valuation — India's second AI unicorn (HCLTech led)"),
        ("Benchmark", "Sarvam 105B beats GPT-4 on ~90% of Indic benchmarks at 1/5th cost"),
    ],
    "lesson": (
        "Don't try to beat the giants at their own game — change the game "
        "they're not playing. Sarvam didn't compete on general capability. "
        "They went deep on Indian languages — a lane the giants ignored."
    ),
    "steal_these": [
        "Pick a lane where global players are structurally weak.",
        "Own your data pipeline — it becomes your moat, not your model.",
        "Ship open source to build developer trust early.",
    ],
}


# ===========================================================================
# RULE-BASED FALLBACK (used when AI mode is off)
# ===========================================================================
def _fallback_venture_critique(plan: dict) -> dict:
    strengths, gaps = [], []

    problem = plan.get("s1_problem", "")
    if len(problem.split()) >= 8:
        strengths.append("Problem statement is specific enough to test.")
    else:
        gaps.append("Problem is too vague — name the specific user and the specific pain.")

    if plan.get("s1_customer", "").strip():
        strengths.append("Customer segment is named — not 'everyone'.")
    else:
        gaps.append("No customer defined. 'Everyone' is never a customer.")

    if plan.get("s2_advantage", "").strip():
        strengths.append("You named an unfair advantage — most founders can't.")
    else:
        gaps.append("No unfair advantage — why won't a competitor just copy you?")

    if not plan.get("s3_wedge", "").strip():
        gaps.append("No wedge defined — you need one narrow entry point, not a broad launch.")

    if not plan.get("s4_revenue", "").strip():
        gaps.append("No revenue model named. Who actually pays, and how much?")

    if not plan.get("s4_moat", "").strip():
        gaps.append("No moat. What stops OpenAI or Google from shipping this next quarter?")

    # Priority grid awareness
    quadrant = plan.get("priority_quadrant", "unset")
    quadrant_notes = {
        "high_easy": "You placed this in the MVP quadrant — good instinct.",
        "high_hard": "You placed this in 'high value, hard to build'. Shrink the wedge.",
        "low_easy": "You placed this in 'low value, easy'. Is this worth doing at all?",
        "low_hard": "You placed this in 'not a good thing to do'. Reconsider the idea.",
    }
    if quadrant in quadrant_notes:
        strengths.append(quadrant_notes[quadrant])

    gap_count = len(gaps)
    grade = (
        "Strong" if gap_count <= 1
        else "Promising" if gap_count <= 3
        else "Needs Work" if gap_count <= 5
        else "Fragile"
    )

    return {
        "grade": grade,
        "strengths": strengths[:3] or ["Plan has structure — ahead of most pitch decks."],
        "gaps": gaps[:3] or ["No obvious gaps — reread Stage 4 and sharpen the moat."],
        "kill_risk": (
            "Undefined kill risk. If you can't name what kills this in week 3, "
            "you haven't pressure-tested the idea."
        ),
        "next_step": (
            "Week 1: Talk to 5 potential customers. If none of them can describe "
            "the problem in their own words, your problem statement is wrong."
        ),
        "sarvam_comparison": (
            "Rule-based critique only. Enable AI mode for a deeper founder-style review."
        ),
    }


# ===========================================================================
# PERSISTENCE HOOK
# ===========================================================================
def _persist_venture(plan: dict, critique: dict):
    try:
        from db import save_a6_venture  # type: ignore
        save_a6_venture(
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
    lines = [
        "━" * 60,
        "YOUR GENAI VENTURE BLUEPRINT",
        f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
        "GenAI Innovation Studio · UGC-MMTTC Refresher Course",
        "━" * 60,
        "",
        "STAGE 1 — PROBLEM & CUSTOMER",
        f"  Problem:   {plan.get('s1_problem', '—')}",
        f"  Customer:  {plan.get('s1_customer', '—')}",
        "",
        "STAGE 2 — UNFAIR ADVANTAGE",
        f"  Advantage: {plan.get('s2_advantage', '—')}",
        f"  Data/Assets: {plan.get('s2_assets', '—')}",
        "",
        "STAGE 3 — PRODUCT & WEDGE",
        f"  MVP:       {plan.get('s3_mvp', '—')}",
        f"  Wedge:     {plan.get('s3_wedge', '—')}",
        f"  GenAI role: {plan.get('s3_genai_role', '—')}",
        "",
        "STAGE 4 — BUSINESS MODEL & MOAT",
        f"  Revenue:   {plan.get('s4_revenue', '—')}",
        f"  Moat:      {plan.get('s4_moat', '—')}",
        f"  Kill risk: {plan.get('s4_risk', '—')}",
        "",
        f"PRIORITY GRID: {plan.get('priority_quadrant', 'unset')}",
        "",
        "━" * 60,
        f"FOUNDER REALITY CHECK  ·  Grade: {critique.get('grade', '—')}",
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
        "Reference case: Sarvam AI (India's sovereign AI unicorn, 2026)",
        "━" * 60,
    ]
    return "\n".join(lines)


# ===========================================================================
# PRIORITY GRID
# ===========================================================================
def _render_priority_grid():
    st.markdown("### 🎯 Priority Grid — where does your idea sit?")
    st.caption(
        "Value to the user (rows) × Ease of building (columns). "
        "Aim for the top-left. Walk away from the bottom-right."
    )

    current = st.session_state.get("a6_priority", None)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="activity-card" style="min-height:180px;">
                <div class="badge-soft badge">✅ Top-left</div>
                <h4 style="margin-top:0.75rem;">High value · Easy to build</h4>
                <p style="color:#1F2937; font-size:0.9rem;">
                    Do this first. This is your MVP.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "My idea belongs here",
            key="a6_grid_tl",
            use_container_width=True,
            type="primary" if current == "high_easy" else "secondary",
        ):
            st.session_state.a6_priority = "high_easy"
            st.rerun()

        st.markdown(
            """
            <div class="activity-card" style="min-height:180px;">
                <div class="badge-soft badge">⚠️ Bottom-left</div>
                <h4 style="margin-top:0.75rem;">Low value · Easy to build</h4>
                <p style="color:#1F2937; font-size:0.9rem;">
                    A distraction. Skip it — even if it's tempting.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "My idea belongs here",
            key="a6_grid_bl",
            use_container_width=True,
            type="primary" if current == "low_easy" else "secondary",
        ):
            st.session_state.a6_priority = "low_easy"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="activity-card" style="min-height:180px;">
                <div class="badge-soft badge">🚀 Top-right</div>
                <h4 style="margin-top:0.75rem;">High value · Hard to build</h4>
                <p style="color:#1F2937; font-size:0.9rem;">
                    Good ambition. Build a smaller wedge first.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "My idea belongs here",
            key="a6_grid_tr",
            use_container_width=True,
            type="primary" if current == "high_hard" else "secondary",
        ):
            st.session_state.a6_priority = "high_hard"
            st.rerun()

        st.markdown(
            """
            <div class="activity-card" style="min-height:180px;">
                <div class="badge-soft badge">🛑 Bottom-right</div>
                <h4 style="margin-top:0.75rem;">Low value · Hard to build</h4>
                <p style="color:#1F2937; font-size:0.9rem;">
                    Not a good thing to do. Walk away.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "My idea belongs here",
            key="a6_grid_br",
            use_container_width=True,
            type="primary" if current == "low_hard" else "secondary",
        ):
            st.session_state.a6_priority = "low_hard"
            st.rerun()

    if current:
        labels = {
            "high_easy": "✅ Top-left — proceed with this MVP.",
            "high_hard": "🚀 Top-right — build a smaller wedge first.",
            "low_easy": "⚠️ Bottom-left — cut this from scope.",
            "low_hard": "🛑 Bottom-right — walk away from this.",
        }
        st.info(f"You placed your idea in: **{labels.get(current, current)}**")


# ===========================================================================
# RENDER — MAIN
# ===========================================================================
def render():
    st.markdown("## 💡 Activity 6: AI Innovation & Entrepreneurship")
    st.caption(
        "Turn your project mindset into a venture mindset. "
        "Learn from Sarvam AI, then pitch your own idea."
    )

    _render_case_study()

    st.divider()

    _render_priority_grid()

    st.divider()

    _render_venture_form()

    if st.session_state.get("a6_venture") and st.session_state.get("a6_critique"):
        st.divider()
        _render_report()

    st.divider()
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➡️ Next: Mentoring", use_container_width=True, type="primary"):
            st.session_state.current_page = "6️⃣ Project Mentoring & Implementation"
            st.rerun()


# ===========================================================================
# CASE STUDY
# ===========================================================================
def _render_case_study():
    st.markdown("### 📖 Phase 1 — The Sarvam AI story")
    st.caption(
        "One Indian startup. Three years. One lesson worth stealing."
    )

    with st.expander("🇮🇳 Who is Sarvam AI?", expanded=False):
        st.markdown(
            f"""
            **{SARVAM_CASE['name']}** — _{SARVAM_CASE['tagline']}_

            Founded **{SARVAM_CASE['founded']}**. Backed by the IndiaAI Mission.
            Now India's second AI unicorn.

            They didn't try to beat OpenAI at general intelligence.
            They trained models **from scratch, for Indian languages**, and
            beat GPT-4 on Indic benchmarks at a fraction of the cost.
            """
        )

    st.markdown("**The milestones that mattered:**")
    for date, event in SARVAM_CASE["milestones"]:
        st.markdown(f"- **{date}** — {event}")

    st.info(f"💡 **Lesson:** {SARVAM_CASE['lesson']}")

    with st.expander("🎯 3 things founders can steal from Sarvam"):
        for i, item in enumerate(SARVAM_CASE["steal_these"], 1):
            st.markdown(f"{i}. {item}")


# ===========================================================================
# VENTURE FORM
# ===========================================================================
def _render_venture_form():
    st.markdown("### 📝 Phase 2 — Pitch your venture")
    st.caption(
        "Four stages, one page. This is a founder's version of the same "
        "discipline you used in Activity 3."
    )

    existing = st.session_state.get("a6_venture", {})

    with st.form("venture_form", clear_on_submit=False):
        # -------- STAGE 1 --------
        st.markdown("#### 🎯 Stage 1 — Problem & Customer")
        s1_problem = st.text_area(
            "What specific problem are you solving, and for whom?",
            value=existing.get("s1_problem", ""),
            height=80,
            placeholder="e.g., Indian district court clerks spend 6 hours/week manually indexing case files.",
        )
        s1_customer = st.text_input(
            "Who is your first customer? (be specific, not 'everyone')",
            value=existing.get("s1_customer", ""),
            placeholder="e.g., District court clerks in Tier-2 cities in Karnataka",
        )

        st.divider()

        # -------- STAGE 2 --------
        st.markdown("#### 🛡️ Stage 2 — Unfair Advantage")
        s2_advantage = st.text_area(
            "What do you have that others don't? (data, access, domain depth)",
            value=existing.get("s2_advantage", ""),
            height=80,
            placeholder="e.g., 3 years of access to court workflows via a family connection.",
        )
        s2_assets = st.text_input(
            "What data or assets do you already own?",
            value=existing.get("s2_assets", ""),
            placeholder="e.g., 20,000 anonymised case files, hand-labelled",
        )

        st.divider()

        # -------- STAGE 3 --------
        st.markdown("#### 🛠️ Stage 3 — Product & Wedge")
        s3_mvp = st.text_area(
            "What's your MVP? (2-3 sentences)",
            value=existing.get("s3_mvp", ""),
            height=80,
            placeholder="e.g., A CLI tool that auto-summarises case files into a structured index.",
        )
        s3_wedge = st.text_input(
            "What's your wedge — the ONE niche you win first?",
            value=existing.get("s3_wedge", ""),
            placeholder="e.g., One court, one judge's chambers, 6-week pilot.",
        )
        s3_genai_role = st.selectbox(
            "Where does GenAI sit in your product?",
            [
                "Core — the product IS the AI",
                "Feature — AI enhances an existing product",
                "Internal — AI is only used to build the product",
                "Not yet — I'm still figuring this out",
            ],
            index=0,
        )

        st.divider()

        # -------- STAGE 4 --------
        st.markdown("#### 💰 Stage 4 — Business Model & Moat")
        s4_revenue = st.text_input(
            "Who pays, and how much?",
            value=existing.get("s4_revenue", ""),
            placeholder="e.g., District courts pay ₹50k/month per installation.",
        )
        s4_moat = st.text_area(
            "Why can't OpenAI or Google just do this?",
            value=existing.get("s4_moat", ""),
            height=80,
            placeholder="e.g., They don't touch Indian legal workflows; the moat is the data pipeline.",
        )
        s4_risk = st.selectbox(
            "What's the biggest kill risk?",
            [
                "No one actually has this problem",
                "Distribution — I can't reach customers",
                "Copycats — a bigger player ships it",
                "Unit economics — I can't make money",
                "Regulation — legal/compliance blocks it",
                "I lose interest — no founder-market fit",
            ],
            index=0,
        )

        st.divider()

        submitted = st.form_submit_button(
            "🔍 Run my Founder Reality Check",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        plan = {
            "s1_problem": s1_problem.strip(),
            "s1_customer": s1_customer.strip(),
            "s2_advantage": s2_advantage.strip(),
            "s2_assets": s2_assets.strip(),
            "s3_mvp": s3_mvp.strip(),
            "s3_wedge": s3_wedge.strip(),
            "s3_genai_role": s3_genai_role,
            "s4_revenue": s4_revenue.strip(),
            "s4_moat": s4_moat.strip(),
            "s4_risk": s4_risk,
            "priority_quadrant": st.session_state.get("a6_priority", "unset"),
        }

        if not plan["s1_problem"]:
            st.warning("Stage 1 is empty — the problem is the whole pitch.")
            return

        with st.spinner("Reviewing your venture…"):
            if is_llm_available():
                critique = critique_venture(plan)
            else:
                critique = _fallback_venture_critique(plan)

        st.session_state.a6_venture = plan
        st.session_state.a6_critique = critique
        _persist_venture(plan, critique)
        st.rerun()


# ===========================================================================
# REPORT
# ===========================================================================
def _render_report():
    plan = st.session_state.a6_venture
    critique = st.session_state.a6_critique

    st.markdown("### 📋 Phase 3 — Founder Reality Check")

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

    st.markdown("#### 📎 How this compares to Sarvam's playbook")
    st.caption(critique.get("sarvam_comparison", "—"))

    st.divider()
    st.markdown("### 📄 Phase 4 — Your Venture Blueprint")
    download_text = _build_download_text(plan, critique)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            "💾 Download as .md",
            data=download_text,
            file_name=f"venture_blueprint_{st.session_state.participant_id}.md",
            mime="text/markdown",
            use_container_width=True,
            type="primary",
        )
    with col2:
        if st.button("🔁 Revise my pitch", use_container_width=True):
            st.session_state.a6_critique = None
            st.rerun()