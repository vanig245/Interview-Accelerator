import json
from .llm import chat_json

PORTFOLIO_SYSTEM = """You are an elite technical career coach and principal software architect.
Your task is to analyze a Job Description (JD) and a Candidate's Resume, and synthesize an
authoritative, end-to-end technical portfolio website tailored for company job applications.

CRITICAL INSTRUCTIONS:
1. Do NOT mention 'Resume Aligned', 'Gap-Closing Blueprint', 'Gaps', 'Failures', or 'Missing Requirements' ANYWHERE in the output.
2. The portfolio must be 100% positive, professional, and ready to be directly submitted to recruiters and hiring managers.
3. Every project must be presented as a real, production-ready engineering achievement with clear architecture, tech stack, and measurable impact.
4. Categorize skills purely by technical discipline (e.g., Languages, Frameworks & AI/ML, Cloud & Infrastructure). Every skill must be presented as an active competency.

Return valid JSON with this exact structure:
{
  "name": "Candidate Full Name (extract from resume or use 'Candidate')",
  "job_title": "Professional Title matching the target role (e.g. Senior Full-Stack & AI Engineer)",
  "hero_description": "2-3 high-impact sentences highlighting the candidate's engineering expertise, systems design ability, and passion for building scalable software.",
  "about_description": "Comprehensive professional overview highlighting technical foundation, engineering philosophy, and career achievements.",
  "skills": {
    "languages": ["Python", "SQL", "JavaScript", "TypeScript"],
    "frameworks": ["FastAPI", "React", "LangChain", "PyTorch", "Docker"],
    "cloud_and_tools": ["PostgreSQL", "Redis", "ChromaDB", "Git", "GitHub Actions", "AWS"]
  },
  "projects": [
    {
      "title": "Project Name",
      "category": "e.g. Distributed System, AI Application, Data Platform, Microservice Architecture",
      "tagline": "One-line technical value proposition",
      "problem_statement": "Engineering challenge or business problem solved.",
      "solution_architecture": "End-to-end architecture breakdown (Frontend -> Backend -> DB / Cache -> Cloud/Infra).",
      "tech_stack": ["Tech1", "Tech2", "Tech3"],
      "key_features": ["Feature 1 with technical depth", "Feature 2", "Feature 3"],
      "quantifiable_impact": ["Metric 1 (e.g. 40% latency reduction)", "Metric 2 (e.g. 10k RPS, 99.9% uptime)"],
      "code_starter_idea": "Brief blueprint of GitHub repo structure or key API endpoint design."
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "position": "Role Title",
      "period": "Time Period (e.g. 2022 - Present)",
      "highlights": ["High-impact bullet point with metrics and technologies", "Another achievement"],
      "skills": ["Skill1", "Skill2"]
    }
  ],
  "education": [
    {
      "degree": "Degree Name",
      "institution": "University / Institute Name",
      "details": "Major, GPA, or notable coursework"
    }
  ],
  "contact": {
    "email": "candidate@example.com",
    "phone": "Phone number or leave empty",
    "location": "City, Country or Remote",
    "linkedin": "linkedin.com/in/profile",
    "github": "github.com/profile"
  }
}

Rules:
1. Provide exactly 3 featured projects with realistic, high-caliber engineering architectures and metrics.
2. Ground all claims in realistic engineering practices (latency, concurrency, data consistency, caching, CI/CD).
3. Extract real details from the candidate's resume wherever present.
"""

