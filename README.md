# AI Resume Analyzer

An AI-powered Resume Analyzer that matches your resume against 3000+ real job listings using NLP, semantic similarity, and ATS scoring. Provides job matches, skill gap analysis, and LLM-generated feedback.

---

## Features

- Upload PDF and DOCX resumes
- Scrape live jobs from Greenhouse, Lever, Ashby, Workable
- Extract and clean resume text automatically
- Parse resume sections (Education, Experience, Skills, Summary)
- ATS compatibility scoring (0–100) using keyword + weighted + semantic scoring
- FAISS vector search — results in under 5 seconds
- LLM analysis via Groq — match analysis, skills advice, cover letter generation
- Pinterest-style frontend with dark/light mode
- REST API with FastAPI + Swagger docs

---

## Tech Stack

### Backend
- Python 3.11+
- FastAPI, Uvicorn

### NLP & AI
- Sentence Transformers (`all-MiniLM-L6-v2`)
- FAISS (vector search)
- Groq API (Llama 3.3 70B)
- Scikit-learn, NumPy, Pandas

### Document Parsing
- pdfplumber
- python-docx

### Scraping
- Playwright

---

## Project Structure

```text
ai-resume-analyzer/
│
├── backend/
│   ├── ats/
│   │   └── ats_scorer.py          # ATS scoring engine
│   ├── embeddings/
│   │   └── build_index.py         # FAISS index builder
│   ├── llm/
│   │   └── llm_analyzer.py        # Groq LLM analysis
│   ├── parsers/
│   │   └── resume_parser.py       # PDF/DOCX parser
│   ├── services/
│   │   ├── scrape_jobs.py         # Job scraper
│   │   └── clean_jobs.py          # Data cleaner
│   ├── utils/
│   │   └── build_skills_list.py   # Skills extractor
│   └── main.py                    # FastAPI server
│
├── config/
├── datasets/
│   ├── all_jobs.csv               # Scraped job listings
│   ├── skills_list.json           # Extracted skills
│   ├── faiss_index.bin            # FAISS vector index
│   └── faiss_meta.json            # Job metadata
├── docs/
│   ├── api.md
│   ├── architecture.md
│   ├── setup.md
│   └── workflow.md
├── frontend/
│   └── index.html                 # Pinterest-style UI
├── reports/                       # LLM analysis output
├── tests/
├── uploads/                       # Temp resume uploads
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Clone and setup

```bash
git clone https://github.com/<your-username>/ai-resume-analyzer.git
cd ai-resume-analyzer
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
playwright install chromium
```

### 2. Environment variables

```bash
cp .env.example .env
```

Add to `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com)

### 3. Scrape jobs

```bash
python backend/services/scrape_jobs.py https://job-boards.greenhouse.io/anthropic
python backend/services/scrape_jobs.py https://job-boards.greenhouse.io/stripe
python backend/services/scrape_jobs.py https://jobs.ashbyhq.com/openai
```

### 4. Clean data and build skills

```bash
python backend/services/clean_jobs.py
python backend/utils/build_skills_list.py
```

### 5. Build FAISS index (once)

```bash
python backend/embeddings/build_index.py
```

### 6. Start the API

```bash
python backend/main.py
```

API: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`

### 7. Start the frontend

```bash
cd frontend
python -m http.server 3000
```

Open `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API + job count |
| POST | `/analyze` | Upload resume → get matches |
| GET | `/jobs` | Browse all jobs |
| GET | `/jobs/companies` | List companies |
| GET | `/jobs/search?q=python` | Search jobs by keyword |

---

## Roadmap

- [x] Job Scraper (Greenhouse, Lever, Ashby, Workable)
- [x] Resume Parsing (PDF + DOCX)
- [x] Skills Extraction (from real job data)
- [x] ATS Scoring (keyword + weighted + semantic)
- [x] FAISS Vector Search
- [x] LLM Analysis (Groq + Llama 3.3)
- [x] REST API (FastAPI)
- [x] Frontend (Pinterest-style, dark/light)
- [ ] Authentication
- [ ] User dashboard
- [ ] Deployment

---

## Future Enhancements

- GPT-powered resume rewriting
- Interview question generation
- Company-specific ATS optimization
- Recruiter dashboard
- Mobile app

---

## License

MIT License.