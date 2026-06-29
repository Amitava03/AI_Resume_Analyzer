import re
from pathlib import Path

from docx import Document
from pypdf import PdfReader


SECTION_PATTERNS = {
    "education": r"\b(education|academic|qualification)\b",
    "experience": r"\b(experience|employment|work history|professional experience)\b",
    "skills": r"\b(skills|technical skills|core competencies|competencies)\b",
    "projects": r"\b(projects|portfolio)\b",
    "certifications": r"\b(certifications?|licenses?)\b",
}


def extract_text_from_file(file_path: str | Path) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf_text(path)
    if suffix in {".docx", ".doc"}:
        return _extract_docx_text(path)
    raise ValueError("Unsupported file format. Upload PDF or DOCX only.")


def _extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def _extract_docx_text(path: Path) -> str:
    document = Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()


def parse_sections(text: str) -> dict[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections: dict[str, list[str]] = {"general": []}
    current = "general"

    for line in lines:
        lowered = line.lower()
        matched = False
        for section, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, lowered) and len(line.split()) <= 5:
                current = section
                sections.setdefault(section, [])
                matched = True
                break
        if not matched:
            sections.setdefault(current, [])
            sections[current].append(line)

    return {name: "\n".join(content).strip() for name, content in sections.items() if content}


def extract_skills(text: str) -> list[str]:
    skill_candidates = re.findall(
        r"\b(Python|Java|JavaScript|TypeScript|Django|React|SQL|AWS|Docker|"
        r"Kubernetes|Git|HTML|CSS|Node\.js|C\+\+|C#|Machine Learning|NLP|"
        r"Leadership|Communication|Agile|Scrum|REST|API|PostgreSQL|MongoDB|"
        r"TensorFlow|PyTorch|Excel|Power BI|Linux|Azure|GCP)\b",
        text,
        flags=re.IGNORECASE,
    )
    normalized = sorted({skill.title() for skill in skill_candidates})
    return normalized