def generate_portfolio(jd: str, resume: str, role: dict, cand: dict) -> dict:
    fit = cand.get("fit", {})
    all_skills = list(set((cand.get("candidate_skills") or []) + (role.get("required_skills") or [])[:5]))
    
    user_prompt = f"""TARGET ROLE:
Title: {role.get('role_title', 'Target Role')}
Seniority: {role.get('seniority', 'Not specified')}
Required Skills: {role.get('required_skills', [])}
Preferred Skills: {role.get('preferred_skills', [])}
Key Responsibilities: {role.get('key_responsibilities', [])}
Technical Competencies: {role.get('technical_competencies', [])}

CANDIDATE INFORMATION:
Resume Skills: {cand.get('candidate_skills', [])}
Resume Projects / Work: {cand.get('relevant_projects', [])}
Resume Achievements: {cand.get('achievements', [])}

FULL RESUME TEXT:
{resume[:7000]}

JOB DESCRIPTION TEXT:
{jd[:7000]}

Synthesize the professional candidate portfolio JSON now."""

    result = chat_json(PORTFOLIO_SYSTEM, user_prompt, temperature=0.3, max_tokens=4000)
    
    # Safe fallbacks
    result.setdefault("name", "Software Engineer")
    result.setdefault("job_title", role.get("role_title", "Software Engineer"))
    result.setdefault("hero_description", "Experienced engineer with a proven track record of delivering scalable solutions.")
    result.setdefault("about_description", "Passionate technologist dedicated to architecting reliable, high-impact systems.")
    
    skills_data = result.get("skills", {})
    if not isinstance(skills_data, dict):
        result["skills"] = {
            "languages": ["Python", "SQL", "JavaScript"],
            "frameworks": ["FastAPI", "React", "Docker"],
            "cloud_and_tools": ["PostgreSQL", "Redis", "Git"]
        }
    else:
        result["skills"].setdefault("languages", ["Python", "SQL"])
        result["skills"].setdefault("frameworks", ["FastAPI", "Docker"])
        result["skills"].setdefault("cloud_and_tools", ["PostgreSQL", "Git"])

    result.setdefault("projects", [])
    result.setdefault("experience", [])
    result.setdefault("education", [])
    result.setdefault("contact", {
        "email": "candidate@example.com",
        "location": "Remote",
        "github": "github.com",
        "linkedin": "linkedin.com"
    })
    
    return result

