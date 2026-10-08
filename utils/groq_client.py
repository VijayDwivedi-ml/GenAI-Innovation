"""Groq LLM wrapper with caching, throttling, and graceful fallback.

Key resolution priority:
    1. Sidebar input (participant's own key)
    2. Streamlit secrets (cloud deployment)
    3. Environment variable / .env (local development)

Design goals:
    1. Never crash the app if the API fails.
    2. Cache identical requests to save rate limit.
    3. Throttle rapid calls to stay under the free-tier RPM.
    4. Support both facilitator key and participant key.
"""
import os
import time
import hashlib
import json
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load .env into os.environ at import time (local dev convenience)
load_dotenv()


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "openai/gpt-oss-20b"       # fast, free-tier friendly
FALLBACK_MODEL = "openai/gpt-oss-120b"     # smarter, slower
MIN_SECONDS_BETWEEN_CALLS = 2.0            # throttle: ~30 RPM
MAX_CACHE_SIZE = 200


# ---------------------------------------------------------------------------
# KEY RESOLUTION
# ---------------------------------------------------------------------------
def _resolve_api_key() -> str | None:
    """Get an API key from the first available source.

    Priority:
        1. Sidebar input (st.session_state.user_groq_key)
        2. st.secrets["GROQ_API_KEY"]
        3. os.environ["GROQ_API_KEY"] (from .env)
    """
    # 1. Participant's own key from sidebar
    user_key = st.session_state.get("user_groq_key", "").strip()
    if user_key and user_key.startswith("gsk_"):
        return user_key

    # 2. Streamlit secrets (cloud deployment)
    try:
        secret_key = st.secrets.get("GROQ_API_KEY", None)
        if secret_key and str(secret_key).startswith("gsk_"):
            return str(secret_key)
    except (KeyError, FileNotFoundError, AttributeError):
        pass

    # 3. Environment variable / .env (local dev)
    env_key = os.getenv("GROQ_API_KEY")
    if env_key and env_key.startswith("gsk_"):
        return env_key

    return None


def get_key_source() -> str:
    """Return a human-readable label of where the key is coming from.

    Useful for the sidebar debug caption during testing.
    """
    user_key = st.session_state.get("user_groq_key", "").strip()
    if user_key and user_key.startswith("gsk_"):
        return "sidebar (participant)"

    try:
        if st.secrets.get("GROQ_API_KEY", None):
            return "st.secrets (cloud)"
    except (KeyError, FileNotFoundError, AttributeError):
        pass

    if os.getenv("GROQ_API_KEY"):
        return ".env (local)"

    return "none — no key found"


def is_llm_available() -> bool:
    """Check whether AI mode can be used at all."""
    if not st.session_state.get("use_llm", False):
        return False
    return _resolve_api_key() is not None


# ---------------------------------------------------------------------------
# THROTTLE
# ---------------------------------------------------------------------------
def _throttle():
    """Sleep if the last call was too recent."""
    last_call = st.session_state.get("_last_llm_call", 0.0)
    elapsed = time.time() - last_call
    if elapsed < MIN_SECONDS_BETWEEN_CALLS:
        time.sleep(MIN_SECONDS_BETWEEN_CALLS - elapsed)
    st.session_state["_last_llm_call"] = time.time()


# ---------------------------------------------------------------------------
# CACHE
# ---------------------------------------------------------------------------
def _cache_key(prompt: str, model: str, temperature: float, system_prompt: str) -> str:
    raw = f"{model}|{temperature}|{system_prompt}|{prompt}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _get_cached(prompt: str, model: str, temperature: float, system_prompt: str) -> str | None:
    cache = st.session_state.get("_llm_cache", {})
    return cache.get(_cache_key(prompt, model, temperature, system_prompt))


def _set_cached(prompt: str, model: str, temperature: float, system_prompt: str, response: str):
    cache = st.session_state.get("_llm_cache", {})
    if len(cache) >= MAX_CACHE_SIZE:
        # FIFO eviction
        cache.pop(next(iter(cache)))
    cache[_cache_key(prompt, model, temperature, system_prompt)] = response
    st.session_state["_llm_cache"] = cache


