from pathlib import Path
from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESUME_FOLDER = PROJECT_ROOT / "data" / "resume"
MAX_RESUME_BYTES = 5_000_000
MAX_RESUME_PAGES = 80
MAX_RESUME_TEXT_CHARS = 100_000


def find_resume_pdf() -> Path:
    pdf_files = list(RESUME_FOLDER.glob("*.pdf"))
    public_resume = RESUME_FOLDER / "public-resume.pdf"

    if public_resume in pdf_files:
        return public_resume

    if not pdf_files:
        raise FileNotFoundError(f"No PDF resume found in {RESUME_FOLDER}")

    if len(pdf_files) > 1:
        raise ValueError(f"Keep only one PDF resume in {RESUME_FOLDER}")

    return pdf_files[0]


def read_resume() -> str:
    resume_pdf = find_resume_pdf()

    if resume_pdf.stat().st_size > MAX_RESUME_BYTES:
        raise ValueError("The resume PDF must be 5 MB or smaller.")

    reader = PdfReader(resume_pdf)
    if len(reader.pages) > MAX_RESUME_PAGES:
        raise ValueError(f"The resume PDF must have {MAX_RESUME_PAGES} pages or fewer.")
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages)
    if len(text) > MAX_RESUME_TEXT_CHARS:
        raise ValueError("The extracted resume text must be 100,000 characters or less.")
    return text