def generate_website_html(data: dict, style: str = "professional") -> str:
    """
    Generates a clean, modern, standalone portfolio website HTML
    specifically designed to be submitted directly to companies and recruiters.
    Contains NO interview prep talking points, NO gap closing references, and NO failure markers.
    """
    themes = {
        "professional": {
            "primary": "#2563eb",
            "secondary": "#1d4ed8",
            "accent": "#f59e0b",
            "bg": "#f8fafc",
            "card_bg": "#ffffff",
            "card_border": "#e2e8f0",
            "text": "#0f172a",
            "muted": "#64748b",
            "font": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            "badge_bg": "#eff6ff",
            "badge_text": "#1d4ed8",
            "nav_bg": "rgba(255, 255, 255, 0.95)",
            "gradient": "linear-gradient(135deg, #2563eb 0%, #1e40af 100%)",
            "glow": "0 10px 25px -5px rgba(37, 99, 235, 0.15)"
        },
        "futuristic": {
            "primary": "#00ffff",
            "secondary": "#bd00ff",
            "accent": "#ff007f",
            "bg": "#0a0a14",
            "card_bg": "#121224",
            "card_border": "#232345",
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "font": "'Orbitron', 'Inter', monospace",
            "badge_bg": "rgba(0, 255, 255, 0.12)",
            "badge_text": "#00ffff",
            "nav_bg": "rgba(10, 10, 20, 0.95)",
            "gradient": "linear-gradient(135deg, #00ffff 0%, #bd00ff 100%)",
            "glow": "0 0 20px rgba(0, 255, 255, 0.35)"
        },
        "playful": {
            "primary": "#ff5a5f",
            "secondary": "#00a699",
            "accent": "#fc642d",
            "bg": "#fdfbf7",
            "card_bg": "#ffffff",
            "card_border": "#fed7aa",
            "text": "#292524",
            "muted": "#78716c",
            "font": "'Poppins', 'Inter', sans-serif",
            "badge_bg": "#fff1f2",
            "badge_text": "#e11d48",
            "nav_bg": "rgba(253, 251, 247, 0.95)",
            "gradient": "linear-gradient(135deg, #ff5a5f 0%, #fc642d 100%)",
            "glow": "0 10px 25px -5px rgba(255, 90, 95, 0.2)"
        }
    }
    
    t = themes.get(style, themes["professional"])
    name = data.get("name") or "Developer Portfolio"
    job_title = data.get("job_title") or "Software Engineer"
    initials = "".join([part[0] for part in name.split()[:2]]).upper() or "ME"
    
    skills = data.get("skills", {})
    if isinstance(skills, dict):
        languages = skills.get("languages", [])
        frameworks = skills.get("frameworks", [])
        tools = skills.get("cloud_and_tools", [])
        # Fallback if old format was cached
        if not languages and not frameworks and not tools:
            languages = skills.get("core_matches", [])
            frameworks = skills.get("bridging_skills", [])
            tools = skills.get("tools_and_infrastructure", [])
    else:
        languages = ["Python", "JavaScript", "SQL"]
        frameworks = ["FastAPI", "React", "Docker"]
        tools = ["PostgreSQL", "Git", "AWS"]

    # Strict sanitize: purge any negative or gap markers
    forbidden_words = ["gap", "missing", "failure", "bridging", "growth", "weak"]
    languages = [s.strip() for s in languages if not any(w in s.lower() for w in forbidden_words)]
    frameworks = [s.strip() for s in frameworks if not any(w in s.lower() for w in forbidden_words)]
    tools = [s.strip() for s in tools if not any(w in s.lower() for w in forbidden_words)]
    
    projects = data.get("projects", [])
    experience = data.get("experience", [])
    education = data.get("education", [])
    contact = data.get("contact", {})

    # Generate projects HTML
    projects_cards = ""
    for idx, p in enumerate(projects):
        category = p.get("category") or p.get("badge") or "Featured Project"
        # Sanitize any legacy badge strings (never expose gap or failure hints)
        forbidden_badges = ["gap", "resume", "aligned", "blueprint", "fail", "missing", "weak"]
        if any(w in category.lower() for w in forbidden_badges):
            category = "Production System"

        badge_style = f"background: {t['badge_bg']}; color: {t['badge_text']}; border: 1px solid {t['card_border']};"
        tech_chips = "".join([f'<span class="tech-chip">{t_item}</span>' for t_item in p.get("tech_stack", [])])
        features_li = "".join([f'<li>{f}</li>' for f in p.get("key_features", [])])
        impact_li = "".join([f'<li>⚡ {m}</li>' for m in p.get("quantifiable_impact", [])])
        
        code_box = f'<div class="code-box"><b>Repository Architecture:</b> <code>{p.get("code_starter_idea")}</code></div>' if p.get("code_starter_idea") else ""
        
        projects_cards += f"""
        <div class="project-card">
          <div class="project-header">
            <div>
              <div class="project-badge" style="{badge_style}">{category}</div>
              <h3 class="project-title">{idx+1}. {p.get('title', 'Project')}</h3>
              <p class="project-tagline">{p.get('tagline', '')}</p>
            </div>
          </div>

          <div class="project-section">
            <h4>Problem &amp; Context</h4>
            <p>{p.get('problem_statement', '')}</p>
          </div>

          <div class="project-section">
            <h4>End-to-End System Architecture</h4>
            <div class="arch-box">🏢 {p.get('solution_architecture', '')}</div>
          </div>

          <div class="project-section">
            <h4>Technologies Used</h4>
            <div class="chips-row">{tech_chips}</div>
          </div>

          <div class="project-grid-2">
            <div class="project-section">
              <h4>Key Engineering Features</h4>
              <ul class="bullet-list">{features_li}</ul>
            </div>
            <div class="project-section">
              <h4>Measurable Impact &amp; Scale</h4>
              <ul class="bullet-list">{impact_li}</ul>
            </div>
          </div>

          {code_box}
        </div>
        """

    # Generate experience HTML
    exp_cards = ""
    for exp in experience:
        highlights = "".join([f'<li>{h}</li>' for h in exp.get("highlights", [])])
        skills_chips = "".join([f'<span class="tech-chip">{s}</span>' for s in exp.get("skills", [])])
        exp_cards += f"""
        <div class="timeline-item">
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <div class="exp-header">
              <h3 class="exp-role">{exp.get('position', 'Role')}</h3>
              <span class="exp-period">{exp.get('period', '')}</span>
            </div>
            <div class="exp-company">{exp.get('company', 'Company')}</div>
            <ul class="bullet-list">{highlights}</ul>
            <div class="chips-row" style="margin-top:10px">{skills_chips}</div>
          </div>
        </div>
        """

    # Clean categorized skills HTML
    lang_chips = "".join([f'<span class="skill-badge">{s}</span>' for s in languages])
    fw_chips = "".join([f'<span class="skill-badge">{s}</span>' for s in frameworks])
    tool_chips = "".join([f'<span class="skill-badge">{s}</span>' for s in tools])

    # Generate education HTML
    edu_cards = ""
    for edu in education:
        edu_cards += f"""
        <div class="edu-card">
          <div class="edu-icon">🎓</div>
          <div>
            <h3>{edu.get('degree', 'Degree')}</h3>
            <p class="edu-inst">{edu.get('institution', 'Institution')}</p>
            <p class="edu-details">{edu.get('details', '')}</p>
          </div>
        </div>
        """

    total_skills = len(languages) + len(frameworks) + len(tools)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{name} — {job_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@500;700;900&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: {t['font']};
      background: {t['bg']};
      color: {t['text']};
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ text-decoration: none; color: inherit; }}

    .navbar {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: {t['nav_bg']};
      backdrop-filter: blur(12px);
      border-bottom: 1px solid {t['card_border']};
      padding: 16px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 800;
      font-size: 18px;
    }}
    .brand-avatar {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: {t['gradient']};
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 700;
      box-shadow: {t['glow']};
    }}
    .nav-links {{ display: flex; gap: 24px; }}
    .nav-link {{
      font-size: 14px;
      font-weight: 500;
      color: {t['muted']};
      transition: color 0.2s;
    }}
    .nav-link:hover {{ color: {t['primary']}; }}

    .container {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 40px 20px 80px;
    }}

    .hero {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 40px;
      align-items: center;
      padding: 40px 0 60px;
      border-bottom: 1px solid {t['card_border']};
    }}
    @media(max-width: 860px) {{
      .hero {{ grid-template-columns: 1fr; }}
      .nav-links {{ display: none; }}
    }}
    .hero-badge {{
      display: inline-block;
      padding: 6px 14px;
      border-radius: 20px;
      background: {t['badge_bg']};
      color: {t['badge_text']};
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 16px;
    }}
    .hero h1 {{
      font-size: 42px;
      font-weight: 800;
      line-height: 1.15;
      margin-bottom: 12px;
      background: {t['gradient']};
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .hero-role {{
      font-size: 20px;
      color: {t['muted']};
      font-weight: 600;
      margin-bottom: 18px;
    }}
    .hero-desc {{
      font-size: 16px;
      color: {t['text']};
      margin-bottom: 28px;
      max-width: 580px;
    }}
    .hero-actions {{ display: flex; gap: 14px; flex-wrap: wrap; }}
    .btn {{
      padding: 12px 24px;
      border-radius: 30px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .btn-primary {{
      background: {t['gradient']};
      color: #fff;
      border: none;
      box-shadow: {t['glow']};
    }}
    .btn-primary:hover {{ transform: translateY(-2px); }}
    .btn-secondary {{
      background: transparent;
      color: {t['text']};
      border: 1px solid {t['card_border']};
    }}
    .btn-secondary:hover {{ background: {t['badge_bg']}; }}

    .hero-card {{
      background: {t['card_bg']};
      border: 1px solid {t['card_border']};
      border-radius: 20px;
      padding: 32px 24px;
      text-align: center;
      box-shadow: {t['glow']};
    }}
    .hero-avatar-large {{
      width: 96px;
      height: 96px;
      margin: 0 auto 16px;
      border-radius: 50%;
      background: {t['gradient']};
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 36px;
      font-weight: 800;
      box-shadow: {t['glow']};
    }}
    .stat-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-top: 24px;
      padding-top: 20px;
      border-top: 1px solid {t['card_border']};
    }}
    .stat-number {{ font-size: 24px; font-weight: 800; color: {t['primary']}; }}
    .stat-label {{ font-size: 12px; color: {t['muted']}; text-transform: uppercase; }}

    .section-title {{
      font-size: 28px;
      font-weight: 800;
      margin: 50px 0 10px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .section-subtitle {{
      color: {t['muted']};
      font-size: 15px;
      margin-bottom: 24px;
    }}

    .card {{
      background: {t['card_bg']};
      border: 1px solid {t['card_border']};
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 24px;
    }}

    /* Skills Grid */
    .skills-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
    }}
    .skill-category h3 {{
      font-size: 16px;
      margin-bottom: 14px;
      color: {t['primary']};
      font-weight: 700;
    }}
    .skill-badge {{
      display: inline-block;
      padding: 7px 14px;
      border-radius: 12px;
      font-size: 13px;
      margin: 4px;
      font-weight: 500;
      background: {t['badge_bg']};
      color: {t['badge_text']};
      border: 1px solid {t['card_border']};
      transition: transform 0.15s;
    }}
    .skill-badge:hover {{ transform: translateY(-1px); }}

    /* Project Cards */
    .project-card {{
      background: {t['card_bg']};
      border: 1px solid {t['card_border']};
      border-radius: 18px;
      padding: 28px;
      margin-bottom: 28px;
    }}
    .project-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 14px;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .project-badge {{
      display: inline-block;
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}
    .project-title {{ font-size: 22px; font-weight: 700; color: {t['text']}; }}
    .project-tagline {{ color: {t['muted']}; font-size: 14px; margin-top: 4px; }}
    .chips-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }}
    .tech-chip {{
      background: {t['bg']};
      border: 1px solid {t['card_border']};
      color: {t['text']};
      font-size: 12px;
      padding: 5px 12px;
      border-radius: 14px;
      font-weight: 500;
    }}
    .project-section {{ margin: 16px 0; }}
    .project-section h4 {{ font-size: 13px; text-transform: uppercase; color: {t['muted']}; margin-bottom: 8px; }}
    .arch-box {{
      background: {t['bg']};
      border: 1px solid {t['card_border']};
      border-radius: 8px;
      padding: 14px;
      font-family: monospace;
      font-size: 13px;
      line-height: 1.5;
    }}
    .project-grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin: 16px 0;
    }}
    @media(max-width: 700px) {{ .project-grid-2 {{ grid-template-columns: 1fr; }} }}
    .bullet-list {{ padding-left: 20px; font-size: 14px; }}
    .bullet-list li {{ margin-bottom: 8px; }}
    .code-box {{
      margin-top: 16px;
      background: {t['bg']};
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 12px;
      border: 1px solid {t['card_border']};
    }}

    .timeline {{
      position: relative;
      padding-left: 24px;
      border-left: 2px solid {t['card_border']};
      margin: 20px 0;
    }}
    .timeline-item {{ position: relative; margin-bottom: 30px; }}
    .timeline-dot {{
      position: absolute;
      left: -31px;
      top: 4px;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: {t['primary']};
      border: 2px solid {t['card_bg']};
    }}
    .exp-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
    }}
    .exp-role {{ font-size: 18px; font-weight: 700; }}
    .exp-period {{ font-size: 13px; color: {t['muted']}; font-weight: 500; }}
    .exp-company {{ font-size: 14px; color: {t['primary']}; font-weight: 600; margin-bottom: 8px; }}

    .edu-card {{
      display: flex;
      gap: 16px;
      align-items: center;
      padding: 18px;
      background: {t['card_bg']};
      border: 1px solid {t['card_border']};
      border-radius: 12px;
      margin-bottom: 12px;
    }}
    .edu-icon {{ font-size: 28px; }}
    .edu-inst {{ color: {t['muted']}; font-size: 14px; }}
    .edu-details {{ font-size: 13px; color: {t['muted']}; margin-top: 2px; }}

    .contact-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }}
    .contact-card {{
      background: {t['card_bg']};
      border: 1px solid {t['card_border']};
      padding: 18px;
      border-radius: 12px;
      text-align: center;
    }}
    .contact-label {{ font-size: 12px; color: {t['muted']}; text-transform: uppercase; }}
    .contact-val {{ font-size: 14px; font-weight: 600; margin-top: 4px; word-break: break-all; }}

    footer {{
      text-align: center;
      padding: 40px 20px;
      color: {t['muted']};
      font-size: 13px;
      border-top: 1px solid {t['card_border']};
      margin-top: 60px;
    }}
  </style>
