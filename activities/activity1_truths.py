"""Activity 1: Two Truths and a Hallucination — Rapid-Fire Quiz.

5 questions, 60-second timer, sequential reveal, summary at the end.
No DB. No LLM. Pure session state.
"""
import time
from datetime import datetime

import streamlit as st


# ===========================================================================
# QUESTION BANK
# ===========================================================================
QUESTIONS = [
    {
        "id": "q1_hinton",
        "question": "Who won the 2024 Nobel Prize in Physics for work on neural networks?",
        "options": [
            "Geoffrey Hinton",
            "Yann LeCun",
            "Fei-Fei Li",
            "Demis Hassabis",
        ],
        "correct": "Geoffrey Hinton",
        "fact": (
            "Hinton shared the 2024 Nobel Prize in **Physics** — not Computer "
            "Science. He's often called the 'godfather of AI'. John Hopfield "
            "co-won with him for foundational work on neural networks."
        ),
    },
    {
        "id": "q2_gpt",
        "question": "What does 'GPT' actually stand for?",
        "options": [
            "General Purpose Transformer",
            "Generative Pre-trained Transformer",
            "Guided Pattern Text",
            "Graphical Processing Toolkit",
        ],
        "correct": "Generative Pre-trained Transformer",
        "fact": (
            "'Generative Pre-trained Transformer.' The 'General Purpose' "
            "version is the most common wrong guess — a neat reminder that "
            "well-known acronyms are often misremembered."
        ),
    },
    {
        "id": "q3_911",
        "question": "Which did ChatGPT famously get WRONG in early 2023?",
        "options": [
            "Writing a sonnet",
            "Solving a math word problem",
            "Answering 'Is 9.11 bigger than 9.9?'",
            "Translating French",
        ],
        "correct": "Answering 'Is 9.11 bigger than 9.9?'",
        "fact": (
            "The model said **9.11 > 9.9** because 11 > 9 — a textbook "
            "hallucination on numeric reasoning. Perfect example of why you "
            "never trust an LLM on math without verification."
        ),
    },
    {
        "id": "q4_water",
        "question": (
            "Roughly how much water does a 20–50 query ChatGPT conversation "
            "consume, per research estimates?"
        ),
        "options": [
            "A few drops",
            "A cup (250 ml)",
            "Around half a liter (500 ml)",
            "A bathtub (150 L)",
        ],
        "correct": "Around half a liter (500 ml)",
        "fact": (
            "UC Riverside (2023) estimates ~500 ml per 20–50 queries for "
            "data-center cooling. AI's environmental footprint is real, "
            "under-discussed, and central to the 'responsible innovation' theme."
        ),
    },
    {
        "id": "q5_gemini",
        "question": (
            "In early 2024, which company paused its AI image generator after "
            "it produced historically inaccurate images?"
        ),
        "options": [
            "OpenAI",
            "Anthropic",
            "Google",
            "Meta",
        ],
        "correct": "Google",
        "fact": (
            "Google paused Gemini's image generation in Feb 2024 after it "
            "generated historically inaccurate but 'diverse' depictions. A "
            "real case study in how bias mitigation can go sideways."
        ),
    },
]


# ===========================================================================
# STATE HELPERS
# ===========================================================================
def _reset_quiz():
    """Reset all quiz-related state to start fresh."""
    st.session_state.a1_quiz_started = False
    st.session_state.a1_start_time = None
    st.session_state.a1_current_index = 0
    st.session_state.a1_answers = []
    st.session_state.a1_finished = False
    st.session_state.a1_reveal = False  # whether current Q is revealed


