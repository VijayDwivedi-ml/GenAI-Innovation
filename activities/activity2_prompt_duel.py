"""Activity 2: The Prompt Duel.

Two modes:
1. Rule-based scoring (always available, no API needed)
2. Live LLM execution via Groq (if AI mode is enabled in sidebar)
"""
import streamlit as st
from utils.groq_client import (
    is_llm_available,
    run_vague_prompt,
    run_user_prompt,
)


# ---------------------------------------------------------------------------
# RULE-BASED SCORER
# ---------------------------------------------------------------------------
def score_prompt(prompt: str) -> tuple[int, list[str]]:
    """Keyword-based prompt scorer — works without any API."""
    score = 0
    feedback = []
    p = prompt.lower()

    if any(k in p for k in ["act as", "you are", "as a"]):
        score += 25
        feedback.append("✅ Role defined")
    else:
        feedback.append("❌ Add a role (e.g., 'Act as a…')")

    if any(k in p for k in ["student", "teacher", "beginner", "expert", "audience"]):
        score += 25
        feedback.append("✅ Audience specified")
    else:
        feedback.append("❌ Specify the audience")

    if any(k in p for k in ["bullet", "list", "paragraph", "words", "sentences"]):
        score += 25
        feedback.append("✅ Format specified")
    else:
        feedback.append("❌ Specify output format")

    if any(k in p for k in ["avoid", "must", "should", "include", "don't"]):
        score += 25
        feedback.append("✅ Constraints given")
    else:
        feedback.append("❌ Add constraints")

    return score, feedback


# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------
def render():
    st.markdown("## ⚔️ Activity 2: The Prompt Duel")
    st.caption("Rewrite a vague prompt into a champion prompt — then watch them run.")

    # Vague baseline
    st.info("**Vague prompt:** _'Write about AI in education.'_")

    # Input
    prompt = st.text_area(
        "Your improved prompt:",
        value=st.session_state.a2_prompt,
        height=150,
        placeholder="Act as a…",
    )
    st.session_state.a2_prompt = prompt

    # ---------------- ACTION BUTTONS ----------------
    col1, col2 = st.columns([1, 1])

    with col1:
        score_clicked = st.button(
            "🏆 Score my prompt",
            use_container_width=True,
            help="Rule-based score — works instantly, no API needed.",
        )

    with col2:
        llm_ready = is_llm_available()
        run_clicked = st.button(
            "⚡ Run it live (Groq)",
            use_container_width=True,
            disabled=not llm_ready or not prompt.strip(),
            help=(
                "Executes both the vague prompt and your prompt, side by side."
                if llm_ready else
                "Enable AI mode in the sidebar to use this."
            ),
        )

    # ---------------- RULE-BASED SCORING ----------------
    if score_clicked:
        if not prompt.strip():
            st.warning("Write something first!")
        else:
            score, feedback = score_prompt(prompt)
            st.session_state.a2_score = score
            st.session_state.a2_feedback = feedback
            st.rerun()

    # ---------------- LLM EXECUTION ----------------
    if run_clicked:
        if not prompt.strip():
            st.warning("Write something first!")
        else:
            with st.spinner("Running both prompts on Groq…"):
                vague_result = run_vague_prompt()
                user_result = run_user_prompt(prompt)

            st.session_state.a2_vague_output = vague_result
            st.session_state.a2_user_output = user_result
            st.session_state.a2_compare_mode = True
            st.rerun()

    # ---------------- SCORE DISPLAY ----------------
    if st.session_state.a2_score is not None:
        st.divider()
        st.metric("Your prompt score", f"{st.session_state.a2_score}/100")
        for fb in st.session_state.a2_feedback:
            st.write(fb)

    # ---------------- SIDE-BY-SIDE OUTPUT ----------------
    if st.session_state.a2_compare_mode:
        _render_side_by_side()

    # ---------------- NAVIGATION ----------------
    st.divider()
    if st.button("➡️ Next: Pilot Sprint", use_container_width=True):
        st.session_state.current_page = "3️⃣ The 90-Day Pilot Sprint"
        st.rerun()


# ---------------------------------------------------------------------------
# SIDE-BY-SIDE COMPARISON
# ---------------------------------------------------------------------------
def _render_side_by_side():
    st.divider()
    st.markdown("### 🔍 Vague vs. Champion — Live Output")

    vague = st.session_state.a2_vague_output or {}
    user = st.session_state.a2_user_output or {}

    col1, col2 = st.columns(2)

    # ---- VAGUE PROMPT OUTPUT ----
    with col1:
        st.markdown("#### 😴 Vague prompt")
        st.caption("_Write about AI in education._")
        if not vague.get("success"):
            st.error(f"❌ {vague.get('error', 'Unknown error')}")
        else:
            st.markdown(
                f"""
                <div style="
                    background:#1E2130;
                    border-left:3px solid #6B7280;
                    padding:1rem;
                    border-radius:8px;
                    font-size:0.92rem;
                    color:#D1D5DB;
                    white-space:pre-wrap;
                ">{vague['text']}</div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(
                f"⏱️ {vague.get('elapsed_ms', 0)} ms · "
                f"{'📦 cached' if vague.get('cached') else '🌐 live'} · "
                f"`{vague.get('model', '')}`"
            )

    # ---- USER PROMPT OUTPUT ----
    with col2:
        st.markdown("#### 🔥 Your champion prompt")
        st.caption(f"_{st.session_state.a2_prompt[:80]}…_")
        if not user.get("success"):
            st.error(f"❌ {user.get('error', 'Unknown error')}")
        else:
            st.markdown(
                f"""
                <div style="
                    background:#1E2130;
                    border-left:3px solid #8B5CF6;
                    padding:1rem;
                    border-radius:8px;
                    font-size:0.92rem;
                    color:#FAFAFA;
                    white-space:pre-wrap;
                ">{user['text']}</div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(
                f"⏱️ {user.get('elapsed_ms', 0)} ms · "
                f"{'📦 cached' if user.get('cached') else '🌐 live'} · "
                f"`{user.get('model', '')}`"
            )

    # ---- TAKEAWAY ----
    st.info(
        "💡 **Notice the difference?** Same model, same topic — but the champion "
        "prompt produces a focused, structured, audience-aware answer. That's the "
        "power of prompt engineering."
    )

    # Reset button
    if st.button("🔄 Try another prompt", use_container_width=True):
        st.session_state.a2_compare_mode = False
        st.session_state.a2_vague_output = None
        st.session_state.a2_user_output = None
        st.rerun()