# ---------------------------------------------------------------------------
# MAIN CALL
# ---------------------------------------------------------------------------
def call_groq(
    prompt: str,
    system_prompt: str = "You are a helpful, concise assistant.",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 500,
) -> dict:
    """Call Groq with caching, throttling, and fallback.

    Returns a dict:
    {
        "success": bool,
        "text": str,
        "error": str | None,
        "cached": bool,
        "model": str,
        "elapsed_ms": int,
        "key_source": str,
    }
    """
    # 1. Availability check
    if not is_llm_available():
        return {
            "success": False,
            "text": "",
            "error": "LLM mode is off or no API key available.",
            "cached": False,
            "model": model,
            "elapsed_ms": 0,
            "key_source": get_key_source(),
        }

    # 2. Cache check
    cached = _get_cached(prompt, model, temperature, system_prompt)
    if cached is not None:
        return {
            "success": True,
            "text": cached,
            "error": None,
            "cached": True,
            "model": model,
            "elapsed_ms": 0,
            "key_source": get_key_source(),
        }

    # 3. Throttle
    _throttle()

    # 4. API call
    api_key = _resolve_api_key()
    start = time.time()
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = completion.choices[0].message.content or ""
        elapsed = int((time.time() - start) * 1000)

        _set_cached(prompt, model, temperature, system_prompt, text)
        return {
            "success": True,
            "text": text,
            "error": None,
            "cached": False,
            "model": model,
            "elapsed_ms": elapsed,
            "key_source": get_key_source(),
        }

    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        # If the default model fails, try the fallback once
        if model == DEFAULT_MODEL:
            try:
                client = Groq(api_key=api_key)
                completion = client.chat.completions.create(
                    model=FALLBACK_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                text = completion.choices[0].message.content or ""
                elapsed = int((time.time() - start) * 1000)
                _set_cached(prompt, FALLBACK_MODEL, temperature, system_prompt, text)
                return {
                    "success": True,
                    "text": text,
                    "error": None,
                    "cached": False,
                    "model": FALLBACK_MODEL,
                    "elapsed_ms": elapsed,
                    "key_source": get_key_source(),
                }
            except Exception:
                pass  # fall through to error return

        return {
            "success": False,
            "text": "",
            "error": f"{type(e).__name__}: {str(e)[:200]}",
            "cached": False,
            "model": model,
            "elapsed_ms": elapsed,
            "key_source": get_key_source(),
        }


# ---------------------------------------------------------------------------
# CONVENIENCE HELPERS (used by Activity 2)
# ---------------------------------------------------------------------------
def run_vague_prompt() -> dict:
    """Run the deliberately vague prompt for side-by-side comparison."""
    return call_groq(
        prompt="Write about AI in education.",
        system_prompt="You are a helpful assistant. Be brief.",
        temperature=0.7,
        max_tokens=200,
    )


def run_user_prompt(user_prompt: str) -> dict:
    """Run the participant's improved prompt."""
    return call_groq(
        prompt=user_prompt,
        system_prompt=(
            "You are a helpful, professional assistant. "
            "Follow the user's instructions precisely."
        ),
        temperature=0.7,
        max_tokens=400,
    )


# ---------------------------------------------------------------------------
# ACTIVITY 3 — PLAN CRITIQUE
# ---------------------------------------------------------------------------
CRITIQUE_SYSTEM_PROMPT = """You are a senior data scientist who has reviewed \
hundreds of 90-day student research projects. The user has just seen a real \
case study: the NCRB Suicide Data Dashboard (India, 2018-2022) — built with \
Python, Streamlit, Plotly, and honest data documentation.

Your job is to critique the user's plan against the same 4-stage template \
the case study used:
  1. Question & Scope
  2. Data & Honesty
  3. Build & Show
  4. Limits & Delivery

Rules:
- Be specific and direct. Never praise vaguely.
- Name what would kill this project by week 3.
- Reference the NCRB template where relevant.
- Vague plans must get "Needs Work" or "Fragile". Do not inflate grades.
- Strong plans should be called out for what makes them strong.

Return ONLY valid JSON, no markdown fences, in this exact shape:
{
  "grade": "Strong" | "Promising" | "Needs Work" | "Fragile",
  "strengths": ["one sentence", "one sentence"],
  "gaps": ["one sentence", "one sentence"],
  "kill_risk": "one short paragraph",
  "next_step": "one concrete action",
  "ncrb_comparison": "one or two sentences comparing to the NCRB template"
}"""


def critique_plan(plan: dict) -> dict:
    """Send a 4-stage plan to Groq and return a structured critique.

    Falls back to a conservative placeholder on any failure — the caller
    should ideally check is_llm_available() first.
    """
    user_prompt = f"""Critique this 90-day project plan.

STAGE 1 — Question & Scope
  Question:        {plan.get('stage1_question', '—')}
  Out of scope:    {plan.get('stage1_scope', '—')}

STAGE 2 — Data & Honesty
  Data source:     {plan.get('stage2_data', '—')}
  What's missing:  {plan.get('stage2_missing', '—')}

STAGE 3 — Build & Show
  What I'll build: {plan.get('stage3_build', '—')}
  The ONE thing:   {plan.get('stage3_one_thing', '—')}
  GenAI's role:    {plan.get('stage3_genai_role', '—')}

STAGE 4 — Limits & Delivery
  Not claiming:    {plan.get('stage4_not_claiming', '—')}
  Access:          {plan.get('stage4_access', '—')}
  Top risk:        {plan.get('stage4_risk', '—')}
"""

    result = call_groq(
        prompt=user_prompt,
        system_prompt=CRITIQUE_SYSTEM_PROMPT,
        model="openai/gpt-oss-120b",   # deeper reasoning than 20b
        temperature=0.3,               # low temp for consistent grading
        max_tokens=700,
    )

    if not result.get("success"):
        # Graceful fallback — never break the activity
        return {
            "grade": "Needs Work",
            "strengths": ["Plan was submitted with all 4 stages."],
            "gaps": [f"AI critique unavailable: {result.get('error', 'unknown error')}"],
            "kill_risk": "Could not evaluate — AI mode failed. Review manually.",
            "next_step": "Retry, or check your Groq key and rate limits.",
            "ncrb_comparison": "No comparison available.",
        }

    # Strip any accidental markdown fences
    text = result["text"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last-resort fallback
        return {
            "grade": "Promising",
            "strengths": ["Plan was submitted."],
            "gaps": ["AI returned malformed output — could not parse critique."],
            "kill_risk": "Unknown — critique parsing failed.",
            "next_step": "Rerun the Reality Check.",
            "ncrb_comparison": "Not available.",
        }

# ---------------------------------------------------------------------------
# ACTIVITY 6 — VENTURE CRITIQUE
# ---------------------------------------------------------------------------
VENTURE_SYSTEM_PROMPT = """You are a seasoned venture partner who has reviewed \
hundreds of GenAI startup pitches. The user has just seen the Sarvam AI case \
study — an Indian startup that built sovereign AI for Indian languages, \
raised $234M, and hit unicorn status in 3 years.

Your job is to critique the user's venture pitch on four axes:
  1. Problem & Customer      — Is the pain real? Is the customer specific?
  2. Unfair Advantage        — Do they have data, access, or depth others lack?
  3. Product & Wedge         — Is there a narrow, winnable entry point?
  4. Business Model & Moat   — Who pays? Why can't OpenAI/Google copy it?

Rules:
- Be specific and direct. Never praise vaguely.
- Name what kills this by week 3. That's the core question.
- Reference Sarvam's playbook where relevant (specific lane, own data, open source).
- Vague pitches must get "Needs Work" or "Fragile". Do not inflate grades.

Return ONLY valid JSON, no markdown fences, in this exact shape:
{
  "grade": "Strong" | "Promising" | "Needs Work" | "Fragile",
  "strengths": ["one sentence", "one sentence"],
  "gaps": ["one sentence", "one sentence"],
  "kill_risk": "one short paragraph",
  "next_step": "one concrete action",
  "sarvam_comparison": "one or two sentences comparing to Sarvam's playbook"
}"""


def critique_venture(plan: dict) -> dict:
    """Send a venture pitch to Groq and return a structured critique."""
    user_prompt = f"""Critique this GenAI venture pitch.

STAGE 1 — Problem & Customer
  Problem:            {plan.get('s1_problem', '—')}
  First customer:     {plan.get('s1_customer', '—')}

STAGE 2 — Unfair Advantage
  What only I have:   {plan.get('s2_advantage', '—')}
  Data/assets I own:  {plan.get('s2_assets', '—')}

STAGE 3 — Product & Wedge
  MVP:                {plan.get('s3_mvp', '—')}
  Wedge:              {plan.get('s3_wedge', '—')}
  GenAI's role:       {plan.get('s3_genai_role', '—')}

STAGE 4 — Business Model & Moat
  Revenue model:      {plan.get('s4_revenue', '—')}
  Moat:               {plan.get('s4_moat', '—')}
  Biggest kill risk:  {plan.get('s4_risk', '—')}
"""

    result = call_groq(
        prompt=user_prompt,
        system_prompt=VENTURE_SYSTEM_PROMPT,
        model="openai/gpt-oss-120b",
        temperature=0.3,
        max_tokens=700,
    )

    if not result.get("success"):
        return {
            "grade": "Needs Work",
            "strengths": ["Pitch was submitted with all 4 stages."],
            "gaps": [f"AI critique unavailable: {result.get('error', 'unknown error')}"],
            "kill_risk": "Could not evaluate — check Groq key or rate limits.",
            "next_step": "Retry, or toggle AI mode off for a rule-based review.",
            "sarvam_comparison": "No comparison available.",
        }

    text = result["text"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "grade": "Promising",
            "strengths": ["Pitch was submitted."],
            "gaps": ["AI returned malformed output — critique parsing failed."],
            "kill_risk": "Unknown — parsing failed.",
            "next_step": "Rerun the Reality Check.",
            "sarvam_comparison": "Not available.",
        }