def _init_quiz_state():
    """Ensure all keys exist. Safe to call on every render."""
    defaults = {
        "a1_quiz_started": False,
        "a1_start_time": None,
        "a1_current_index": 0,
        "a1_answers": [],
        "a1_finished": False,
        "a1_reveal": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ===========================================================================
# RENDER — MAIN
# ===========================================================================
def render():
    _init_quiz_state()

    st.markdown("## ❄️ Activity 1: Two Truths and a Hallucination")
    st.caption(
        "Five quick questions. Sixty seconds. How many can you nail?"
    )

    # Route to the correct screen
    if not st.session_state.a1_quiz_started:
        _render_intro()
    elif st.session_state.a1_finished:
        _render_summary()
    else:
        _render_quiz()


# ===========================================================================
# SCREEN 1 — INTRO
# ===========================================================================
def _render_intro():
    st.markdown(
        """
        <div class="activity-card">
            <span class="badge-soft badge">❄️ 5 Questions · 60 Seconds</span>
            <h3 style="margin-top:1rem;">Ready when you are.</h3>
            <p style="color:#94A3B8;">
                You'll see 5 rapid-fire questions about Generative AI.
                Each has 4 options. Pick fast — the timer doesn't pause.
                At the end you'll see your score, time taken, and one
                surprising fact per question.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("▶️  Start the quiz", use_container_width=True, type="primary"):
        _reset_quiz()
        st.session_state.a1_quiz_started = True
        st.session_state.a1_start_time = time.time()
        st.rerun()


# ===========================================================================
# SCREEN 2 — QUIZ
# ===========================================================================
def _render_quiz():
    total = len(QUESTIONS)
    idx = st.session_state.a1_current_index
    elapsed = time.time() - st.session_state.a1_start_time
    remaining = max(0, 60 - int(elapsed))

    # ---------- TIMER + PROGRESS BAR ----------
    col1, col2 = st.columns([2, 1])
    with col1:
        st.progress(
            (idx) / total,
            text=f"Question {min(idx + 1, total)} of {total}",
        )
    with col2:
        if remaining > 10:
            st.markdown(f"### ⏱️ {remaining}s")
        elif remaining > 0:
            st.markdown(f"### 🔴 {remaining}s")
        else:
            st.markdown("### ⏰ Time!")

    # ---------- AUTO-FINISH ON TIMEOUT ----------
    if remaining <= 0:
        _finish_quiz()
        st.rerun()
        return

    # ---------- QUESTION ----------
    question = QUESTIONS[idx]
    st.markdown(f"### {question['question']}")

    if not st.session_state.a1_reveal:
        # ---------- ANSWER BUTTONS ----------
        for i, opt in enumerate(question["options"]):
            if st.button(
                opt,
                key=f"a1_opt_{idx}_{i}",
                use_container_width=True,
            ):
                st.session_state.a1_answers.append({
                    "question_id": question["id"],
                    "question": question["question"],
                    "chosen": opt,
                    "correct": question["correct"],
                    "is_correct": opt == question["correct"],
                    "fact": question["fact"],
                    "answered_at": datetime.now().isoformat(),
                })
                st.session_state.a1_reveal = True
                st.rerun()
    else:
        # ---------- REVEAL ----------
        last = st.session_state.a1_answers[-1]
        if last["is_correct"]:
            st.success(f"🎉 Correct! **{last['correct']}**")
        else:
            st.error(
                f"❌ Not quite. You chose **{last['chosen']}**. "
                f"The correct answer is **{last['correct']}**."
            )
        st.info(f"💡 {last['fact']}")

        # Advance or finish
        col1, col2 = st.columns([3, 1])
        with col2:
            next_label = (
                "🏁 See results"
                if idx + 1 >= total
                else "➡️  Next question"
            )
            if st.button(next_label, use_container_width=True, type="primary"):
                st.session_state.a1_current_index += 1
                st.session_state.a1_reveal = False
                if st.session_state.a1_current_index >= total:
                    _finish_quiz()
                st.rerun()


# ===========================================================================
# FINISH LOGIC
# ===========================================================================
def _finish_quiz():
    """Mark the quiz finished. Missing answers = wrong."""
    answered_ids = {a["question_id"] for a in st.session_state.a1_answers}
    for q in QUESTIONS:
        if q["id"] not in answered_ids:
            st.session_state.a1_answers.append({
                "question_id": q["id"],
                "question": q["question"],
                "chosen": "— (no answer)",
                "correct": q["correct"],
                "is_correct": False,
                "fact": q["fact"],
                "answered_at": datetime.now().isoformat(),
            })
    st.session_state.a1_finished = True


# ===========================================================================
# SCREEN 3 — SUMMARY
# ===========================================================================
def _render_summary():
    answers = st.session_state.a1_answers
    total = len(QUESTIONS)
    score = sum(1 for a in answers if a["is_correct"])

    elapsed = time.time() - (st.session_state.a1_start_time or time.time())
    elapsed = min(elapsed, 60)  # cap at 60s even if user stalled

    # ---------- SCORE CARD ----------
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Your score", f"{score}/{total}")
    with col2:
        pct = round(100 * score / total)
        st.metric("Accuracy", f"{pct}%")
    with col3:
        st.metric("Time taken", f"{int(elapsed)}s")

    # ---------- GRADE MESSAGE ----------
    if score == total:
        st.success("🏆 Perfect score. You know your GenAI trivia.")
    elif score >= total - 1:
        st.success("🎉 Excellent — one slip, easily forgiven.")
    elif score >= total // 2:
        st.info("👍 Solid. You're ahead of the average.")
    else:
        st.warning("📚 Worth a reread — the facts below will help.")

    st.divider()

    # ---------- PER-QUESTION REVIEW ----------
    st.markdown("### 🔍 Question-by-question review")
    for i, a in enumerate(answers, 1):
        icon = "✅" if a["is_correct"] else "❌"
        with st.expander(f"{icon} Q{i}. {a['question']}"):
            st.markdown(f"**Your answer:** {a['chosen']}")
            st.markdown(f"**Correct answer:** {a['correct']}")
            st.info(f"💡 {a['fact']}")

    # ---------- SESSION ID ----------
    st.divider()
    st.caption(
        f"Session ID: `{st.session_state.participant_id}` · "
        f"Completed at {datetime.now().strftime('%H:%M:%S')}"
    )

    # ---------- NEXT / RETRY ----------
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔁 Retry the quiz", use_container_width=True):
            _reset_quiz()
            st.rerun()
    with col2:
        if st.button("➡️  Next: Prompt Duel", use_container_width=True, type="primary"):
            st.session_state.current_page = "2️⃣ The Prompt Duel"
            st.rerun()