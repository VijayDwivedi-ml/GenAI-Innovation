"""Activity 5: Live Pulse Dashboard.

Session-state-based metrics. No DB required.
Handles gracefully when activities haven't been attempted yet.
"""
import streamlit as st
import plotly.express as px
import pandas as pd


# ---------------------------------------------------------------------------
# SAFE GETTERS — return defaults if activities not yet attempted
# ---------------------------------------------------------------------------
def _get_a1_score() -> tuple[int, int]:
    """Return (correct, total) from Activity 1's answers list."""
    answers = st.session_state.get("a1_answers", []) or []
    if not answers:
        return 0, 0
    correct = sum(1 for a in answers if a.get("is_correct"))
    return correct, len(answers)


def _get_a2_score():
    """Return rule-based score or None."""
    return st.session_state.get("a2_score", None)


def _get_a3_status() -> str:
    """Return 'submitted' or 'not started'."""
    if st.session_state.get("a3_submitted") and st.session_state.get("a3_critique"):
        return "✓ submitted"
    return "—"


def _get_a4_count() -> int:
    """How many ethics scenarios the participant has answered."""
    return len(st.session_state.get("a4_choices", []) or [])


# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------
def render():
    st.markdown("## 📊 Live Pulse Dashboard")
    st.caption("See how the room is doing — in real time.")

    # ---------------- TOP METRICS ----------------
    a1_correct, a1_total = _get_a1_score()
    a2_score = _get_a2_score()
    a3_status = _get_a3_status()
    a4_count = _get_a4_count()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if a1_total > 0:
            st.metric(
                "Activity 1 score",
                f"{a1_correct}/{a1_total}",
                help="Hallucination quiz result",
            )
        else:
            st.metric("Activity 1 score", "—", help="Not attempted yet")

    with col2:
        if a2_score is not None:
            st.metric("Prompt score", f"{a2_score}/100")
        else:
            st.metric("Prompt score", "—", help="Not attempted yet")

    with col3:
        st.metric("Pilot plan", a3_status)

    with col4:
        st.metric("Ethics scenarios", f"{a4_count}/5")

    st.divider()

    # ---------------- CONFIDENCE SHIFT ----------------
    st.markdown("### 📈 Confidence Shift")
    before = st.session_state.get("confidence_before", 5)
    after = st.session_state.get("confidence_after", 5)

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Before today", f"{before}/10")
    with col_b:
        st.metric("After today", f"{after}/10")

    df = pd.DataFrame({
        "When": ["Before", "After"],
        "Confidence": [before, after],
    })
    fig = px.bar(
        df, x="When", y="Confidence",
        color="When",
        color_discrete_sequence=["#93C5FD", "#2563EB"],
        range_y=[0, 10],
    )
    fig.update_layout(
        showlegend=False,
        height=260,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111827"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # ---------------- PROGRESS MAP ----------------
    st.markdown("### 🗺️ Your Progress")
    progress_data = {
        "Activity": ["1 · Quiz", "2 · Prompt", "3 · Plan", "4 · Ethics"],
        "Status": [
            100 if a1_total > 0 else 0,
            100 if a2_score is not None else 0,
            100 if a3_status.startswith("✓") else 0,
            int(100 * a4_count / 5) if a4_count else 0,
        ],
    }
    prog_df = pd.DataFrame(progress_data)
    fig2 = px.bar(
        prog_df, x="Status", y="Activity", orientation="h",
        range_x=[0, 100],
        color_discrete_sequence=["#2563EB"],
        text="Status",
    )
    fig2.update_traces(texttemplate="%{text}%", textposition="outside")
    fig2.update_layout(
        showlegend=False,
        height=240,
        margin=dict(l=10, r=40, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111827"),
        xaxis=dict(showgrid=False, showticklabels=False),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # ---------------- CONFIDENCE UPDATE ----------------
    st.markdown("### 🎯 Update Your Confidence")
    st.session_state.confidence_after = st.slider(
        "How confident are you now?",
        1, 10, st.session_state.confidence_after,
    )

    st.caption(
        "You've completed this session. Review the other activities or "
        "download your Direction Plan from Activity 3."
    )