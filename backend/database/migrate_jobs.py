import os, sys
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(__file__))

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.database.database import init_db, SessionLocal, Job

def migrate():
    print("Creating tables...")
    init_db()

    df = pd.read_csv("datasets/all_jobs.csv").fillna("")
    db = SessionLocal()

    existing = {j.apply_url for j in db.query(Job.apply_url).all()}
    print(f"Existing jobs in DB: {len(existing)}")

    new_jobs = []
    for _, row in df.iterrows():
        if row["apply_url"] in existing:
            continue
        new_jobs.append(Job(
            title=row.get("title","")[:500],
            company=row.get("company","")[:200],
            location=row.get("location","")[:300],
            department=row.get("department","")[:200],
            employment_type=row.get("employment_type","")[:100],
            description=row.get("description",""),
            apply_url=row.get("apply_url","")[:1000],
            source_url=row.get("source_url","")[:1000],
            posted_date=row.get("posted_date","")[:100],
        ))

    if new_jobs:
        db.bulk_save_objects(new_jobs)
        db.commit()
        print(f"Migrated {len(new_jobs)} jobs to PostgreSQL.")
    else:
        print("No new jobs to migrate.")

    db.close()

if __name__ == "__main__":
    migrate()