import os, json, shutil, sys
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

sys.path.append(os.path.dirname(__file__))

from parsers.resume_parser import parse_resume
from ats.ats_scorer import score_against_all_jobs
from llm.llm_analyzer import analyze_top_matches
from database.database import get_db, init_db, Job, Resume, Analysis, User
from auth.auth_routes import router as auth_router
from auth.auth import decode_token

app = FastAPI(title="AI Resume Analyzer", version="1.0.0")
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR    = os.path.dirname(__file__)
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "uploads")
SKILLS_PATH = os.path.join(BASE_DIR, "..", "datasets", "skills_list.json")
JOBS_PATH   = os.path.join(BASE_DIR, "..", "datasets", "all_jobs.csv")

os.makedirs(UPLOADS_DIR, exist_ok=True)

def load_skills():
    with open(SKILLS_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_optional_current_user(authorization: str = Header(None, alias="Authorization"), db: Session = Depends(get_db)):
    """Return User if authenticated, None otherwise (no 401 raised)"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ")[1]
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        user = db.query(User).filter(User.id == int(payload["sub"])).first()
        return user
    except:
        return None

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Resume Analyzer API"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    job_count = db.query(Job).count()
    return {
        "status": "ok",
        "total_jobs": job_count,
        "skills_loaded": len(load_skills()),
    }

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    top_n: int = 10,
    llm: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if not file.filename.endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(400, "Unsupported file type. Use PDF, DOCX, or TXT.")

    save_path = os.path.join(UPLOADS_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        skills = load_skills()
        resume = parse_resume(save_path)
        if not resume.get("raw_text"):
            raise HTTPException(400, "Could not parse resume.")

        db_resume = Resume(
            user_id=current_user.id if current_user else None,
            file_name=file.filename,
            name=resume.get("name",""),
            email=resume.get("email",""),
            phone=resume.get("phone",""),
            linkedin=resume.get("linkedin",""),
            github=resume.get("github",""),
            skills=resume.get("skills",[]),
            raw_text=resume.get("raw_text","")[:50000],
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        top_jobs = score_against_all_jobs(resume, JOBS_PATH, skills, top_n=top_n)

        for job in top_jobs:
            db_analysis = Analysis(
                resume_id=db_resume.id,
                job_title=job.get("job_title",""),
                job_company=job.get("job_company",""),
                apply_url=job.get("apply_url",""),
                final_score=job.get("final_score",0),
                grade=job.get("grade",""),
                matched_skills=job.get("keyword_match",{}).get("matched",[]),
                missing_skills=job.get("keyword_match",{}).get("missing",[]),
                semantic_score=job.get("semantic_score",0),
            )
            db.add(db_analysis)
        db.commit()

        response = {
            "resume_id": db_resume.id,
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

        if llm:
            analyses = analyze_top_matches(resume, top_jobs[:3], JOBS_PATH)
            response["llm_analysis"] = analyses

        return response

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

@app.get("/jobs")
def get_jobs(
    company: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if company:
        query = query.filter(Job.company.ilike(company))
    total = query.count()
    jobs  = query.offset(offset).limit(limit).all()
    return {
        "total": total, "offset": offset, "limit": limit,
        "jobs": [{"id": j.id, "title": j.title, "company": j.company,
                  "location": j.location, "apply_url": j.apply_url} for j in jobs]
    }

@app.get("/jobs/companies")
def get_companies(db: Session = Depends(get_db)):
    from sqlalchemy import func
    rows = db.query(Job.company, func.count(Job.id).label("job_count"))\
             .group_by(Job.company).order_by(func.count(Job.id).desc()).all()
    return {"companies": [{"company": r.company, "job_count": r.job_count} for r in rows]}

@app.get("/jobs/search")
def search_jobs(q: str, limit: int = 20, db: Session = Depends(get_db)):
    results = db.query(Job).filter(
        Job.title.ilike(f"%{q}%") |
        Job.description.ilike(f"%{q}%") |
        Job.company.ilike(f"%{q}%")
    ).limit(limit).all()
    return {
        "query": q, "count": len(results),
        "jobs": [{"id": j.id, "title": j.title, "company": j.company,
                  "location": j.location, "apply_url": j.apply_url} for j in results]
    }

@app.get("/resumes")
def get_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).all()
    return {"resumes": [{"id": r.id, "name": r.name, "email": r.email,
                         "skills": r.skills, "created_at": str(r.created_at)} for r in resumes]}

@app.get("/resumes/{resume_id}/analyses")
def get_analyses(resume_id: int, db: Session = Depends(get_db)):
    analyses = db.query(Analysis).filter(Analysis.resume_id == resume_id).all()
    if not analyses:
        raise HTTPException(404, "No analyses found for this resume.")
    return {"resume_id": resume_id, "analyses": [
        {"job_title": a.job_title, "job_company": a.job_company,
         "final_score": a.final_score, "grade": a.grade,
         "matched_skills": a.matched_skills, "missing_skills": a.missing_skills,
         "apply_url": a.apply_url} for a in analyses
    ]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)