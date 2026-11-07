from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


def read_attachment_text(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension == ".txt":
        text = content.decode("utf-8")
    elif extension == ".pdf":
        reader = PdfReader(BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif extension == ".docx":
        document = Document(BytesIO(content))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    else:
        raise ValueError("Please upload a .txt, .pdf, or .docx file.")

    if not text.strip():
        raise ValueError("No readable text was found in the file.")

    return text.strip()
