from functools import lru_cache
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from portfolio_chatbot.chat import ask_candidate, client
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
def receive_chat_message(request: ChatRequest) -> StreamingResponse:
    conversation = [message.model_dump() for message in request.messages]

    return StreamingResponse(
        ask_candidate(conversation, get_candidate_profile()), media_type="text/plain"
    )
