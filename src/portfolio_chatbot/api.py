from functools import lru_cache
from typing import Annotated, Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from portfolio_chatbot.chat import ask_candidate, client
from portfolio_chatbot.attachments import read_attachment_text
from portfolio_chatbot.profile import CandidateProfile
from portfolio_chatbot.profile_parser import parse_candidate_profile

app = FastAPI(title="Ask.Atandrit")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)


@lru_cache(maxsize=1)
def get_candidate_profile() -> CandidateProfile:
    return parse_candidate_profile(client)


@app.post("/chat")
async def receive_chat_message(
    messages_json: Annotated[str, Form()],
    attachments: Annotated[list[UploadFile] | None, File()] = None,
) -> StreamingResponse:
    request = ChatRequest.model_validate_json(messages_json)
    conversation = [message.model_dump() for message in request.messages]
    attachment_context = []

    for attachment in attachments or []:
        filename = attachment.filename or "uploaded file"
        content = await attachment.read()

        try:
            text = read_attachment_text(filename, content)
        except (ValueError, UnicodeDecodeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"{filename}: {error}",
            ) from error

        attachment_context.append({"filename": filename, "text": text})

    return StreamingResponse(
        ask_candidate(
            conversation,
            get_candidate_profile(),
            attachments=attachment_context,
        ),
        media_type="text/plain",
    )
