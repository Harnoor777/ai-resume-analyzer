# AI Resume Analyzer

An AI-powered Resume Analyzer that evaluates resumes against job descriptions using NLP, semantic similarity, and ATS scoring. Provides detailed feedback, skill gap analysis, keyword optimization, and improvement suggestions.

---

## Features

* Upload PDF and DOCX resumes
* Extract and clean resume text automatically
* Parse resume sections (Education, Experience, Skills, Projects, Certifications)
* Compare resume with job descriptions
* ATS compatibility scoring (0–100)
* Semantic similarity using Sentence Transformers
* Missing keyword and skill gap detection
* Resume improvement recommendations
* REST API with FastAPI
* Interactive API docs via Swagger and ReDoc

---

## Tech Stack

### Backend
* Python 3.11+
* FastAPI
* Uvicorn

### NLP & AI
* spaCy
* Sentence Transformers
* Scikit-learn
* NumPy
* Pandas

### Document Parsing
* PyMuPDF
* pdfplumber
* python-docx

---

## Project Structure

```text
ai-resume-analyzer/
│
├── backend/
│   ├── api/
│   ├── ats/
│   ├── database/
│   ├── embeddings/
│   ├── llm/
│   ├── models/
│   ├── parsers/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── config/
├── datasets/
├── docs/
│   ├── api.md
│   ├── architecture.md
│   ├── setup.md
│   └── workflow.md
├── frontend/
├── reports/
├── tests/
├── uploads/
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## Quickstart

See [docs/setup.md](docs/setup.md) for full setup instructions including environment variables and model downloads.

```bash
git clone https://github.com/<your-username>/ai-resume-analyzer.git
cd ai-resume-analyzer
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env         # then fill in your values
uvicorn backend.main:app --reload
```

API: `http://127.0.0.1:8000`
Swagger: `http://127.0.0.1:8000/docs`

---

## Roadmap

* [x] Resume Upload
* [x] Resume Parsing
* [ ] Skill Extraction
* [ ] ATS Scoring
* [ ] Semantic Matching
* [ ] Resume Recommendations
* [ ] Dashboard
* [ ] Authentication
* [ ] Deployment

*(Update checkboxes as features are completed.)*

---

## Future Enhancements

* GPT-powered resume rewriting
* Cover letter generation
* Interview question generation
* Company-specific ATS optimization
* Resume ranking
* Recruiter dashboard

---

## License

MIT License.