from .llm import chat_json

ROLE_SYSTEM = """You are an expert technical recruiter. Analyse the job description and return JSON:
{"role_title": str, "seniority": str, "key_responsibilities": [str], "required_skills": [str],
 "preferred_skills": [str], "technical_competencies": [str], "behavioural_competencies": [str],
 "experience_expectations": str, "keywords": [str], "concepts": [str], "qualifications": [str]}
Only use what is in the JD. Keep each item short."""

CANDIDATE_SYSTEM = """You are a strict but fair hiring manager comparing a resume to a job description.
Return JSON:
{"candidate_skills": [str], "relevant_experience": [str], "relevant_projects": [str], "achievements": [str],
 "requirement_matches": [{"requirement": str, "type": "required"|"preferred", "match": "strong"|"partial"|"missing", "evidence": str}],
 "strengths": [str], "weak_areas": [str],
 "claims_to_probe": [{"claim": str, "why": str}],
 "prep_areas": [str]}
Rules: requirement_matches must cover every required and preferred skill and the key technical competencies.
'strong' needs concrete evidence in the resume, 'partial' means related or shallow evidence, otherwise 'missing'.
claims_to_probe are vague, inflated or unverifiable resume statements (e.g. unexplained percentages, buzzwords)."""

def analyse_role(jd: str) -> dict:
    return chat_json(ROLE_SYSTEM, f"JOB DESCRIPTION:\n{jd[:8000]}", temperature=0.2)

def compute_fit(matches: list) -> dict:
    weight = {"required": 2, "preferred": 1}
    credit = {"strong": 1, "partial": 0.5, "missing": 0}
    total = sum(weight.get(m.get("type"), 1) for m in matches) or 1
    got = sum(weight.get(m.get("type"), 1) * credit.get(m.get("match"), 0) for m in matches)
    group = lambda k: [m["requirement"] for m in matches if m.get("match") == k]
    return {"score": round(100 * got / total), "strong": group("strong"),
            "partial": group("partial"), "missing": group("missing")}

def analyse_candidate(jd: str, resume: str, role: dict) -> dict:
    user = f"JD ANALYSIS:\n{role}\n\nRESUME:\n{resume[:8000]}"
    cand = chat_json(CANDIDATE_SYSTEM, user, temperature=0.2)
    cand["fit"] = compute_fit(cand.get("requirement_matches", []))
    return cand