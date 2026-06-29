import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"
    id              = Column(Integer, primary_key=True, index=True)
    title           = Column(String(500), nullable=False)
    company         = Column(String(200))
    location        = Column(String(300))
    department      = Column(String(200))
    employment_type = Column(String(100))
    description     = Column(Text)
    apply_url       = Column(String(1000), unique=True, index=True)
    source_url      = Column(String(1000))
    posted_date     = Column(String(100))
    created_at      = Column(DateTime, default=datetime.utcnow)


class Resume(Base):
    __tablename__ = "resumes"
    id          = Column(Integer, primary_key=True, index=True)
    file_name   = Column(String(500))
    name        = Column(String(300))
    email       = Column(String(300))
    phone       = Column(String(100))
    linkedin    = Column(String(500))
    github      = Column(String(500))
    skills      = Column(JSON)
    raw_text    = Column(Text)
    created_at  = Column(DateTime, default=datetime.utcnow)
    analyses    = relationship("Analysis", back_populates="resume")


class Analysis(Base):
    __tablename__ = "analyses"
    id            = Column(Integer, primary_key=True, index=True)
    resume_id     = Column(Integer, ForeignKey("resumes.id"))
    job_title     = Column(String(500))
    job_company   = Column(String(200))
    apply_url     = Column(String(1000))
    final_score   = Column(Float)
    grade         = Column(String(5))
    matched_skills = Column(JSON)
    missing_skills = Column(JSON)
    semantic_score = Column(Float)
    llm_analysis  = Column(JSON, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    resume        = relationship("Resume", back_populates="analyses")


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()