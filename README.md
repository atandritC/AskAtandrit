# Portfolio Chatbot

An AI portfolio project that will let recruiters ask questions about a candidate's experience, projects, and skills. The goal is to answer from the candidate's real information and be clear when the available information does not support an answer.

## Current progress

- Reads text from one PDF resume in `data/resume/`; the PDF can be replaced without changing the code.
- Uses Groq to extract a structured candidate profile from the resume and validates the result with Pydantic.
- The profile includes projects, skills, experience, organization locations, and the original date period from the resume. Python counts inclusive calendar months, merges overlapping roles for the total, and formats durations as years and months (for example, `1 year 9 months`).
- A streaming answer function is present; the API and recruiter-facing web interface are not built yet.
- Personal resume files and API secrets are excluded from Git.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)
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
