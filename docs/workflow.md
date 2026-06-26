# Workflow

## Full Pipeline

User Uploads Resume (PDF or DOCX)

│

▼

Store file in uploads/

│

▼

Extract raw text

(PyMuPDF / pdfplumber / python-docx)

│

▼

Clean text

(strip noise, normalize whitespace)

│

▼

Parse resume sections

(spaCy NER + header detection)

│

▼

Extract skills and entities

│

▼

User submits Job Description text

│

▼

Generate embeddings

(Sentence Transformers — resume + JD)

│

▼

Calculate cosine similarity

│

▼

Calculate ATS score

(weighted metrics)

│

▼

Generate recommendations

│

▼

Return JSON response
---

## Step-by-Step Details

### Step 1 — Receive File

User uploads a PDF or DOCX via `POST /upload`. File is saved temporarily to `uploads/`.

### Step 2 — Extract Text

Depending on file type:
* PDF → PyMuPDF (fast) or pdfplumber (layout-aware)
* DOCX → python-docx paragraph extraction

Output: raw text string.

### Step 3 — Clean Text

Regex-based cleaning removes headers, footers, extra line breaks, and non-ASCII characters. Text is lowercased and whitespace is normalized.

### Step 4 — Parse Resume Sections

spaCy pipeline runs tokenization, lemmatization, and NER. Section boundaries are detected using common heading keywords (e.g., "Education", "Experience", "Skills"). Each section's text is extracted separately.

### Step 5 — Extract Skills and Entities

A predefined skills vocabulary is matched against the parsed skills section. Named entities (organizations, dates, locations) are extracted for experience and education sections.

### Step 6 — Parse Job Description

The user submits a job description string (plain text). The same cleaning pipeline is applied. Keywords and required skills are extracted.

### Step 7 — Generate Embeddings

`all-MiniLM-L6-v2` from Sentence Transformers encodes both the cleaned resume text and the job description text into 384-dimensional vectors.

### Step 8 — Calculate Similarity

Cosine similarity is computed between the two vectors using scikit-learn. Result is a float between 0 (no match) and 1 (perfect match).

### Step 9 — Calculate ATS Score

Weighted scoring across keyword match, skill match, experience match, education match, completeness, and contact info. Final score is 0–100.

### Step 10 — Generate Recommendations and Return Response

Missing skills and keywords are identified by diffing extracted resume content against the JD. Suggestions are generated. Full JSON response is returned.

---

## Example Output

```json
{
  "ats_score": 84,
  "similarity": 0.91,
  "matched_skills": ["Python", "FastAPI", "REST APIs", "Git"],
  "missing_skills": ["Docker", "AWS"],
  "missing_keywords": ["CI/CD", "microservices"],
  "recommendations": [
    "Add cloud platform experience (AWS or GCP)",
    "Mention Docker or containerization in your projects",
    "Include measurable achievements in your experience section",
    "Add CI/CD pipeline experience"
  ]
}
```
