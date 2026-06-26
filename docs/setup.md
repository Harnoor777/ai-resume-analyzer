# Setup Guide

## Prerequisites

* Python 3.11 or higher
* Git
* pip

---

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/ai-resume-analyzer.git
cd ai-resume-analyzer
```

---

## 2. Create and Activate Virtual Environment

Windows
```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS
```bash
python -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Download spaCy Model

This step is required and easy to miss.

```bash
python -m spacy download en_core_web_sm
```

---

## 5. Configure Environment Variables

Copy the example env file and fill in your values.

```bash
copy .env.example .env
```

`.env.example` contains:
APP_ENV=development

UPLOAD_DIR=uploads/

MAX_FILE_SIZE_MB=5

ALLOWED_EXTENSIONS=pdf,docx

All variables and their purpose:

| Variable             | Default        | Description                            |
|----------------------|----------------|----------------------------------------|
| `APP_ENV`            | `development`  | Environment: development or production |
| `UPLOAD_DIR`         | `uploads/`     | Directory where uploads are stored     |
| `MAX_FILE_SIZE_MB`   | `5`            | Maximum allowed upload size in MB      |
| `ALLOWED_EXTENSIONS` | `pdf,docx`     | Comma-separated list of accepted types |

---

## 6. Run the Server

```bash
uvicorn backend.main:app --reload
```

API: `http://127.0.0.1:8000`
Swagger: `http://127.0.0.1:8000/docs`

---

## Config Directory

The `config/` directory holds any static configuration files (e.g., skills vocabulary list, scoring weights). These are loaded at startup and are separate from `.env` secrets.

---

## Common Issues

**spaCy model not found**
Run `python -m spacy download en_core_web_sm` — this is a separate step from pip install.

**File upload fails**
Check that the `uploads/` directory exists. Create it manually if needed: `mkdir uploads`

**Port already in use**
Run on a different port: `uvicorn backend.main:app --reload --port 8001`