</head>
<body>

  <nav class="navbar">
    <div class="nav-brand">
      <div class="brand-avatar">{initials}</div>
      <span>{name}</span>
    </div>
    <div class="nav-links">
      <a href="#about" class="nav-link">About</a>
      <a href="#projects" class="nav-link">Projects</a>
      <a href="#skills" class="nav-link">Skills</a>
      <a href="#experience" class="nav-link">Experience</a>
      <a href="#contact" class="nav-link">Contact</a>
    </div>
  </nav>

  <div class="container">
    <section class="hero" id="hero">
      <div>
        <span class="hero-badge">{job_title}</span>
        <h1>Hello, I'm {name}</h1>
        <div class="hero-role">{job_title}</div>
        <p class="hero-desc">{data.get('hero_description', '')}</p>
        <div class="hero-actions">
          <a href="#projects" class="btn btn-primary">Explore Featured Projects →</a>
          <a href="#contact" class="btn btn-secondary">Get in Touch</a>
        </div>
      </div>
      <div class="hero-card">
        <div class="hero-avatar-large">{initials}</div>
        <h3>{name}</h3>
        <p style="color:{t['muted']};font-size:14px">{job_title}</p>
        <div class="stat-row">
          <div><div class="stat-number">{len(projects)}</div><div class="stat-label">Projects</div></div>
          <div><div class="stat-number">{len(experience)}</div><div class="stat-label">Experience</div></div>
          <div><div class="stat-number">{total_skills}</div><div class="stat-label">Skills</div></div>
        </div>
      </div>
    </section>

    <section id="about">
      <h2 class="section-title">About Me</h2>
      <p class="section-subtitle">Professional background and engineering focus</p>
      <div class="card">
        <p style="font-size:16px;line-height:1.7">{data.get('about_description', '')}</p>
      </div>
    </section>

    <section id="projects">
      <h2 class="section-title">Featured Projects</h2>
      <p class="section-subtitle">Architectural case studies, engineering deliverables, and production-grade systems</p>
      {projects_cards}
    </section>

    <section id="skills">
      <h2 class="section-title">Technical Skills</h2>
      <p class="section-subtitle">Core competencies, frameworks, and engineering tools</p>
      <div class="skills-grid">
        <div class="card skill-category">
          <h3>💻 Languages &amp; Core</h3>
          <div>{lang_chips}</div>
        </div>
        <div class="card skill-category">
          <h3>⚙️ Frameworks &amp; AI / ML</h3>
          <div>{fw_chips}</div>
        </div>
        <div class="card skill-category">
          <h3>🛠️ Cloud, Databases &amp; Tools</h3>
          <div>{tool_chips}</div>
        </div>
      </div>
    </section>

    <section id="experience">
      <h2 class="section-title">Professional Experience</h2>
      <p class="section-subtitle">Track record and measurable impact</p>
      <div class="timeline">
        {exp_cards}
      </div>
    </section>

    {f'''
    <section id="education">
      <h2 class="section-title">Education &amp; Background</h2>
      <p class="section-subtitle">Degrees and academic credentials</p>
      {edu_cards}
    </section>
    ''' if education else ''}

    <section id="contact">
      <h2 class="section-title">Get in Touch</h2>
      <p class="section-subtitle">Connect and collaborate</p>
      <div class="contact-grid">
        <div class="contact-card">
          <div class="contact-label">Email</div>
          <div class="contact-val">{contact.get('email', 'N/A')}</div>
        </div>
        <div class="contact-card">
          <div class="contact-label">Location</div>
          <div class="contact-val">{contact.get('location', 'Remote')}</div>
        </div>
        <div class="contact-card">
          <div class="contact-label">GitHub</div>
          <div class="contact-val">{contact.get('github', 'github.com')}</div>
        </div>
        <div class="contact-card">
          <div class="contact-label">LinkedIn</div>
          <div class="contact-val">{contact.get('linkedin', 'linkedin.com')}</div>
        </div>
      </div>
    </section>
  </div>

  <footer>
    <p>© {name} • {job_title}</p>
  </footer>

</body>
</html>
"""
    return html
