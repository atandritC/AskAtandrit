# Portfolio Chatbot

An AI portfolio project that will let recruiters ask questions about a candidate's experience, projects, and skills. The goal is to answer from the candidate's real information and be clear when the available information does not support an answer.

## Current progress

- Reads text from one PDF resume in `data/resume/`; the PDF can be replaced without changing the code.
- Uses Groq to extract a structured candidate profile from the resume and validates the result with Pydantic.
- The profile includes projects, skills, experience, organization locations, and the original date period from the resume. Python calculates per-role durations and total experience from extracted dates, merging overlapping roles to avoid double-counting.
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

## Parse and inspect the candidate profile

```bash
uv run python -m portfolio_chatbot.chat
```

The current CLI sends the resume to Groq, validates the returned profile with Pydantic, and prints it as JSON. The output may contain personal information, so inspect it locally and do not commit or share it.

## Read the resume without the LLM

```bash
uv run python read_resume.py
```

This extracts and prints the text from the resume PDF. Do not commit your `.env` file or resume PDF.
