# Portfolio Chatbot

An AI portfolio project that will let recruiters ask questions about a candidate's experience, projects, and skills. The goal is to answer from the candidate's real information and be clear when the available information does not support an answer.

## Current progress

- Reads text from a PDF resume stored in `data/resume/`.
- Requires exactly one PDF in that folder. You can replace it with an updated resume, including under a different filename.
- Keeps personal resume files out of Git.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup

Clone the repository, then from its root folder run:

```bash
uv sync
```

Create the resume folder if needed, then put your PDF resume in it. Keep only one PDF in the folder. The resume is personal information and is intentionally ignored by Git.

```bash
mkdir -p data/resume
```

## Read the resume

Run the current resume-reading example from the project root:

```bash
uv run python read_resume.py
```

The script extracts and prints the text from the resume PDF. This is an early project step; the API and chat interface are not implemented yet.
