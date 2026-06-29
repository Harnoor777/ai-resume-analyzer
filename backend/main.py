import os, json, shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from parsers.resume_parser import parse_resume
from ats.ats_scorer import score_against_all_jobs
from llm.llm_analyzer import analyze_top_matches

app = FastAPI(title="AI Resume Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR    = os.path.join(os.path.dirname(__file__), "..")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
SKILLS_PATH = os.path.join(BASE_DIR, "datasets", "skills_list.json")
JOBS_PATH   = os.path.join(BASE_DIR, "datasets", "all_jobs.csv")

os.makedirs(UPLOADS_DIR, exist_ok=True)

def load_skills():
    with open(SKILLS_PATH, encoding="utf-8") as f:
        return json.load(f)


# --- routes ---

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Resume Analyzer API"}


@app.get("/health")
def health():
    import pandas as pd
    df = pd.read_csv(JOBS_PATH)
    return {
        "status": "ok",
        "total_jobs": len(df),
        "skills_loaded": len(load_skills()),
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    top_n: int = 10,
    llm: bool = False,
):
    # validate file type
    if not file.filename.endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(400, "Unsupported file type. Use PDF, DOCX, or TXT.")

    # save uploaded file
    save_path = os.path.join(UPLOADS_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        skills = load_skills()

        # parse resume
        resume = parse_resume(save_path)
        if not resume.get("name") and not resume.get("raw_text"):
            raise HTTPException(400, "Could not parse resume. Check file format.")

        # ATS scoring
        top_jobs = score_against_all_jobs(resume, JOBS_PATH, skills, top_n=top_n)

        response = {
            "candidate": {
                "name":     resume.get("name"),
                "email":    resume.get("email"),
                "phone":    resume.get("phone"),
                "linkedin": resume.get("linkedin"),
                "github":   resume.get("github"),
                "skills":   resume.get("skills"),
            },
            "top_matches": top_jobs,
            "llm_analysis": None,
        }

        # optional LLM analysis
        if llm:
            analyses = analyze_top_matches(resume, top_jobs[:3], JOBS_PATH)
            response["llm_analysis"] = analyses

        return response

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        # clean up uploaded file
        if os.path.exists(save_path):
            os.remove(save_path)


@app.get("/jobs")
def get_jobs(
    company: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    import pandas as pd
    df = pd.read_csv(JOBS_PATH).fillna("")
    if company:
        df = df[df["company"].str.lower() == company.lower()]
    total = len(df)
    jobs = df.iloc[offset:offset+limit].to_dict("records")
    return {"total": total, "offset": offset, "limit": limit, "jobs": jobs}


@app.get("/jobs/companies")
def get_companies():
    import pandas as pd
    df = pd.read_csv(JOBS_PATH).fillna("")
    companies = df.groupby("company").size().reset_index(name="job_count")
    return {"companies": companies.to_dict("records")}


@app.get("/jobs/search")
def search_jobs(q: str, limit: int = 20):
    import pandas as pd
    df = pd.read_csv(JOBS_PATH).fillna("")
    mask = (
        df["title"].str.contains(q, case=False, na=False) |
        df["description"].str.contains(q, case=False, na=False) |
        df["company"].str.contains(q, case=False, na=False)
    )
    results = df[mask].head(limit).to_dict("records")
    return {"query": q, "count": len(results), "jobs": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)