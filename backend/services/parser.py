import re
import os
from typing import Optional
import pdfplumber
from docx import Document as DocxDocument


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX."""
    text = ""
    try:
        doc = DocxDocument(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
                text += "\n"
    except Exception as e:
        print(f"DOCX extraction error: {e}")
    return text.strip()


def extract_text(file_path: str, file_type: str) -> str:
    """Route to correct extractor."""
    if file_type in ["pdf", "application/pdf"]:
        return extract_text_from_pdf(file_path)
    elif file_type in ["docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        return extract_text_from_docx(file_path)
    elif file_type in ["txt", "text/plain"]:
        with open(file_path, "r", errors="ignore") as f:
            return f.read()
    return ""


# ── Pattern-based extractors ─────────────────────────────────────────────────

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-().]{7,15}\d)")
YEARS_EXP_RE = re.compile(r"(\d+\.?\d*)\s*\+?\s*years?\s+(?:of\s+)?(?:experience|exp)", re.IGNORECASE)

TECH_SKILLS = {
    "languages": ["python", "java", "javascript", "typescript", "go", "rust", "c++", "c#", "ruby", "php", "scala", "kotlin", "swift", "r"],
    "frameworks": ["django", "fastapi", "flask", "spring", "react", "angular", "vue", "node.js", "express", "laravel", "rails", "nextjs", "nestjs"],
    "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "sqlite", "oracle", "mssql", "neo4j", "clickhouse"],
    "cloud": ["aws", "gcp", "azure", "ec2", "s3", "lambda", "rds", "cloudfront", "gke", "aks"],
    "devops": ["docker", "kubernetes", "k8s", "jenkins", "github actions", "gitlab ci", "terraform", "ansible", "helm", "argocd"],
    "ml": ["tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "huggingface", "langchain", "openai", "mlflow", "airflow"],
    "tools": ["git", "linux", "kafka", "rabbitmq", "graphql", "rest api", "grpc", "celery", "nginx", "prometheus", "grafana"],
}

ALL_SKILLS = []
for category in TECH_SKILLS.values():
    ALL_SKILLS.extend(category)

EDUCATION_KEYWORDS = {
    "phd": ["phd", "ph.d", "doctorate", "doctor of"],
    "masters": ["m.tech", "m.s.", "msc", "m.e.", "mba", "master of", "masters"],
    "bachelors": ["b.tech", "b.e.", "b.sc", "b.s.", "bachelor of", "bachelors", "undergraduate", "b.a."],
    "diploma": ["diploma", "polytechnic"],
}

PREMIUM_INSTITUTES = ["iit", "iim", "nit", "bits pilani", "mit", "stanford", "oxford", "cambridge", "harvard", "cmu"]


def extract_email(text: str) -> Optional[str]:
    matches = EMAIL_RE.findall(text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    matches = PHONE_RE.findall(text)
    return matches[0].strip() if matches else None


def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in ALL_SKILLS:
        # word boundary check
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return list(set(found))


def extract_years_experience(text: str) -> float:
    matches = YEARS_EXP_RE.findall(text)
    if matches:
        return float(matches[0])
    # fallback: count job entries duration
    return 0.0


def extract_education(text: str) -> dict:
    text_lower = text.lower()
    level = "unknown"
    institution = ""

    for lvl, keywords in EDUCATION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                level = lvl
                break

    for inst in PREMIUM_INSTITUTES:
        if inst in text_lower:
            institution = inst.upper()
            break

    if not institution:
        # try to extract via pattern
        edu_pattern = re.search(r"(?:from|at|,\s*)([A-Z][A-Za-z\s]{3,40}(?:University|College|Institute|School|IIT|NIT|BITS))", text)
        if edu_pattern:
            institution = edu_pattern.group(1).strip()

    return {"level": level, "institution": institution}


def extract_name(text: str) -> str:
    """Heuristic: first non-empty line often has name."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        first = lines[0]
        # Filter out lines that look like headers
        if len(first.split()) <= 5 and not any(c in first for c in ["@", "http", "+91", "linkedin"]):
            return first
    return "Unknown"


def extract_work_experience(text: str) -> list:
    """Extract work experience blocks."""
    experience = []
    
    # Common company patterns
    company_pattern = re.compile(
        r"(?:at|@|•|\|)?\s*([A-Z][A-Za-z\s&.,]+(?:Inc|Ltd|Pvt|Corp|Technologies|Solutions|Systems|Labs|Software|Services)?)"
        r"\s*[|·•–-]\s*"
        r"([A-Za-z\s]+(?:Engineer|Developer|Manager|Analyst|Designer|Architect|Lead|Senior|Junior|Intern)?)",
        re.MULTILINE
    )
    
    date_pattern = re.compile(
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})"
        r"\s*[-–to]+\s*"
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current|Now)",
        re.IGNORECASE
    )
    
    dates = date_pattern.findall(text)
    for start, end in dates[:5]:  # max 5 jobs
        experience.append({
            "start_date": start,
            "end_date": end,
            "is_current": end.lower() in ["present", "current", "now"],
        })
    
    return experience


def detect_keyword_stuffing(text: str) -> bool:
    """Flag resumes with excessive skill keyword density."""
    found_skills = extract_skills(text)
    word_count = len(text.split())
    if word_count == 0:
        return False
    density = len(found_skills) / max(word_count / 100, 1)
    return density > 15 or len(found_skills) > 80


def detect_duplicate(text: str, existing_texts: list) -> bool:
    """Simple similarity check for duplicate detection."""
    if not existing_texts:
        return False
    
    # Get email as primary key
    email = extract_email(text)
    if email:
        for existing in existing_texts:
            if extract_email(existing) == email:
                return True
    
    # Rough text overlap
    words = set(text.lower().split())
    for existing in existing_texts:
        existing_words = set(existing.lower().split())
        if len(words) == 0 or len(existing_words) == 0:
            continue
        overlap = len(words & existing_words) / len(words | existing_words)
        if overlap > 0.85:
            return True
    return False


def parse_resume(text: str, job_required_skills: list = None) -> dict:
    """Full parse pipeline."""
    skills = extract_skills(text)
    education = extract_education(text)
    work_exp = extract_work_experience(text)
    years_exp = extract_years_experience(text)
    
    # Infer years from work blocks if direct mention absent
    if years_exp == 0 and work_exp:
        years_exp = len(work_exp) * 1.5  # rough estimate
    
    return {
        "full_name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": skills,
        "years_experience": years_exp,
        "education_level": education["level"],
        "education_institution": education["institution"],
        "work_experience": work_exp,
        "is_flagged": detect_keyword_stuffing(text),
        "flag_reason": "Suspected keyword stuffing" if detect_keyword_stuffing(text) else None,
    }
