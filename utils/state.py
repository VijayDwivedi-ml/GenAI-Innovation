"""Central session state initializer.

All session state keys used across the app are declared here exactly once.
This ensures:
1. No KeyError from missing keys anywhere in the app.
2. Reset functions can reliably clear state.
3. New developers can see the full state schema at a glance.
"""
import streamlit as st
import uuid
from datetime import datetime


def init_state():
    """Initialize all session state keys exactly once."""
    defaults = {
        # -------------------------------------------------------------------
        # Participant identity
        # -------------------------------------------------------------------
        "participant_id": str(uuid.uuid4())[:8],
        "participant_name": "",
        "joined_at": datetime.now().isoformat(),

        # -------------------------------------------------------------------
        # Navigation
        # -------------------------------------------------------------------
        "current_page": "🏠 Welcome",

        # -------------------------------------------------------------------
        # Activity 1: Two Truths & a Hallucination
        # -------------------------------------------------------------------
        "a1_quiz_started": False,
        "a1_start_time": None,
        "a1_current_index": 0,
        "a1_answers": [],
        "a1_finished": False,
        "a1_reveal": False,

        # -------------------------------------------------------------------
        # Activity 2: Prompt Duel
        # -------------------------------------------------------------------
        "a2_prompt": "",
        "a2_score": None,
        "a2_feedback": [],
        "a2_vague_output": None,       # result dict from run_vague_prompt()
        "a2_user_output": None,        # result dict from run_user_prompt()
        "a2_llm_error": None,          # last LLM error message (if any)
        "a2_compare_mode": False,      # whether to show side-by-side view

        # -------------------------------------------------------------------
        # Activity 3: Pilot Sprint
        # -------------------------------------------------------------------
        "a3_blueprint": {},
        "a3_submitted": False,

        # -------------------------------------------------------------------
        # Activity 4: AI Ethics Hot Seat
        # -------------------------------------------------------------------
        "a4_index": 0,
        "a4_choices": [],
        # Note: per-scenario choice keys are created dynamically
        # in activity4_ethics.py as `a4_choice_<scenario_id>`

        # -------------------------------------------------------------------
        # Activity 5: Live Pulse Dashboard
        # -------------------------------------------------------------------
        "confidence_before": 5,
        "confidence_after": 5,
        
        # -------------------------------------------------------------------
        # Activity 6 — Innovation & Entrepreneurship
        # -------------------------------------------------------------------
        "a6_venture": {},
        "a6_critique": None,

        # -------------------------------------------------------------------
        # Activity 6 — Priority Grid
        "a6_priority": None,
        # -------------------------------------------------------------------
        # Activity 7 — Empathy Map
        "a7_empathy": {},
        # -------------------------------------------------------------------    
        
        # -------------------------------------------------------------------
        # LLM mode & Groq client
        # -------------------------------------------------------------------
        "use_llm": False,              # toggle from sidebar
        "user_groq_key": "",           # participant's own key (optional)
        "_llm_cache": {},              # internal: prompt->response cache
        "_last_llm_call": 0.0,         # internal: timestamp for throttling
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# OPTIONAL HELPERS
# ---------------------------------------------------------------------------

def reset_activity_4():
    """Clear all Activity 4 state (index, choices, per-scenario choices)."""
    # Clear all a4_* keys
    for key in list(st.session_state.keys()):
        if key.startswith("a4_"):
            del st.session_state[key]
    # Re-initialize the base keys
    st.session_state.a4_index = 0
    st.session_state.a4_choices = []


def reset_activity_2():
    """Clear all Activity 2 state (prompt, scores, LLM outputs)."""
    st.session_state.a2_prompt = ""
    st.session_state.a2_score = None
    st.session_state.a2_feedback = []
    st.session_state.a2_vague_output = None
    st.session_state.a2_user_output = None
    st.session_state.a2_llm_error = None
    st.session_state.a2_compare_mode = False


def reset_llm_cache():
    """Clear the LLM response cache and throttle timer."""
    st.session_state._llm_cache = {}
    st.session_state._last_llm_call = 0.0


def reset_all():
    """Nuclear option: clear everything and re-init. Useful for testing."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()