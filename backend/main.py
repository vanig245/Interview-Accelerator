import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from . import parsing, analysis, interview

app = FastAPI(title="Interview Accelerator")
SESSIONS: dict = {}
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

class AnalyzeIn(BaseModel):
    jd: str
    resume: str

class SidIn(BaseModel):
    session_id: str

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

app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")