# API Documentation

## Base URL
http://127.0.0.1:8000

---

## Endpoints

### GET /

Health check.

**Response**
```json
{
  "message": "AI Resume Analyzer API is running!"
}
```

---

### GET /health

Returns API status.

**Response**
```json
{
  "status": "healthy"
}
```

---

### POST /upload

Uploads a resume file for text extraction.

**Request**

Content-Type: `multipart/form-data`

| Field  | Type | Required | Description           |
|--------|------|----------|-----------------------|
| `file` | File | Yes      | PDF or DOCX resume    |

**Response 200**
```json
{
  "filename": "resume.pdf",
  "text": "John Doe\nSoftware Engineer\n..."
}
```

**Error Responses**

| Code | Reason                        |
|------|-------------------------------|
| 400  | Unsupported file type         |
| 422  | Missing file field            |
| 500  | Text extraction failed        |

---

### POST /parse

Parses structured sections from extracted resume text.

**Request**

Content-Type: `application/json`

```json
{
  "text": "John Doe\nSkills: Python, FastAPI..."
}
```

**Response 200**
```json
{
  "skills": ["Python", "FastAPI", "SQL"],
  "education": ["B.Tech Computer Science, XYZ University, 2022"],
  "experience": ["Software Engineer at ABC Corp, 2022–2024"],
  "projects": ["Resume Analyzer — Python, FastAPI, spaCy"],
  "certifications": ["AWS Certified Developer"]
}
```

**Error Responses**

| Code | Reason              |
|------|---------------------|
| 400  | Empty or null text  |
| 500  | Parsing failed      |

---

### POST /match

Compares a resume against a job description and returns similarity and ATS scores.

**Request**

Content-Type: `application/json`

```json
{
  "resume_text": "John Doe\nSkills: Python, FastAPI...",
  "job_description": "We are looking for a Python developer with FastAPI and Docker experience..."
}
```

**Response 200**
```json
{
  "similarity": 0.91,
  "ats_score": 84,
  "matched_skills": ["Python", "FastAPI", "REST APIs"],
  "missing_skills": ["Docker", "AWS"],
  "missing_keywords": ["CI/CD", "microservices"]
}
```

**Error Responses**

| Code | Reason                              |
|------|-------------------------------------|
| 400  | Missing resume_text or job_description |
| 500  | Embedding or scoring failed         |

---

### POST /recommend

Generates resume improvement suggestions based on a prior match result.

**Request**

Content-Type: `application/json`

```json
{
  "missing_skills": ["Docker", "AWS"],
  "missing_keywords": ["CI/CD", "microservices"],
  "ats_score": 84
}
```

**Response 200**
```json
{
  "recommendations": [
    "Add Docker or containerization experience to your projects section",
    "Mention cloud platform experience (AWS or GCP)",
    "Include CI/CD pipeline tools such as GitHub Actions or Jenkins",
    "Add measurable achievements to your experience section"
  ]
}
```

**Error Responses**

| Code | Reason                    |
|------|---------------------------|
| 400  | Missing required fields   |
| 500  | Recommendation failed     |

---

## Interactive Documentation

Start the server, then open:

| Tool    | URL                              |
|---------|----------------------------------|
| Swagger | http://127.0.0.1:8000/docs       |
| ReDoc   | http://127.0.0.1:8000/redoc      |


