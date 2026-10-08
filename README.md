# 🚀 GenAI Innovation Studio

An interactive, Streamlit-based workshop app built for the **UGC-MMTTC Refresher Course on "Applied Generative AI: Innovation with Responsibility"** (Day 11 — 15 Oct 2026).

Instead of slides, participants get a **hands-on journey** through seven activities that teach GenAI concepts through play, reflection, venture thinking, and real project design.

---

## ✨ What's Inside

| # | Activity | Time | What It Teaches |
|---|----------|------|-----------------|
| 1 | **Two Truths & a Hallucination** | 8 min | A rapid-fire quiz (5 questions, 60s timer) that makes hallucination, terminology, and AI ethics tangible |
| 2 | **The Prompt Duel** | 12 min | Rewrite a vague prompt, score it, and *run it live* on Groq to see side-by-side output differences |
| 3 | **The 90-Day Pilot Sprint** | 15 min | Study a real completed project (the NCRB Suicide Data Dashboard), then plan your own — with an AI-generated Reality Check |
| 4 | **The AI Ethics Hot Seat** | 10 min | Five real-world dilemmas. Every choice has a consequence. Industry consensus revealed after each decision |
| 5 | **AI Innovation & Entrepreneurship** | 25 min | Learn from Sarvam AI (India's sovereign AI unicorn). Pitch your own GenAI venture. Get a Founder Reality Check |
| 6 | **Project Mentoring & Implementation** | 20 min | Auto-fills from Activity 3. Adds a 90-day checklist, an Empathy Map, and a downloadable Mentor Brief |
| 7 | **Live Pulse Dashboard** | live | Tracks your score, confidence shift, and progress across all activities |

**Total session runtime:** ~90 minutes (or ~45 minutes if you run Activities 1–4 only).

---

## 🎯 Design Principles

1. **Hands-on over handouts.** Every activity requires the participant to *do* something.
2. **Insight over information.** Each activity ends with a lesson, not a summary.
3. **Light theme, low cognitive load.** Clean, readable, projector-friendly.
4. **Graceful degradation.** Every AI-powered feature falls back to rule-based logic if the LLM is unavailable.
5. **No database required.** Everything runs on `st.session_state` — no setup, no migrations, no infra.
6. **Real Indian context.** Sarvam AI, NCRB data, and IndiaAI Mission anchor the case studies.

---

## 🧭 The Learning Arc

The seven activities form a deliberate journey:

```
Awareness  →  Skill  →  Design  →  Ethics  →  Venture  →  Execution
   (1)         (2)       (3)         (4)         (5)          (6)
```

- **Activity 1** makes hallucination tangible.
- **Activity 2** teaches that prompt quality determines output quality.
- **Activity 3** shows what a real project looks like — and forces you to plan one.
- **Activity 4** confronts the ethical cost of every GenAI decision.
- **Activity 5** flips the mindset from *builder* to *founder*.
- **Activity 6** turns the plan into action: mentors, checklist, empathy.
- **The Dashboard** measures the room's collective confidence shift.

---

## 🚦 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-username/genai-innovation-studio.git
cd genai-innovation-studio
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Add your Groq API key

For the **live AI mode** in Activities 2, 3, and 5, get a free key from [console.groq.com/keys](https://console.groq.com/keys) and add it to a `.env` file:

```bash
# .env (project root)
GROQ_API_KEY=gsk_your_key_here
```

> ⚠️ **Never commit `.env` to Git.** It's already in `.gitignore`. If you skip this step, the app runs in **rule-based mode** — fully functional, just without live LLM calls.

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
genai-innovation-studio/
├── app.py                              # Entry point — sidebar, routing, CSS loader
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
├── .env                                # Your Groq key (gitignored)
├── .gitignore
│
├── assets/
│   └── styles.css                      # Light-theme custom stylesheet
│
├── .streamlit/
│   ├── config.toml                     # Theme palette
│   └── secrets.toml                    # (Optional) Groq key for cloud deploy
│
├── utils/
│   ├── __init__.py
│   ├── state.py                        # Central session_state initializer
│   └── groq_client.py                  # Groq wrapper (caching, throttling, fallbacks)
│
└── activities/
    ├── __init__.py
    ├── activity1_truths.py             # Quiz
    ├── activity2_prompt_duel.py        # Prompt scoring + LLM execution
    ├── activity3_pilot_sprint.py       # Case study → Plan → Reality Check
    ├── activity4_ethics.py             # Ethics decision game
    ├── activity5_dashboard.py          # Live progress dashboard
    ├── activity6_innovation.py         # Sarvam AI → Venture pitch → Founder check
    └── activity7_mentoring.py          # 90-day checklist + Empathy Map + Mentor Brief
```

---

## 🔑 API Keys — Three Ways to Load Them

The Groq client looks for a key in this priority order:

| Priority | Source | Use Case |
|----------|--------|----------|
| 1 | **Sidebar input** (participant's own key) | Public deployments, workshops with power users |
| 2 | **`st.secrets`** | Streamlit Cloud deployments |
| 3 | **`.env` file** | Local development |

**If no key is found:** the app automatically switches to rule-based mode. Nothing crashes.

### How to Configure Each Source

**Sidebar input** — participant types it during the session. No setup needed.

**Streamlit secrets** — for cloud deploys:
```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "gsk_your_key_here"
```

**`.env`** — for local dev:
```bash
GROQ_API_KEY=gsk_your_key_here
```

---

## 🎨 Customizing the Theme

The light theme is anchored to a specific palette in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2563EB"              # Buttons, accents
backgroundColor = "#FFFFFF"           # Main background
secondaryBackgroundColor = "#EFF6FF"  # Cards, sidebar
textColor = "#111827"                 # Body text
font = "sans serif"
```

To rebrand:
1. Change the hex values in `config.toml`
2. Update the matching hex values in `assets/styles.css`
3. Restart Streamlit

**Green/teal alternative:** replace `#2563EB` with `#059669` and `#EFF6FF` with `#ECFDF5`.

---

## 🧠 How Each Activity Works

### Activity 1 — Two Truths & a Hallucination
5 questions, 60-second timer, sequential reveal, per-question review.

**Customize:** Edit the `QUESTIONS` list in `activities/activity1_truths.py`.

### Activity 2 — The Prompt Duel
Rule-based scoring (keyword matching) + optional live LLM execution.

**Customize:** Edit `score_prompt()` in `activities/activity2_prompt_duel.py`.

### Activity 3 — The 90-Day Pilot Sprint
Shows a real case study (NCRB Suicide Data Dashboard), then a 4-stage plan form, then a Groq-generated Reality Check.

**Customize:**
- Case study content: edit `CASE_STUDY` in `activities/activity3_pilot_sprint.py`
- Reality Check prompt: edit `CRITIQUE_SYSTEM_PROMPT` in `utils/groq_client.py`

### Activity 4 — The AI Ethics Hot Seat
5 scenarios, 4 options each, consequence narratives, industry consensus reveal.

**Customize:** Edit the `SCENARIOS` list in `activities/activity4_ethics.py`.

### Activity 5 — AI Innovation & Entrepreneurship
Sarvam AI case study, Priority Grid, 4-stage venture pitch, Groq Founder Reality Check.

**Customize:**
- Case study: edit `SARVAM_CASE` in `activities/activity6_innovation.py`
- Venture prompt: edit `VENTURE_SYSTEM_PROMPT` in `utils/groq_client.py`

### Activity 6 — Project Mentoring & Implementation
Auto-fills from Activity 3. Adds: 90-day checklist, mentor directory, Empathy Map, Mentor Brief.

**Customize:** Edit `CHECKLIST` and `MENTOR_TYPES` in `activities/activity7_mentoring.py`.

### Activity 7 — Live Pulse Dashboard
Reads from `st.session_state`. Shows score, prompt score, plan status, ethics progress, and confidence shift.

---

## 🤖 Groq Integration

The app uses [Groq](https://groq.com) for fast, free-tier LLM inference.

### Models Used

| Purpose | Model | Why |
|---------|-------|-----|
| Prompt execution (Activity 2) | `openai/gpt-oss-20b` | Fast, cheap, plenty smart |
| Reality Check (Activities 3 & 5) | `openai/gpt-oss-120b` | Deeper reasoning, better critique |

### Features Built In

- **Caching:** Identical requests are served from memory.
- **Throttling:** ~2s between calls (30 RPM free-tier limit).
- **Graceful fallback:** If the API fails, the app switches to rule-based logic silently.
- **Participant keys:** Users can bring their own key without touching your config.

---

## 🛠️ Deployment

### Option A — Streamlit Community Cloud (Free, Easiest)

1. Push the repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → connect your repo → select `app.py`
4. Under **Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Click **Deploy**

### Option B — Your Own Domain / VPS

```bash
git clone https://github.com/your-username/genai-innovation-studio.git
cd genai-innovation-studio
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
nano .env    # add GROQ_API_KEY
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

Then point Nginx/Caddy at port 8501.

### Option C — Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t genai-studio .
docker run -p 8501:8501 --env-file .env genai-studio
```

---

## 🧪 Testing Checklist

Before the session day:

- [ ] Run the app locally — no errors on load
- [ ] Navigate to all 7 activities — each renders correctly
- [ ] Complete Activity 1 — score shows, timer works
- [ ] Submit a prompt in Activity 2 — rule score appears
- [ ] Enable AI mode — Groq output appears side-by-side
- [ ] Complete Activity 3 — Reality Check returns a grade
- [ ] Answer one scenario in Activity 4 — consequence reveals
- [ ] Complete Activity 5 — Founder Reality Check returns a grade
- [ ] Complete Activity 6 — Empathy Map saves, Mentor Brief downloads
- [ ] Visit Live Dashboard — no crash, values shown
- [ ] Hard refresh — app reloads cleanly
- [ ] Open in incognito — new participant ID generated
- [ ] Disable AI mode — all activities still work

---

## 🎓 Session-Day Tips

1. **Pre-warm the Groq cache** the day before — run 3–4 sample prompts so participants get instant cached responses.
2. **QR code on the opening slide** linking to the deployed URL — zero typing.
3. **Second screen** showing the Live Dashboard — creates ambient engagement.
4. **Kill switch ready** — if Groq rate-limits, toggle AI mode off. Nobody panics.
5. **Backup plan** — have the app running locally on your laptop in case the deployment hiccups.

---

## 🧰 Tech Stack

| Layer | Tool |
|-------|------|
| Framework | Streamlit |
| Charts | Plotly Express |
| Data | Pandas |
| LLM | Groq (optional) |
| Styling | Custom CSS |
| State | `st.session_state` |

**No database. No backend server. No ORM.**

---

## 📜 License

MIT — free to use, modify, and share for educational purposes.

---

## 🙏 Credits

- **Concept & facilitation:** UGC-MMTTC Refresher Course, JNTUH
- **Case studies:** Sarvam AI (India's sovereign AI unicorn) · NCRB Suicide Data Dashboard
- **Built with:** Streamlit · Plotly · Groq

---

## 🐛 Troubleshooting

### "CSS file not found"
Ensure `assets/styles.css` exists at the project root level.

### "No key available. AI mode will not work."
Add `GROQ_API_KEY` to `.env`, `st.secrets`, or the sidebar input. Or toggle AI mode off.

### "Error code: 404 - model does not exist"
Groq deprecates models periodically. Update `DEFAULT_MODEL` and `FALLBACK_MODEL` in `utils/groq_client.py`. Current recommended: `openai/gpt-oss-20b` and `openai/gpt-oss-120b`.

### "NameError: name 'json' is not defined"
Add `import json` at the top of `utils/groq_client.py`.

### "ImportError: DLL load failed while importing join" (Windows)
Your Windows security policy is blocking pandas. Disable **Smart App Control** in Windows Security, or use Conda instead of pip. This will **not** occur in cloud deployments.

### Cards look dark
Hard refresh the browser (`Ctrl+Shift+R`). Confirm `load_css()` is called in `app.py` and `assets/styles.css` is the light version.

### "AttributeError: st.session_state has no attribute X"
A session state key wasn't initialized. Add it to the `defaults` dict in `utils/state.py`.

---

## 📬 Contact

For questions, feedback, or adaptations — open an issue on GitHub or reach out via the course forum.

---

**Built with ❤️ for the UGC-MMTTC Refresher Course.**
```

