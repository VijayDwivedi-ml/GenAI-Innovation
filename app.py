"""
GenAI Innovation
UGC-MMTTC Refresher Course — Day 11 Activity App

Main entry point. Handles:
- Page config and global CSS
- Session state initialization
- Sidebar navigation and AI mode toggle
- Routing to individual activity modules
"""
import os
from pathlib import Path

import streamlit as st

from utils.state import (
    init_state,
    reset_activity_2,
    reset_activity_4,
    reset_llm_cache,
    reset_all,
)
from utils.groq_client import is_llm_available, get_key_source
from activities import (
    activity1_truths,
    activity2_prompt_duel,
    activity3_pilot_sprint,
    activity4_ethics,
    activity5_dashboard,
    activity6_innovation,
    activity7_mentoring,
)


# ---------------------------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="GenAI Innovation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# CSS LOADER
# ---------------------------------------------------------------------------
def load_css():
    """Load the custom light-theme stylesheet from assets/styles.css."""
    css_file = Path(__file__).parent / "assets" / "styles.css"
    if css_file.exists():
        st.markdown(
            f"<style>{css_file.read_text()}</style>",
            unsafe_allow_html=True,
        )
    else:
        st.warning(f"⚠️ CSS file not found at {css_file}")


# ---------------------------------------------------------------------------
# INITIALIZE SESSION STATE
# ---------------------------------------------------------------------------
init_state()


# ---------------------------------------------------------------------------
# GLOBAL CSS  (light theme — loaded from assets/styles.css)
# ---------------------------------------------------------------------------
load_css()


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚀 GenAI Innovation ")
    st.caption("Day 11 — 15 Oct 2026")

    st.divider()

    # Participant identity
    name = st.text_input(
        "👤 Your name (optional)",
        value=st.session_state.participant_name,
        placeholder="e.g., Priya S.",
    )
    st.session_state.participant_name = name
    st.caption(f"ID: `{st.session_state.participant_id}`")

    st.divider()

    # Navigation
    PAGES = {
        "🏠 Welcome": "welcome",
        "1️⃣ Two Truths & a Hallucination": "activity1",
        "2️⃣ The Prompt Duel": "activity2",
        "3️⃣ The 90-Day Pilot Sprint": "activity3",
        "4️⃣ The AI Ethics Hot Seat": "activity4",
        "5️⃣ AI Innovation & Entrepreneurship": "activity6",
        "6️⃣ Project Mentoring & Implementation": "activity7",
        "📊 Live Dashboard": "dashboard",
    }

    # Preserve the currently selected page across reruns
    current = st.session_state.current_page
    if current not in PAGES:
        current = "🏠 Welcome"
        st.session_state.current_page = current

    choice = st.radio(
        "Navigate",
        list(PAGES.keys()),
        index=list(PAGES.keys()).index(current),
        label_visibility="collapsed",
    )
    st.session_state.current_page = choice

    st.divider()

    # -------- AI MODE SETTINGS --------
    with st.expander("⚙️ AI Mode Settings", expanded=False):
        st.session_state.use_llm = st.toggle(
            "Enable AI mode (Groq)",
            value=st.session_state.use_llm,
            help=(
                "Off = rule-based scoring only. "
                "On = live LLM feedback using Groq."
            ),
        )

        if st.session_state.use_llm:
            st.session_state.user_groq_key = st.text_input(
                "Groq API Key (optional)",
                type="password",
                value=st.session_state.user_groq_key,
                help=(
                    "Leave blank to use the facilitator's key. "
                    "Enter your own to use your own quota."
                ),
            )

            # Show current key source
            key_src = get_key_source()
            if key_src.startswith("none"):
                st.warning("No key available. AI mode will not work.")
            else:
                st.caption(f"🔑 Using: {key_src}")

    # -------- RESET OPTIONS --------
    with st.expander("🔄 Reset options", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset Activity 2", use_container_width=True):
                reset_activity_2()
                st.rerun()
            if st.button("Reset Activity 4", use_container_width=True):
                reset_activity_4()
                st.rerun()
        with col2:
            if st.button("Clear LLM cache", use_container_width=True):
                reset_llm_cache()
                st.rerun()
            if st.button(
                "Reset everything",
                use_container_width=True,
                type="primary",
            ):
                reset_all()
                st.rerun()

    # -------- DEBUG (remove before session day) --------
    if os.getenv("GENAI_DEBUG", "0") == "1":
        with st.expander("🐞 Debug", expanded=False):
            st.caption(f"Key source: **{get_key_source()}**")
            st.caption(f"LLM available: `{is_llm_available()}`")
            st.caption(f"Current page: `{st.session_state.current_page}`")

    st.divider()
    st.caption("Built with ❤️ for UGC-MMTTC")


# ---------------------------------------------------------------------------
# ROUTING
# ---------------------------------------------------------------------------
page_key = PAGES[st.session_state.current_page]

if page_key == "welcome":
    # ------------------------- WELCOME PAGE -------------------------
    st.markdown(
        """
        <div class="hero">
            <span class="badge-soft badge">Day 11 · 15 Oct 2026</span>
            <h1 class="main-header" style="margin-top:1rem;">
                Welcome to the GenAI Innovation
            </h1>
            <p class="sub-header">
                A hands-on journey from awareness to action — in 3 hours.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="activity-card">
                <div class="badge-soft badge">🎯 What you'll do</div>
                <ul style="margin-top:1rem; line-height:1.9; color:#1F2937;">
                    <li>Bust a GenAI hallucination</li>
                    <li>Duel with prompts</li>
                    <li>Design a 90-day pilot</li>
                    <li>Face an ethics dilemma</li>
                    <li>Pitch a GenAI venture</li>
                    <li>Plan your mentoring path</li>
                    <li>Watch the room's pulse</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="activity-card">
                <div class="badge-soft badge">⏱️ Time</div>
                <ul style="margin-top:1rem; line-height:1.9; color:#1F2937;">
                    <li>Activity 1 — 8 min</li>
                    <li>Activity 2 — 12 min</li>
                    <li>Activity 3 — 15 min</li>
                    <li>Activity 4 — 10 min</li>
                    <li>Activity 5 — 25 min</li>
                    <li>Activity 6 — 20 min</li>
                    <li>Dashboard — live</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="activity-card">
                <div class="badge-soft badge">🧭 How to start</div>
                <ol style="margin-top:1rem; line-height:1.9; color:#1F2937;">
                    <li>Enter your name (optional)</li>
                    <li>Click <b>Activity 1</b></li>
                    <li>Complete each activity in order</li>
                    <li>Download your plan at the end</li>
                    <li>Check the Dashboard anytime</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Confidence baseline
    st.markdown("### 📈 Before we begin…")
    st.session_state.confidence_before = st.slider(
        "How confident are you with Generative AI right now?",
        min_value=1,
        max_value=10,
        value=st.session_state.confidence_before,
        help="1 = never touched it, 10 = I build with it daily",
    )

    if st.button("🚀 Start Activity 1", use_container_width=True, type="primary"):
        st.session_state.current_page = "1️⃣ Two Truths & a Hallucination"
        st.rerun()


elif page_key == "activity1":
    activity1_truths.render()


elif page_key == "activity2":
    activity2_prompt_duel.render()


elif page_key == "activity3":
    activity3_pilot_sprint.render()


elif page_key == "activity4":
    activity4_ethics.render()


elif page_key == "activity6":
    activity6_innovation.render()


elif page_key == "activity7":
    activity7_mentoring.render()


elif page_key == "dashboard":
    activity5_dashboard.render()