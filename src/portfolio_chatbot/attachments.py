from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from docx import Document
from pypdf import PdfReader

MAX_PDF_PAGES = 80
MAX_DOCX_UNCOMPRESSED_BYTES = 10_000_000
MAX_DOCX_ENTRIES = 2_000


def read_attachment_text(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension == ".txt":
        text = content.decode("utf-8")
    elif extension == ".pdf":
        reader = PdfReader(BytesIO(content))
        if len(reader.pages) > MAX_PDF_PAGES:
            raise ValueError(f"PDFs must have {MAX_PDF_PAGES} pages or fewer.")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif extension == ".docx":
        try:
            with ZipFile(BytesIO(content)) as archive:
                if len(archive.infolist()) > MAX_DOCX_ENTRIES:
                    raise ValueError("The Word document contains too many parts.")
                if sum(item.file_size for item in archive.infolist()) > MAX_DOCX_UNCOMPRESSED_BYTES:
                    raise ValueError("The Word document is too large to process safely.")
            document = Document(BytesIO(content))
        except BadZipFile as error:
            raise ValueError("This Word document is damaged or invalid.") from error
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    else:
        raise ValueError("Please upload a .txt, .pdf, or .docx file.")

    if not text.strip():
        raise ValueError("No readable text was found in the file.")

    return text.strip()
