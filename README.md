# AI Interview Accelerator & Portfolio Studio

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![Groq LLM](https://img.shields.io/badge/LLM-Groq%20API-orange.svg)](https://groq.com)
[![Vercel Ready](https://img.shields.io/badge/Deploy-Vercel-black.svg)](https://vercel.com)

**AI Interview Accelerator** is an end-to-end career preparation platform tailored to one specific target role. Given a Job Description (JD) and your Resume, the system:
1. Deconstructs what the employer requires and computes your objective match score.
2. Synthesizes a role-aligned, production-ready **Portfolio Website** customized for recruiter review with multi-theme switching and instant HTML export.
3. Conducts a dynamic, out-loud **AI Voice Mock Interview** that evaluates your answers in real time and probes your specific projects.
4. Generates an exhaustive **Diagnostic Performance Report** with competency benchmarks, speech signal analytics, and an actionable preparation plan.

---

## What It Does

| Step | Feature | Description |
|---|---|---|
| **Step 1** | **Document Parsing & Extraction** | Upload or paste your JD and Resume in **PDF**, **DOCX**, or **TXT** format. |
| **Step 2** | **Role & Candidate Fit Analysis** | Extracts technical competencies, role responsibilities, experience levels, and computes a mathematical fit score. Flags specific resume claims that an interviewer will probe. |
| **Step 3** | **Tailored Portfolio Studio** | Automatically architects a clean, production-grade technical portfolio showcasing custom case studies, system architectures, and categorized competencies matching the JD. |
| **Step 4** | **Adaptive AI Voice Interview** | A 3-stage spoken interview with browser-native text-to-speech and real-time speech recognition. Adapts difficulty based on answer quality. |
| **Step 5** | **Performance & Readiness Report** | Comprehensive breakdown across 7 competencies, speech pace analysis (WPM & filler words), question-by-question feedback, and an overall Readiness verdict. |

---

## Project Structure

```
interview-accelerator/
├── api/
│   └── index.py            # Vercel serverless entrypoint exposing FastAPI
├── backend/
│   ├── __init__.py
│   ├── main.py             # FastAPI REST endpoints, routing, and app lifecycle
│   ├── analysis.py         # JD deconstruction, candidate analysis & fit scoring
│   ├── interview.py        # Turn state machine, adaptive difficulty & report compiler
│   ├── portfolio.py        # Tailored portfolio JSON generator & multi-theme HTML engine
│   ├── parsing.py          # Multi-format document parser (PDF, DOCX, TXT)
│   └── llm.py              # Groq API client with strict JSON schema parsing & retry fallback
├── frontend/
│   └── index.html          # Single-file modern UI (HTML5, responsive CSS, vanilla JS)
├── .env                    # Environment variables (API keys & model config)
├── .gitignore              # Git ignore rules for virtualenvs, caches & temp files
├── README.md               # Project documentation & setup instructions
├── requirements.txt        # Python backend dependencies
└── vercel.json             # Vercel serverless deployment routing configuration
```

---

## Architectural Breakdown

```
Browser Frontend (index.html)
  ├─ Web Speech API       → Real-time Speech-to-Text (live transcript)
  ├─ SpeechSynthesis      → Text-to-Speech (interviewer voice)
  ├─ Theme Switcher       → Professional / Futuristic / Playful live re-render
  └─ REST fetch() ──────────────┐
                                ▼
FastAPI Backend Engine (backend/main.py)
  ├─ parsing.py    → PDF / DOCX / TXT text extraction via pypdf & python-docx
  ├─ analysis.py   → Semantic JD role analysis & weighted candidate fit scoring
  ├─ portfolio.py  → Production-ready portfolio synthesis & standalone HTML generator
  ├─ interview.py  → Adaptive conversation turns, difficulty adjustments & final diagnostic
  └─ llm.py        → Ultra-fast inference via Groq Cloud LLMs (JSON-mode enforced)
                                ▼
                       Groq LLM Platform
```

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/extract` | Upload and extract raw text from PDF, DOCX, or TXT documents |
| `POST` | `/api/analyze` | Parse JD and Resume, compute weighted fit score, and initialize session |
| `POST` | `/api/portfolio` | Synthesize tailored portfolio content and generate responsive HTML website |
| `POST` | `/api/portfolio/html` | Instant re-render of portfolio website with selected design theme |
| `POST` | `/api/interview/start` | Generate the first adaptive screening question |
| `POST` | `/api/interview/answer` | Evaluate candidate spoken answer, update metrics, and produce next question |
| `POST` | `/api/interview/report` | Compile final scored performance report and readiness verdict |
| `GET` | `/p/{session_id}` | Direct public endpoint to view standalone portfolio website |

---

## Features in Detail

### 1. Tailored Portfolio Studio
The Portfolio Studio analyzes the requirements in the job description and highlights your relevant skills, projects, and achievements into a clean, ready-to-share portfolio website:
- **Featured System Case Studies**: Formats projects with realistic engineering contexts, end-to-end architectures, tech stacks, and quantifiable impact metrics.
- **Categorized Technical Competencies**: Organizes active skills into **Languages & Core**, **Frameworks & AI/ML**, and **Cloud, Databases & Tools**.
- **Three Design Themes**:
  -  **Professional**: Clean, corporate modern blue palette (`#2563eb`), Inter typography, elegant card elevation.
  -  **Futuristic**: Dark cyberpunk aesthetic (`#00ffff` & `#bd00ff`), Orbitron monospace typography, glowing borders.
  -  **Playful**: Vibrant contemporary editorial aesthetic (`#ff5a5f` & `#00a699`), Poppins typography, warm card accents.
- **Responsive Inspection**: Toggle between **Desktop View** and **Mobile View** inside an interactive mock browser frame.
- **Instant Export**: Download the self-contained `.html` website with one click, or open it in a fresh full-screen tab.

### 2. Adaptive Voice Mock Interview
The interview loop runs across three difficulty tiers:

| Tier | Level | Focus & Style | Question Count |
|---|---|---|:---:|
| 1 | **Screening** | Recruiter-style: Career narrative, motivation, core qualifications | 3 |
| 2 | **Competency** | Technical & behavioural deep-dive tied to projects on your resume | 3 |
| 3 | **Deep-Dive** | Edge cases, system constraints, trade-offs, and probing vague claims | 4 |

#### Real-Time Adaptive Logic
- **Dual-Job Turn**: Each turn executes a single unified LLM prompt that evaluates the previous spoken answer and crafts the next question simultaneously, halving roundtrip latency.
- **Dynamic Difficulty**: Answer scores of 8+/10 increase question difficulty (1 to 5 scale), while scores below 4/10 drop difficulty to simpler clarifying questions.
- **Speech Signal Telemetry**: Computes words-per-minute (WPM), answer duration, and counts filler words (*um, uh, basically, you know*) to evaluate communication composure.

### 3. Scoring & Readiness Formula

#### Weighted Job Fit
Requirements are classified as **Strong** (full credit), **Partial** (half credit), or **Missing** (zero credit), with required skills weighted $2\times$ over preferred skills:

$$\text{Fit Score} = 100 \times \frac{\sum (\text{weight} \times \text{credit})}{\sum \text{weight}}$$

#### Interview Readiness Score

$$\text{Readiness} = 0.5 \times \text{Interview Score} + 0.2 \times \text{Avg Competency} + 0.3 \times \text{Job Fit}$$

| Readiness Score | Verdict |
|---|---|
| $< 40$ | 🔴 **Not Ready** |
| $40 - 59$ | 🟡 **Needs Preparation** |
| $60 - 77$ | 🟢 **Interview Ready** |
| $78 - 100$ | 🌟 **Strong Candidate** |

---

## Getting Started

### Prerequisites
- **Python 3.10+**
- A free **[Groq API Key](https://console.groq.com)**
- Google Chrome or Microsoft Edge (recommended for Web Speech API speech synthesis & recognition)

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vanig245/Interview-Accelerator.git
   cd Interview-Accelerator
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate       # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   ```

5. **Start the local server:**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

6. **Launch the application:**
   Open [http://localhost:8000](http://localhost:8000) in Chrome or Edge.

---

## Deployment

### Option A: Deploy to Vercel (Recommended Serverless)

The project includes built-in Vercel configuration (`vercel.json` + `api/index.py`):

1. Push your repository to GitHub.
2. Log in to [Vercel](https://vercel.com) and click **Add New Project**.
3. Select your repository.
4. Under **Environment Variables**, add:
   - `GROQ_API_KEY` = your Groq API key
   - `GROQ_MODEL` = `openai/gpt-oss-120b` (or `llama-3.3-70b-versatile`)
5. Click **Deploy**. Vercel will build and serve your app globally via `@vercel/python`.

### Option B: Deploy to Render / Cloud Platforms

The application runs as a standard FastAPI web service:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:** `GROQ_API_KEY`, `GROQ_MODEL`
- **Note:** Ensure your deployment URL uses **HTTPS** so browsers allow microphone permissions.

---

## License

This project is licensed under the [MIT License](LICENSE).
