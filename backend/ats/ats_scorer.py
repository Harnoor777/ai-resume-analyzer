import json, re, os, math
from collections import Counter

# junk phrases that are NOT skills
JUNK_PHRASES = {
    "san francisco","such as","at least","s degree","people who","work at",
    "at figma","pay range","interview process","experience working","communication skills",
    "even if","every single","meet every","apply even","re looking","re building",
    "work on","working on","working together","at anthropic","on behalf","role as",
    "team on","impact work","about anthropic","growing group","guidance on",
    "demonstrated through","track record","long term","sales roles","base salary",
    "annual base","sponsor visas","single qualification","strong candidates",
    "preferred qualifications","minimum requirements","experience required",
    "anthropic s","stripe s","figma s","airbnb s","quickly growing","rather than",
    "most important","minimum years","professional experience","policy experts",
    "diverse perspectives","beneficial ai","steerable ai","ai safety","ai research",
    "s mission","new business","high growth","fast paced","best practices",
    "reasonable accommodation","subject matter","decision makers","third party",
    "full name","real estate","world class","health dental","dental vision",
    "family planning","mental health","parental leave","recharge days","phone reimbursement",
    "rolling basis","continuous improvement","trade offs","cutting edge","thought leadership",
    "trusted advisor","next generation","senior leaders","senior stakeholders",
    "real world","emerging technologies","revenue growth","value proposition",
    "detail oriented","self starter","product roadmap","strategic thinking",
    "cross functional","functional teams","cross functionally", "computer science"
}

def is_real_skill(phrase):
    return phrase.lower() not in JUNK_PHRASES

_model = None
def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            _model = "unavailable"
    return _model if _model != "unavailable" else None

def normalize(text):
    return re.sub(r'\s+', ' ', text.lower().strip())

def extract_keywords(text, skills):
    text = normalize(text)
    return {s.lower() for s in skills
            if is_real_skill(s)
            and re.search(r'\b' + re.escape(s.lower()) + r'\b', text)}

def keyword_score(resume_text, job_text, skills):
    r = extract_keywords(resume_text, skills)
    j = extract_keywords(job_text, skills)
    if not j: return {"score": 0, "matched": [], "missing": [], "total_required": 0}
    matched = r & j
    return {
        "score": round(len(matched) / len(j), 4),
        "matched": sorted(matched),
        "missing": sorted(j - r),
        "total_required": len(j),
    }

def weighted_section_score(resume, job_text, skills):
    sections = {
        "skills":     (" ".join(resume.get("skills", [])), 0.40),
        "experience": (resume.get("experience_section", ""), 0.35),
        "summary":    (resume.get("summary_section", ""), 0.15),
        "education":  (resume.get("education_section", ""), 0.10),
    }
    job_skills = extract_keywords(job_text, skills)
    if not job_skills: return {"score": 0, "breakdown": {}}
    total, breakdown = 0.0, {}
    for section, (content, weight) in sections.items():
        matched = extract_keywords(content, list(job_skills))
        ratio = len(matched) / len(job_skills)
        weighted = ratio * weight
        total += weighted
        breakdown[section] = {"matched": len(matched), "weight": weight, "contribution": round(weighted, 4)}
    return {"score": round(total, 4), "breakdown": breakdown}

def tfidf_cosine(t1, t2):
    def vec(t):
        words = re.findall(r'\b[a-z]{2,}\b', normalize(t))
        freq = Counter(words)
        total = sum(freq.values()) or 1
        return {w: c/total for w, c in freq.items()}
    rv, jv = vec(t1), vec(t2)
    common = set(rv) & set(jv)
    if not common: return 0.0
    dot = sum(rv[w]*jv[w] for w in common)
    nr = math.sqrt(sum(v**2 for v in rv.values()))
    nj = math.sqrt(sum(v**2 for v in jv.values()))
    return dot / (nr * nj) if nr * nj else 0.0

def semantic_score_batch(resume_text, job_texts):
    model = _get_model()
    if model:
        from sentence_transformers import util
        r_emb = model.encode(resume_text[:2000], convert_to_tensor=True)
        j_embs = model.encode([t[:2000] for t in job_texts], convert_to_tensor=True)
        scores = util.cos_sim(r_emb, j_embs)[0].tolist()
        return [round(s, 4) for s in scores]
    return [tfidf_cosine(resume_text, jt) for jt in job_texts]

WEIGHTS = {"keyword": 0.35, "weighted": 0.35, "semantic": 0.30}

def _grade(score):
    if score >= 80: return "A"
    if score >= 65: return "B"
    if score >= 50: return "C"
    if score >= 35: return "D"
    return "F"

def score_against_all_jobs(resume, jobs_csv, skills, top_n=10):
    import pandas as pd
    df = pd.read_csv(jobs_csv).fillna("")
    jobs = df.to_dict("records")
    resume_text = resume.get("raw_text", "")
    job_texts = [j.get("description","") + " " + j.get("title","") for j in jobs]

    print(f"Scoring {len(jobs)} jobs...")
    sem_scores = semantic_score_batch(resume_text, job_texts)

    results = []
    for job, sem in zip(jobs, sem_scores):
        job_text = job.get("description","") + " " + job.get("title","")
        kw = keyword_score(resume_text, job_text, skills)
        ws = weighted_section_score(resume, job_text, skills)
        final = (kw["score"] * WEIGHTS["keyword"] +
                 ws["score"] * WEIGHTS["weighted"] +
                 sem         * WEIGHTS["semantic"])
        results.append({
            "final_score":    round(final * 100, 1),
            "grade":          _grade(final * 100),
            "keyword_match":  kw,
            "weighted_match": ws,
            "semantic_score": round(sem * 100, 1),
            "job_title":      job.get("title",""),
            "job_company":    job.get("company",""),
            "apply_url":      job.get("apply_url",""),
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from parsers.resume_parser import parse_resume

    if len(sys.argv) < 2:
        print("Usage: python ats_scorer.py path/to/resume.pdf")
        exit(1)

    skills_path = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "skills_list.json")
    jobs_path   = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "all_jobs.csv")

    skills = json.load(open(skills_path, encoding="utf-8"))
    resume = parse_resume(sys.argv[1])

    print(f"\nResume: {resume['name']}")
    print(f"Skills: {resume['skills']}\n")

    top = score_against_all_jobs(resume, jobs_path, skills, top_n=10)

    print("\nTop 10 Matches:\n")
    for i, r in enumerate(top, 1):
        print(f"{i}. [{r['grade']}] {r['final_score']}/100 — {r['job_title']} @ {r['job_company']}")
        print(f"   Semantic: {r['semantic_score']}%")
        print(f"   Matched:  {r['keyword_match']['matched']}")
        print(f"   Missing:  {r['keyword_match']['missing']}")
        print(f"   Apply:    {r['apply_url']}\n")