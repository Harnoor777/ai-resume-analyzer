import json, re, os, math
import numpy as np
from collections import Counter

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
    "cross functional","functional teams","cross functionally","computer science",
    "fair chance","equal opportunity","veteran status","national origin","los angeles",
    "artificial intelligence","job posting","job duties","computer hardware",
    "openai s","at scale","at datadog",
}

# FAISS index loaded once at module level
_faiss_index = None
_faiss_meta  = None
_model       = None

def _load_faiss():
    global _faiss_index, _faiss_meta
    if _faiss_index is None:
        import faiss
        base = os.path.join(os.path.dirname(__file__), "..", "..")
        idx_path  = os.path.join(base, "datasets", "faiss_index.bin")
        meta_path = os.path.join(base, "datasets", "faiss_meta.json")
        if os.path.exists(idx_path):
            _faiss_index = faiss.read_index(idx_path)
            with open(meta_path, encoding="utf-8") as f:
                _faiss_meta = json.load(f)
    return _faiss_index, _faiss_meta

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def normalize(text):
    return re.sub(r'\s+', ' ', text.lower().strip())

def is_real_skill(phrase):
    return phrase.lower() not in JUNK_PHRASES

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

def _grade(score):
    if score >= 80: return "A"
    if score >= 65: return "B"
    if score >= 50: return "C"
    if score >= 35: return "D"
    return "F"

def score_against_all_jobs(resume, jobs_csv, skills, top_n=10):
    import pandas as pd

    resume_text = resume.get("raw_text", "")
    index, meta = _load_faiss()

    if index is not None:
        # FAISS fast path
        model = _get_model()
        r_emb = model.encode([resume_text[:2000]], convert_to_numpy=True).astype(np.float32)
        import faiss as faiss_lib
        faiss_lib.normalize_L2(r_emb)

        # get top_n * 5 candidates from FAISS then re-rank
        k = min(top_n * 5, index.ntotal)
        scores, indices = index.search(r_emb, k)

        df = pd.read_csv(jobs_csv).fillna("")

        results = []
        for sem_score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(df): continue
            job = df.iloc[idx].to_dict()
            job_text = job.get("description","") + " " + job.get("title","")
            kw = keyword_score(resume_text, job_text, skills)
            ws = weighted_section_score(resume, job_text, skills)
            final = (kw["score"] * 0.35 +
                     ws["score"] * 0.35 +
                     float(sem_score) * 0.30)
            results.append({
                "final_score":    round(final * 100, 1),
                "grade":          _grade(final * 100),
                "keyword_match":  kw,
                "weighted_match": ws,
                "semantic_score": round(float(sem_score) * 100, 1),
                "job_title":      job.get("title",""),
                "job_company":    job.get("company",""),
                "location":       job.get("location",""),
                "apply_url":      job.get("apply_url",""),
                "description":    job.get("description","")[:300],
            })

        results.sort(key=lambda x: x["final_score"], reverse=True)
        return results[:top_n]

    else:
        # fallback: tfidf only (no FAISS)
        print("FAISS index not found, using keyword scoring only...")
        df = pd.read_csv(jobs_csv).fillna("")
        results = []
        for _, row in df.iterrows():
            job = row.to_dict()
            job_text = job.get("description","") + " " + job.get("title","")
            kw = keyword_score(resume_text, job_text, skills)
            ws = weighted_section_score(resume, job_text, skills)
            final = (kw["score"] * 0.50 + ws["score"] * 0.50)
            results.append({
                "final_score":    round(final * 100, 1),
                "grade":          _grade(final * 100),
                "keyword_match":  kw,
                "weighted_match": ws,
                "semantic_score": 0,
                "job_title":      job.get("title",""),
                "job_company":    job.get("company",""),
                "location":       job.get("location",""),
                "apply_url":      job.get("apply_url",""),
                "description":    job.get("description","")[:300],
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