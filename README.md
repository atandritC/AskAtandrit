# Portfolio Chatbot

An AI portfolio project that will let recruiters ask questions about a candidate's experience, projects, and skills. The goal is to answer from the candidate's real information and be clear when the available information does not support an answer.

## Current progress

- Reads text from one PDF resume in `data/resume/`; the PDF can be replaced without changing the code.
- Streams a single question and the resume text to Groq, printing the answer as it is generated. The system prompt asks for grounded, honest answers.
- FastAPI dependencies are installed; the API and recruiter-facing web interface are not built yet.
- Personal resume files and API secrets are excluded from Git.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)
- A Groq API key for the chat script

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

## Read the resume

```bash
uv run python read_resume.py
```

This extracts and prints the text from the resume PDF.

## Try a candidate question

```bash
uv run python -m portfolio_chatbot.chat
```

The script prompts for one question, sends it with the resume text to Groq, and prints the answer as it streams in. Do not commit your `.env` file or resume PDF.
