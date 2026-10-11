# AI Interview Accelerator

Interview Accelerator is a web app that prepares you for one specific job interview. You give it a job description and your resume, and it works out what the employer wants, how well you match, and then interviews you out loud. The interviewer is an AI that reads your resume, listens to your answers, and decides what to ask next based on how you actually did. At the end you get a scored report, specific feedback on every answer, and a prioritised list of what to study before the real thing.

I built it because generic question banks never prepared me for the questions that actually get asked: the ones about my own projects and the claims on my own resume.

**Live demo:** `https://interview-accelerator-w3z8.onrender.com`  


---

## What it does

1. **Role analysis.** Paste or upload a JD (PDF, DOCX or TXT). The app extracts the role, responsibilities, required and preferred skills, technical and behavioural competencies, experience expectations, keywords and key concepts.
2. **Candidate analysis.** It compares your resume against the JD and shows your skills, relevant experience, projects and achievements, strengths, weak areas, and the resume claims an interviewer is likely to question.
3. **Job fit score.** Every JD requirement is judged as a strong, partial or missing match, and the score is computed from those judgements (see [Fit scoring](#job-fit-scoring)).
4. **Voice interview.** A three-level interview where the AI speaks each question, listens to your spoken answer, transcribes it live, evaluates it, and generates the next question.
5. **Performance report.** Overall score, seven competency scores, question-by-question feedback, strengths, weaknesses, a prioritised preparation plan, and a readiness verdict from 🔴 Not Ready to 🟢 Strong Candidate.

### The three interview levels

| Level | Style | Questions |
|---|---|---|
| 1. Screening | Recruiter-style. Resume, motivation, role fit, basics | 3 |
| 2. Competency | Job-specific technical and behavioural questions tied to your projects | 3 |
| 3. Deep-Dive | Tough interviewer. Probes claims, challenges vague answers, scenarios, edge cases | 4 |

---

## How the interview stays dynamic

There is no question list anywhere in the code. Each turn makes one LLM call that does two jobs: it evaluates the answer you just gave, and it writes the next question. That call is given:

- the JD analysis and the full resume
- the requirements you only partially match or are missing
- the resume claims flagged for probing
- the recent conversation
- a running memory of strengths shown, weaknesses found, and topics already covered
- the current level and difficulty

The prompt instructs the interviewer to base the next question on your last answer: follow up on vague points and unsupported claims, go deeper when you answer well, and drop to a simpler clarifying question when you struggle. The backend handles the structure around it. It controls when the level changes, and it adjusts difficulty (1 to 5) up when an answer scores 8 or above and down when it scores 4 or below.

An example of the behaviour this produces: if you say you improved accuracy by 18% and compared against the previous version, the next question asks which metric you used and why, and if you say accuracy, the one after asks whether that still holds on an imbalanced dataset.

---

## Architecture

```
Browser (single index.html)
  ├─ Web Speech API  → speech-to-text (live transcript)
  ├─ Speech Synthesis → text-to-speech (interviewer voice)
  └─ fetch() ─────────────┐
                          ▼
FastAPI backend
  ├─ parsing.py    PDF / DOCX / TXT → text
  ├─ analysis.py   JD analysis, resume analysis, fit scoring
  ├─ interview.py  session state, adaptive turn logic, report, readiness
  └─ llm.py        Groq client, JSON-mode wrapper
                          ▼
                    Groq LLM API
```

**API endpoints**

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/extract` | Extract text from an uploaded file |
| POST | `/api/analyze` | Analyse JD and resume, compute fit, create a session |
| POST | `/api/interview/start` | Generate the first question |
| POST | `/api/interview/answer` | Evaluate an answer and return the next question |
| POST | `/api/interview/report` | Generate the final report |

**Project structure**

```
interview-accelerator/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── llm.py
│   ├── parsing.py
│   ├── analysis.py
│   └── interview.py
├── frontend/
│   └── index.html        # HTML, CSS and JS in one file
├── requirements.txt
└── .env
```

---

## Voice implementation

The loop is: the interviewer's question is spoken with the browser's speech synthesis, the microphone starts automatically afterwards, speech recognition streams a live transcript into an editable text box, and you submit when you're done. The transcript stays editable so you can fix any recognition errors before the answer is evaluated.

I chose the browser's built-in speech APIs because they need no extra keys, add no latency from uploading audio, and give real-time transcription. The trade-off is that speech recognition works best in Chrome and Edge. If it isn't available, the app falls back to typed answers.

An optional camera self-view is included so the session feels closer to a real interview. No video is recorded or analysed, and scoring is based on what you say, not how you look.

---

## Evaluation methodology

**Per-answer evaluation.** After every answer the model returns a score out of 10, relevance, strengths, gaps, and the claims you made. These feed the interviewer's memory and the difficulty control.

**Speech signals.** The backend computes words per minute, answer length and filler-word count (um, uh, basically, you know and similar) for each answer. These are passed to the report as supporting evidence for the Communication and Confidence scores. Most of the weight stays on answer quality.

**Final report.** A single LLM call receives the full transcript, the live evaluations, the speech metrics and the job fit score. It returns an overall score, seven competency scores (Role Fit, Technical Knowledge, Problem Solving, Communication, Confidence, Depth of Understanding, Behavioural Fit), and question-level feedback. Each feedback item has the question, your answer, an assessment, what was good, what could be better, and the ideal direction. The prompt requires feedback to reference what you actually said and forbids generic advice.

### Job fit scoring

Each JD requirement is classified as strong, partial or missing, and weighted: required skills count 2, preferred skills count 1. Strong earns full credit, partial earns half, missing earns none.

```
fit = 100 × Σ(weight × credit) / Σ(weight)
```

The LLM judges the evidence, but the arithmetic happens in code, so the score is consistent and explainable.

### Readiness score

```
readiness = 0.5 × interview score + 0.2 × average competency + 0.3 × job fit
```

| Score | Verdict |
|---|---|
| below 40 | Not Ready |
| 40 to 59 | Needs Preparation |
| 60 to 77 | Interview Ready |
| 78 and above | Strong Candidate |

---

## Key technical decisions

- **One combined call per turn (evaluate and ask).** It halves latency compared with separate evaluation and generation calls, and the evaluation and next question stay consistent with each other.
- **Code controls the structure, the LLM controls the content.** Level progression, difficulty bounds and score formulas are deterministic. Question wording and judgement are the model's job.
- **Strict JSON output.** Every LLM call uses JSON mode with a regex fallback parser, so malformed output doesn't crash a session.
- **Single-file frontend.** No build step, one file to deploy, easy to read end to end.
- **Server-side sessions kept in memory.** The right trade-off for a prototype; see limitations below.

---

## Getting started

**Requirements:** Python 3.10+, a [Groq API key](https://console.groq.com), and Chrome or Edge.

```bash
git clone https://github.com/vanig245/Interview-Accelerator.git
cd Interview-Accelerator

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

Run it:

```bash
uvicorn backend.main:app --reload
```

Open http://localhost:8000, paste a JD and a resume, and allow microphone access when prompted.

Groq retires models from time to time. If you see a "model decommissioned" error, pick a current model from their docs and update `GROQ_MODEL`.

## Deployment

The app is a single FastAPI service. On a platform like Render:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `GROQ_API_KEY` and `GROQ_MODEL`

HTTPS is required for microphone access in browsers, and most hosting platforms provide it by default (`localhost` also works).

---

## Limitations

- Sessions are stored in server memory, so they are lost on restart and the app should run as a single instance.
- Speech recognition quality depends on the browser and works best with clear English speech.
- Scores come from an LLM and should be treated as guidance for practice, not an objective measure.
- Interview history is not persisted between sessions.

## Roadmap

- Persistent storage with interview history and progress tracking across attempts
- Whisper-based transcription as a fallback for browsers without speech recognition
- Resume improvement suggestions based on the gaps found
- Coding and technical question mode
- Pace and pause analysis with a visual breakdown in the report
- Shareable report links

---

Built by Vani.