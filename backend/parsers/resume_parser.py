import os, re, json
from pathlib import Path
import json, os

# PDF
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# DOCX
try:
    from docx import Document
except ImportError:
    Document = None


def extract_text_pdf(path: str) -> str:
    if not pdfplumber:
        raise ImportError("pip install pdfplumber")
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    return text.strip()


def extract_text_docx(path: str) -> str:
    if not Document:
        raise ImportError("pip install python-docx")
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return extract_text_pdf(path)
    elif ext in (".docx", ".doc"):
        return extract_text_docx(path)
    elif ext == ".txt":
        return open(path, encoding="utf-8").read()
    else:
        raise ValueError(f"Unsupported format: {ext}")


# --- Structured extraction (regex-based, no LLM needed) ---

_skills_path = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "skills_list.json")
SKILL_KEYWORDS = json.load(open(_skills_path, encoding="utf-8"))

def extract_email(text):
    m = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    return m.group() if m else ""

def extract_phone(text):
    m = re.search(r'(\+?\d[\d\s\-().]{7,}\d)', text)
    return m.group().strip() if m else ""

def extract_name(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        if len(line.split()) in (2, 3) and not any(c in line for c in ["@","http","."]):
            return line
    return ""

def extract_skills(text):
    text_lower = text.lower()
    return [s for s in SKILL_KEYWORDS if re.search(r'\b' + re.escape(s) + r'\b', text_lower)]

def extract_section(text, headers):
    pattern = r'(?i)(?:^|\n)(' + '|'.join(re.escape(h) for h in headers) + r')[:\s]*\n(.*?)(?=\n[A-Z][A-Z\s]{2,}:|\Z)'
    m = re.search(pattern, text, re.DOTALL)
    return m.group(2).strip() if m else ""

def extract_links(text):
    return re.findall(r'https?://[^\s,)>]+', text)

def parse_resume(path: str) -> dict:
    raw_text = extract_text(path)
    links = extract_links(raw_text)
    linkedin = next((l for l in links if "linkedin.com" in l), "")
    github = next((l for l in links if "github.com" in l), "")

    return {
        "raw_text": raw_text,
        "name": extract_name(raw_text),
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
        "linkedin": linkedin,
        "github": github,
        "skills": extract_skills(raw_text),
        "experience_section": extract_section(raw_text, ["experience","work experience","employment"]),
        "education_section": extract_section(raw_text, ["education","academic","qualifications"]),
        "summary_section": extract_section(raw_text, ["summary","objective","profile","about"]),
        "file_name": Path(path).name,
        "file_type": Path(path).suffix.lower(),
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: python resume_parser.py path/to/resume.pdf")
        exit(1)
    result = parse_resume(path)
    result_display = {k: v for k, v in result.items() if k != "raw_text"}
    print(json.dumps(result_display, indent=2))