import asyncio
from functools import lru_cache
from pathlib import Path
from threading import BoundedSemaphore
from typing import Annotated, Literal

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, ValidationError
from starlette.staticfiles import StaticFiles

from portfolio_chatbot.chat import ask_candidate, client
from portfolio_chatbot.attachments import read_attachment_text
from portfolio_chatbot.profile import CandidateProfile
from portfolio_chatbot.profile_parser import parse_candidate_profile
from portfolio_chatbot.resume import find_resume_pdf

app = FastAPI(title="Ask.Atandrit")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

# Keep multipart requests below Vercel's 4.5 MB function request-body limit.
MAX_REQUEST_BYTES = 4_000_000
MAX_FILES = 3
MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_FILE_BYTES = 2_500_000
MAX_FILE_TEXT_CHARS = 30_000
MAX_TOTAL_FILE_TEXT_CHARS = 40_000
MAX_MESSAGES = 20
MAX_MESSAGE_CHARS = 4_000
MAX_CONVERSATION_CHARS = 40_000
CHAT_CONCURRENCY = BoundedSemaphore(value=3)


@app.middleware("http")
async def limit_chat_request_size(request: Request, call_next):
    if request.url.path == "/chat":
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                too_large = int(content_length) > MAX_REQUEST_BYTES
            except ValueError:
                too_large = True
            if too_large:
                response = JSONResponse(
                    {"detail": "Request is too large. Keep the total upload under 4 MB."},
                    status_code=413,
                )
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                response.headers["X-Frame-Options"] = "DENY"
                return response

    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Frame-Options", "DENY")
    return response


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/resume", response_class=FileResponse)
def download_resume() -> FileResponse:
    try:
        resume_pdf = find_resume_pdf()
    except (FileNotFoundError, ValueError):
        raise HTTPException(
            status_code=404,
            detail="The candidate resume is not available.",
        )
    return FileResponse(
        resume_pdf,
        media_type="application/pdf",
        filename="Atandrit-Resume.pdf",
    )


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=MAX_MESSAGE_CHARS)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=MAX_MESSAGES)


@lru_cache(maxsize=1)
def get_candidate_profile() -> CandidateProfile:
    return parse_candidate_profile(client)


@app.post("/chat")
async def receive_chat_message(
    messages_json: Annotated[str, Form()],
    attachments: Annotated[list[UploadFile] | None, File()] = None,
) -> StreamingResponse:
    try:
        request = ChatRequest.model_validate_json(messages_json)
    except ValidationError as error:
        raise HTTPException(status_code=422, detail="Invalid chat request or message limits exceeded.") from error

    conversation_chars = sum(len(message.content) for message in request.messages)
    if conversation_chars > MAX_CONVERSATION_CHARS:
        raise HTTPException(status_code=413, detail="Conversation is too long. Start a new conversation.")

    if attachments and len(attachments) > MAX_FILES:
        raise HTTPException(status_code=413, detail=f"Attach no more than {MAX_FILES} files at a time.")

    if not CHAT_CONCURRENCY.acquire(blocking=False):
        raise HTTPException(
            status_code=503,
            detail="The chat service is busy. Please try again shortly.",
            headers={"Retry-After": "10"},
        )

    conversation = [message.model_dump() for message in request.messages]
    attachment_context = []
    total_file_bytes = 0
    total_file_text_chars = 0

    try:
        for attachment in attachments or []:
            filename = attachment.filename or "uploaded file"
            file_size = attachment.size or 0
            if file_size > MAX_FILE_BYTES:
                raise HTTPException(status_code=413, detail=f"{filename}: each file must be 1 MB or smaller.")
            content = await attachment.read(MAX_FILE_BYTES + 1)
            if len(content) > MAX_FILE_BYTES:
                raise HTTPException(status_code=413, detail=f"{filename}: each file must be 1 MB or smaller.")
            total_file_bytes += len(content)
            if total_file_bytes > MAX_TOTAL_FILE_BYTES:
                raise HTTPException(status_code=413, detail="Keep all attached files together under 2.5 MB.")

            try:
                text = await asyncio.to_thread(read_attachment_text, filename, content)
            except (ValueError, UnicodeDecodeError) as error:
                raise HTTPException(
                    status_code=400,
                    detail=f"{filename}: {error}",
                ) from error
            if len(text) > MAX_FILE_TEXT_CHARS:
                raise HTTPException(
                    status_code=413,
                    detail=f"{filename}: extracted text must be 30,000 characters or less.",
                )
            total_file_text_chars += len(text)
            if total_file_text_chars > MAX_TOTAL_FILE_TEXT_CHARS:
                raise HTTPException(status_code=413, detail="Keep extracted text from all files under 40,000 characters.")

            attachment_context.append({"filename": filename, "text": text})

        def response_stream():
            try:
                yield from ask_candidate(
                    conversation,
                    get_candidate_profile(),
                    attachments=attachment_context,
                )
            finally:
                CHAT_CONCURRENCY.release()

        return StreamingResponse(response_stream(), media_type="text/plain")
    except BaseException:
        CHAT_CONCURRENCY.release()
        raise


if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
