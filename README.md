# Portfolio Chatbot

An AI portfolio project that will let recruiters ask questions about a candidate's experience, projects, and skills. The goal is to answer from the candidate's real information and be clear when the available information does not support an answer.

## Current progress

- Reads text from one PDF resume in `data/resume/`; the PDF can be replaced without changing the code.
- Uses Groq to extract a structured candidate profile from the resume and validates the result with Pydantic.
- The profile includes projects, skills, experience, organization locations, and the original date period from the resume. Python counts inclusive calendar months, merges overlapping roles for the total, and formats durations as years and months (for example, `1 year 9 months`).
- A FastAPI backend is available with a health check, a streaming `/chat` endpoint, and a resume download.
- A responsive React website provides the recruiter chat interface, streaming answers, file attachments, light/dark themes, and a download link for the resume.
- Personal resume files and API secrets are excluded from Git.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm
- A Groq API key for the profile parser

## Setup

Clone the repository, then from its root folder run:

```bash
uv sync
mkdir -p data/resume
```

Put exactly one PDF resume in `data/resume/`. The folder's contents are intentionally ignored by Git because resumes contain personal information.

Create a `.env` file in the project root and add your Groq API key:

```text
GROQ_API_KEY=your_key_here
```

Keep `.env` private; it is ignored by Git.

## Run the chatbot

```bash
uv run python -m portfolio_chatbot.chat
```

The CLI parses the resume into a validated candidate profile, calculates and formats experience durations in Python, asks one question, and streams an answer grounded in that profile. The profile contains personal information and is sent to Groq; keep it private and do not commit or share it.

## Run the API

```bash
uv run uvicorn portfolio_chatbot.api:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the API. `POST /chat` accepts a conversation, optional `.txt`, text-based `.pdf`, or `.docx` attachments, and streams a reply. Attachments can provide extra context for any question. The caller sends earlier messages and any attachments it wants considered with each request; the API does not save conversations or attachments. The parsed resume profile is reused while the server runs. Restart the server after replacing the resume. Scanned PDFs need OCR and are not readable yet.

## Run the website locally

Install Node.js, then open two terminals in the project folder.

In the first terminal, start the backend:

```bash
uv run uvicorn portfolio_chatbot.api:app --reload
```

In the second terminal, start the website:

```bash
cd frontend
npm install
npm run dev
```

Open the local website address printed by Vite (usually `http://localhost:5173`). The site forwards chat, health, and resume requests to the backend on port 8000. For a production-style local run, build the website with `npm run build` inside `frontend`, then open `http://127.0.0.1:8000`; FastAPI serves the built website and `/resume` serves the current PDF from `data/resume/`.

## Read the resume without the LLM

```bash
uv run python read_resume.py
```

This extracts and prints the text from the resume PDF. Do not commit your `.env` file or resume PDF.

## Run tests

```bash
uv run pytest
```

The tests cover inclusive per-role duration, overlapping roles, missing dates, fixed reference dates for current roles, and years-and-months formatting.
