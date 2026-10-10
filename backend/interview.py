import re
from .llm import chat_json

LEVELS = {1: ("Screening", 3), 2: ("Competency", 3), 3: ("Deep-Dive", 4)}
TOTAL_Q = sum(n for _, n in LEVELS.values())
FILLERS = re.compile(r"\b(um+|uh+|erm|you know|basically|actually|sort of|kind of|like)\b", re.I)

LEVEL_RULES = {
    1: "SCREENING: first-round recruiter style. Ask about a specific project/experience from THEIR resume, motivation for THIS role, "
       "basic understanding of the role's core skills, and career goals. Never ask a generic 'tell me about yourself'.",
    2: "COMPETENCY: job-specific. Test technical understanding, problem solving, decision-making and behavioural competencies from the JD, "
       "tied to their actual projects and experience. Ask for concrete examples and practical application.",
    3: "DEEP-DIVE: tough senior interviewer. Probe resume claims (ask how metrics were measured), challenge vague answers, ask why/how, "
       "introduce realistic scenarios and edge cases, ask counter-questions, point out inconsistencies. Test depth and reasoning.",
}

SYSTEM = """You are an experienced interviewer conducting a live spoken mock interview. You speak naturally and briefly.
Each turn you (1) evaluate the candidate's latest answer honestly and strictly, then (2) ask exactly ONE next question.
Rules for the next question:
- It must depend on the candidate's last answer: follow up on vague points, unsupported claims or interesting details.
- If the last answer was strong, raise difficulty (depth, scenario, edge case). If weak, probe the gap with a simpler clarifying
  question and check fundamentals before moving on.
- Use details from the resume and JD. Do not repeat topics already covered unless following up.
- Spoken style: max 2-3 sentences, no lists, no markdown. If the level changes, start with one short transition sentence.
Return JSON:
{"evaluation": {"score": 0-10, "strengths": [str], "gaps": [str], "claims_made": [str], "relevance": 0-10},
 "next_question": str, "topic": str, "question_type": "followup"|"new_topic"|"scenario"|"counter"|"clarification"}
If told this is the final answer, set next_question to "" and still evaluate. If there is no answer yet, set evaluation to null."""

def metrics(answer: str, duration: float) -> dict:
    words = len(answer.split())
    wpm = round(words / (duration / 60)) if duration > 3 else None
    return {"words": words, "duration": round(duration, 1), "wpm": wpm, "fillers": len(FILLERS.findall(answer))}

def new_session(jd, resume, role, cand) -> dict:
    return {"jd": jd, "resume": resume, "role": role, "cand": cand, "history": [], "level": 1,
            "answered_in_level": 0, "difficulty": 2, "strengths": [], "weaknesses": [], "topics": [],
            "current_q": "", "done": False}

def _context(s: dict) -> str:
    r, c = s["role"], s["cand"]
    return (f"ROLE: {r.get('role_title')}\nREQUIRED SKILLS: {r.get('required_skills')}\n"
            f"RESPONSIBILITIES: {r.get('key_responsibilities')}\nBEHAVIOURAL COMPETENCIES: {r.get('behavioural_competencies')}\n"
            f"CANDIDATE GAPS (partial/missing): {c['fit']['partial'] + c['fit']['missing']}\n"
            f"CLAIMS TO PROBE: {c.get('claims_to_probe')}\n\nRESUME:\n{s['resume'][:6000]}")

