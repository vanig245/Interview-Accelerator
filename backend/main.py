import json
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from . import parsing, analysis, interview, portfolio

app = FastAPI(title="Interview Accelerator")
SESSIONS: dict = {}
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND = BASE_DIR / "frontend"

class AnalyzeIn(BaseModel):
    jd: str
    resume: str

class SidIn(BaseModel):
    session_id: str

class PortfolioIn(BaseModel):
    session_id: str | None = None
    jd: str | None = None
    resume: str | None = None
    style: str = "professional"

class PortfolioHtmlIn(BaseModel):
    portfolio_data: dict
    style: str = "professional"

class AnswerIn(BaseModel):
    session_id: str
    answer: str
    duration_sec: float = 0

def get_session(sid: str) -> dict:
    if sid not in SESSIONS:
        raise HTTPException(404, "Session not found. Please start again.")
    return SESSIONS[sid]

@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):
    text = parsing.extract_text(file.filename, await file.read())
    if not text.strip():
        raise HTTPException(400, "Could not read any text from this file.")
    return {"text": text}

@app.post("/api/analyze")
def analyze(body: AnalyzeIn):
    if len(body.jd.strip()) < 50 or len(body.resume.strip()) < 50:
        raise HTTPException(400, "Please provide a fuller JD and resume.")
    role = analysis.analyse_role(body.jd)
    cand = analysis.analyse_candidate(body.jd, body.resume, role)
    sid = str(uuid.uuid4())
    SESSIONS[sid] = interview.new_session(body.jd, body.resume, role, cand)
    return {"session_id": sid, "role": role, "candidate": cand}

@app.post("/api/portfolio")
def get_portfolio(body: PortfolioIn):
    style = body.style or "professional"
    
    # 1. Existing session
    if body.session_id and body.session_id in SESSIONS:
        s = SESSIONS[body.session_id]
        if "portfolio" not in s:
            s["portfolio"] = portfolio.generate_portfolio(s["jd"], s["resume"], s["role"], s["cand"])
        data = s["portfolio"]
        html = portfolio.generate_website_html(data, style=style)
        return {"data": data, "html": html, "style": style, "session_id": body.session_id}
    
    # 2. Or generate directly using raw JD & resume (for stateless Vercel environments)
    if body.jd and body.resume:
        if len(body.jd.strip()) < 50 or len(body.resume.strip()) < 50:
            raise HTTPException(400, "Please provide a fuller JD and resume.")
        role = analysis.analyse_role(body.jd)
        cand = analysis.analyse_candidate(body.jd, body.resume, role)
        sid = str(uuid.uuid4())
        data = portfolio.generate_portfolio(body.jd, body.resume, role, cand)
        SESSIONS[sid] = interview.new_session(body.jd, body.resume, role, cand)
        SESSIONS[sid]["portfolio"] = data
        html = portfolio.generate_website_html(data, style=style)
        return {"data": data, "html": html, "style": style, "session_id": sid}
        
    raise HTTPException(400, "Please provide a valid session_id or both jd and resume.")

@app.post("/api/portfolio/html")
def render_portfolio_html(body: PortfolioHtmlIn):
    html = portfolio.generate_website_html(body.portfolio_data, style=body.style or "professional")
    return {"html": html, "style": body.style}

@app.get("/p/{session_id}", response_class=HTMLResponse)
@app.get("/portfolio/{session_id}", response_class=HTMLResponse)
def view_public_portfolio(session_id: str, style: str = "professional"):
    if session_id not in SESSIONS:
        raise HTTPException(404, "Portfolio not found or session has expired. Please launch the app to generate a fresh link.")
    s = SESSIONS[session_id]
    if "portfolio" not in s:
        s["portfolio"] = portfolio.generate_portfolio(s["jd"], s["resume"], s["role"], s["cand"])
    html = portfolio.generate_website_html(s["portfolio"], style=style)
    return HTMLResponse(content=html)

@app.post("/api/interview/start")
def start(body: SidIn):
    return interview.next_turn(get_session(body.session_id))

@app.post("/api/interview/answer")
def answer(body: AnswerIn):
    s = get_session(body.session_id)
    if not body.answer.strip():
        raise HTTPException(400, "Empty answer.")
    return interview.next_turn(s, body.answer.strip(), body.duration_sec)

@app.post("/api/interview/report")
def report(body: SidIn):
    return interview.build_report(get_session(body.session_id))

if FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

@app.get("/")
def index():
    index_file = FRONTEND / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Interview Accelerator</h1><p>Frontend not found.</p>")
