# System Architecture

## Goal

An AI-powered Resume Analyzer that parses resumes, understands job descriptions, calculates ATS compatibility, identifies skill gaps, and provides actionable recommendations.

---

## High-Level Architecture

User Request

│

▼

FastAPI Layer (REST API)

│

├──► Document Parser        → Extracts raw text from PDF/DOCX

│

├──► Text Cleaner           → Removes noise, normalizes whitespace

│

├──► Resume Parser          → Identifies sections and entities

│         ├── Skills

│         ├── Education

│         ├── Experience

│         ├── Projects

│         └── Certifications

│

├──► Embedding Engine       → Generates vectors via Sentence Transformers

│

├──► Similarity Engine      → Cosine similarity between resume and JD

│

├──► ATS Scoring Engine     → Weighted scoring across multiple metrics

│

└──► Recommendation Engine  → Generates improvement suggestions

│

▼

JSON Response


---

## Module Descriptions

### Document Parser (`backend/parsers/`)

Accepts PDF and DOCX files uploaded via the API. Extracts raw text using PyMuPDF or pdfplumber for PDFs and python-docx for DOCX. Returns a plain text string for downstream processing.

Supported formats: PDF, DOCX

### Text Cleaner (`backend/utils/`)

Receives raw extracted text and removes unwanted characters, extra whitespace, and formatting artifacts. Normalizes text to a consistent format before NLP processing.

### Resume Parser (`backend/parsers/`)

Runs the cleaned text through a spaCy NLP pipeline to identify and extract structured sections.

Pipeline steps:
* Tokenization
* Lemmatization
* Named Entity Recognition (NER)
* Section boundary detection using header keywords
* Keyword extraction per section

Outputs a structured dictionary with keys: `skills`, `education`, `experience`, `projects`, `certifications`.

### Embedding Engine (`backend/embeddings/`)

Uses the `all-MiniLM-L6-v2` Sentence Transformer model to convert resume text and job description text into dense vector embeddings. Both are generated independently and passed to the Similarity Engine.

### Similarity Engine (`backend/services/`)

Computes cosine similarity between the resume embedding and the job description embedding using scikit-learn. Returns a float score between 0 and 1.

### ATS Scoring Engine (`backend/ats/`)

Calculates a weighted ATS score (0–100) across the following metrics:

| Metric               | Weight |
|----------------------|--------|
| Keyword Match        | 30%    |
| Skill Match          | 25%    |
| Experience Match     | 20%    |
| Education Match      | 10%    |
| Resume Completeness  | 10%    |
| Contact Information  | 5%     |

### Recommendation Engine (`backend/services/`)

Compares extracted resume skills and keywords against the job description. Produces:
* List of missing skills
* List of missing keywords
* Actionable improvement suggestions

### REST API (`backend/api/`)

Built with FastAPI. Exposes endpoints for upload, parse, match, and recommend. All responses are JSON. See `docs/api.md` for full endpoint reference.

---

## Data Flow Between Modules

Document Parser

│ raw text

▼

Text Cleaner

│ clean text

├──────────────────────────────┐

▼                              ▼

Resume Parser               Embedding Engine

│ structured data             │ resume vector

▼                             │

ATS Scoring Engine ◄────────────────┤

│                             │ JD vector

│                    Embedding Engine (JD)

▼                             │

Recommendation Engine               ▼

│                    Similarity Engine

└──────────────────────────────┘

│

▼

JSON Response

---

## Storage

| Resource        | Location          | Notes                            |
|-----------------|-------------------|----------------------------------|
| Uploaded files  | `uploads/`        | Temporary; cleared after parsing |
| Config/env vars | `config/` + `.env`| See docs/setup.md                |
| Reports         | `reports/`        | Optional saved output            |

---

## Technology Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| API         | FastAPI, Uvicorn                  |
| NLP         | spaCy, Sentence Transformers      |
| ML          | Scikit-learn, NumPy, Pandas       |
| Parsing     | PyMuPDF, pdfplumber, python-docx  |
| Language    | Python 3.11+                      |

---

## Future Extensions

* GPT-based resume rewriting via LLM module (`backend/llm/`)
* Database integration (`backend/database/`) for storing results
* Cover letter and interview prep generation
* Multi-language resume support
* Recruiter dashboard with analytics