def next_turn(s: dict, answer: str | None = None, duration: float = 0) -> dict:
    is_last, next_level = False, s["level"]
    if answer is not None:
        s["history"].append({"level": s["level"], "question": s["current_q"], "answer": answer,
                             "metrics": metrics(answer, duration)})
        s["answered_in_level"] += 1
        if s["answered_in_level"] >= LEVELS[s["level"]][1]:
            if s["level"] == 3: is_last = True
            else: next_level = s["level"] + 1

    recent = "\n".join(f"Q: {h['question']}\nA: {h['answer']}" for h in s["history"][-4:])
    user = (f"{_context(s)}\n\nINTERVIEW STATE:\n- Next question level: {next_level} ({LEVELS[next_level][0]})\n"
            f"- Level guidance: {LEVEL_RULES[next_level]}\n- Current difficulty (1-5): {s['difficulty']}\n"
            f"- Strengths shown so far: {s['strengths'][-6:]}\n- Weaknesses so far: {s['weaknesses'][-6:]}\n"
            f"- Topics already covered: {s['topics']}\n- This is the FINAL answer: {is_last}\n\n"
            f"RECENT CONVERSATION:\n{recent or '(none yet)'}\n\n"
            f"LATEST CANDIDATE ANSWER TO EVALUATE:\n{answer if answer is not None else '(no answer yet, ask the first question)'}")
    out = chat_json(SYSTEM, user, temperature=0.6)

    ev = out.get("evaluation")
    if answer is not None and ev:
        s["history"][-1]["eval"] = ev
        s["strengths"] += ev.get("strengths", [])
        s["weaknesses"] += ev.get("gaps", [])
        score = ev.get("score", 5)
        s["difficulty"] = min(5, s["difficulty"] + 1) if score >= 8 else max(1, s["difficulty"] - 1) if score <= 4 else s["difficulty"]
    if out.get("topic"): s["topics"].append(out["topic"])

    if is_last:
        s["done"] = True
        return {"done": True}
    if next_level != s["level"]:
        s["level"], s["answered_in_level"] = next_level, 0
    s["current_q"] = out["next_question"]
    return {"done": False, "question": s["current_q"], "level": s["level"], "level_name": LEVELS[s["level"]][0],
            "difficulty": s["difficulty"], "progress": len(s["history"]), "total": TOTAL_Q,
            "question_type": out.get("question_type")}

REPORT_SYSTEM = """You are a senior interviewer writing an honest, specific performance report for a mock interview.
Score strictly: vague, short or incorrect answers must score low; do not inflate. Never give generic feedback; always reference
what the candidate actually said. Return JSON:
{"overall_score": 0-100,
 "competency_scores": {"Role Fit": 0-100, "Technical Knowledge": 0-100, "Problem Solving": 0-100, "Communication": 0-100,
                       "Confidence": 0-100, "Depth of Understanding": 0-100, "Behavioural Fit": 0-100},
 "question_feedback": [{"question": str, "answer": str, "assessment": str, "good": str, "better": str, "ideal_direction": str}],
 "strengths": [str], "weaknesses": [str],
 "preparation_gaps": [{"priority": 1, "topic": str, "review": [str]}],
 "summary": str}
Use the speaking metrics (pace, fillers, answer length) as evidence for Communication and Confidence, but base most scores on answer quality.
'better' must be actionable, e.g. say exactly which numbers, metrics or reasoning were missing. Order preparation_gaps by priority."""

def readiness(overall: int, comps: dict, fit: int) -> dict:
    nums = [v for v in comps.values() if isinstance(v, (int, float))]
    avg = sum(nums) / max(len(nums), 1)
    score = round(0.5 * float(overall or 0) + 0.2 * avg + 0.3 * fit)
    if score < 40:
        label, emoji, msg = "Not Ready", "🔴", "Significant preparation required."
    elif score < 60:
        label, emoji, msg = "Needs Preparation", "🟠", "Some important gaps remain."
    elif score < 78:
        label, emoji, msg = "Interview Ready", "🟡", "You can reasonably attempt the interview."
    else:
        label, emoji, msg = "Strong Candidate", "🟢", "You show strong readiness for this role."
    return {"score": score, "label": label, "emoji": emoji, "message": msg}

def build_report(s: dict) -> dict:
    turns = [{"level": LEVELS[h["level"]][0], "question": h["question"], "answer": h["answer"],
              "live_eval": h.get("eval"), "metrics": h["metrics"]} for h in s["history"]]
    user = (f"{_context(s)}\n\nJOB FIT SCORE: {s['cand']['fit']['score']}\n\nINTERVIEW TRANSCRIPT WITH METRICS:\n{turns}")
    rep = chat_json(REPORT_SYSTEM, user, temperature=0.3, max_tokens=4500)
    rep["readiness"] = readiness(rep.get("overall_score", 0), rep.get("competency_scores", {}), s["cand"]["fit"]["score"])
    ms = [h["metrics"] for h in s["history"]]
    paces = [m["wpm"] for m in ms if m["wpm"]]
    rep["speech_stats"] = {"avg_wpm": round(sum(paces) / len(paces)) if paces else None,
                           "total_fillers": sum(m["fillers"] for m in ms),
                           "avg_words": round(sum(m["words"] for m in ms) / max(len(ms), 1))}
    return rep