import os, json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def _chat(prompt: str, system: str = None, max_tokens: int = 1024) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()

def analyze_resume_for_job(resume: dict, job: dict, ats_result: dict) -> dict:
    resume_text = f"""
Name: {resume.get('name')}
Skills: {', '.join(resume.get('skills', []))}
Summary: {resume.get('summary_section', '')[:500]}
Experience: {resume.get('experience_section', '')[:800]}
Education: {resume.get('education_section', '')[:300]}
""".strip()

    job_text = f"""
Title: {job.get('title')}
Company: {job.get('company')}
Description: {job.get('description', '')[:1000]}
""".strip()

    matched = ats_result.get('keyword_match', {}).get('matched', [])
    missing = ats_result.get('keyword_match', {}).get('missing', [])
    score = ats_result.get('final_score', 0)

    system = "You are an expert resume coach and ATS specialist. Be concise, specific, and actionable."

    # 1. match analysis
    match_prompt = f"""
Resume:
{resume_text}

Job:
{job_text}

ATS Score: {score}/100
Matched Skills: {matched}
Missing Skills: {missing}

Give a 3-4 sentence analysis of why this candidate does or doesn't match this role. Be specific and honest.
"""
    match_analysis = _chat(match_prompt, system)

    # 2. missing skills advice
    skills_prompt = f"""
The candidate is missing these skills for the job "{job.get('title')}": {missing}

In 2-3 sentences, tell them which missing skills are most critical to learn first and why.
"""
    skills_advice = _chat(skills_prompt, system, max_tokens=300)

    # 3. summary rewrite
    summary_prompt = f"""
Original summary:
{resume.get('summary_section', '')[:400]}

Rewrite this summary to better target the role of "{job.get('title')}" at {job.get('company')}.
Keep it under 4 sentences. Be specific and professional.
"""
    rewritten_summary = _chat(summary_prompt, system, max_tokens=300)

    # 4. cover letter
    cover_prompt = f"""
Write a short, punchy cover letter (3 paragraphs) for {resume.get('name')} applying to {job.get('title')} at {job.get('company')}.

Candidate background:
{resume_text}

Job context:
{job_text}

Be specific, genuine, and avoid generic phrases. Max 200 words.
"""
    cover_letter = _chat(cover_prompt, system, max_tokens=400)

    return {
        "job_title": job.get("title"),
        "job_company": job.get("company"),
        "ats_score": score,
        "match_analysis": match_analysis,
        "skills_advice": skills_advice,
        "rewritten_summary": rewritten_summary,
        "cover_letter": cover_letter,
        "apply_url": job.get("apply_url", ""),
    }

def analyze_top_matches(resume: dict, top_jobs: list, all_jobs_csv: str) -> list:
    import pandas as pd
    df = pd.read_csv(all_jobs_csv).fillna("")
    jobs_map = {row["apply_url"]: row.to_dict() for _, row in df.iterrows()}

    results = []
    for i, ats_result in enumerate(top_jobs, 1):
        url = ats_result.get("apply_url", "")
        job = jobs_map.get(url, {
            "title": ats_result.get("job_title"),
            "company": ats_result.get("job_company"),
            "description": "",
            "apply_url": url,
        })
        print(f"Analyzing job {i}/{len(top_jobs)}: {job.get('title')} @ {job.get('company')}")
        result = analyze_resume_for_job(resume, job, ats_result)
        results.append(result)

    return results


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from parsers.resume_parser import parse_resume
    from ats.ats_scorer import score_against_all_jobs

    if len(sys.argv) < 2:
        print("Usage: python llm_analyzer.py path/to/resume.pdf")
        exit(1)

    skills_path = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "skills_list.json")
    jobs_path   = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "all_jobs.csv")

    skills = json.load(open(skills_path, encoding="utf-8"))
    resume = parse_resume(sys.argv[1])

    print(f"Resume: {resume['name']}")
    print("Getting top job matches...")
    top_jobs = score_against_all_jobs(resume, jobs_path, skills, top_n=3)

    print("\nRunning LLM analysis on top 3 matches...\n")
    analyses = analyze_top_matches(resume, top_jobs, jobs_path)

    for i, a in enumerate(analyses, 1):
        print(f"\n{'='*60}")
        print(f"JOB {i}: {a['job_title']} @ {a['job_company']}")
        print(f"ATS Score: {a['ats_score']}/100")
        print(f"\nMATCH ANALYSIS:\n{a['match_analysis']}")
        print(f"\nSKILLS ADVICE:\n{a['skills_advice']}")
        print(f"\nREWRITTEN SUMMARY:\n{a['rewritten_summary']}")
        print(f"\nCOVER LETTER:\n{a['cover_letter']}")
        print(f"\nApply: {a['apply_url']}")

    # save to file
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "analysis.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analyses, f, indent=2)
    print(f"\n\nFull analysis saved to reports/analysis.json")