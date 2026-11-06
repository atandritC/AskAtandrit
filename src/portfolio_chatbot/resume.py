from pathlib import Path
from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESUME_FOLDER = PROJECT_ROOT / "data" / "resume"


def read_resume() -> str:
    pdf_files = list(RESUME_FOLDER.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF resume found in {RESUME_FOLDER}")

    if len(pdf_files) > 1:
        raise ValueError(f"Keep only one PDF resume in {RESUME_FOLDER}")

    reader = PdfReader(pdf_files[0])
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)
