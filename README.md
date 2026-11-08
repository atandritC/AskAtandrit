<div align="center">

<img src="docs/readme-banner.svg" alt="Ask.Atandrit — a conversational portfolio for exploring Atandrit’s experience, projects, and skills" width="100%" />

<br />

[![Live demo](https://img.shields.io/badge/OPEN_LIVE_DEMO-Ask.Atandrit-163B5B?style=for-the-badge&logo=vercel&logoColor=white)](https://ask-atandrit.vercel.app/)

<br />

`PYTHON 3.14+` &nbsp; · &nbsp; `FASTAPI` &nbsp; · &nbsp; `GROQ`

</div>

<br />

> **The idea** &nbsp; Give recruiters a more natural way to learn about Atandrit: ask a question, share relevant context, and get a streamed answer grounded in his resume.

---

## ◈ Explore

<div align="center">

| &nbsp;01&nbsp; **Overview** | &nbsp;02&nbsp; **Architecture** | &nbsp;03&nbsp; **Quick start** | &nbsp;04&nbsp; **Deployment** |
|:---:|:---:|:---:|:---:|
| [What it does](#what-it-does) | [How it works](#how-it-works) | [Get started](#get-started) | [Deploy to Vercel](#deploy-to-vercel) |

</div>

## What it does

Ask.Atandrit turns a portfolio into a conversation. Ask about experience, projects, or skills; attach a document for extra context; or download the public resume.

| **Resume-grounded** | **Made for recruiters** | **Lightweight by design** |
|:---|:---|:---|
| Groq extracts a structured candidate profile, validated with Pydantic. Answers use that profile as their source of facts. | A responsive chat interface with streamed answers, file attachments, light and dark themes, and resume download. | FastAPI serves health, chat, and resume endpoints. Conversations and visitor uploads are not saved by the app. |

**Experience details** &nbsp; Python calculates inclusive role durations, merges overlapping roles for total experience, and formats time in years and months.

## How it works

<div align="center">

<img src="docs/architecture.svg" alt="A recruiter question and optional visitor files are combined with the resume profile, sent to Groq, and streamed back to the website." width="100%" />

</div>

The browser sends the conversation and any attached files with each question. The API extracts readable text, combines it with the in-memory candidate profile, and streams a response. Earlier messages and files are supplied again by the browser with each request; the API does not persist them.

## Get started

<details>
<summary><strong>Requirements and first-time setup</strong></summary>
<br />

- Python **3.14 or newer**
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm (to run the website)
- A [Groq API key](https://console.groq.com/keys)

```bash
git clone https://github.com/atandritC/AskAtandrit.git
cd AskAtandrit
uv sync
mkdir -p data/resume
```

Place one PDF resume in `data/resume/`. The directory is ignored by Git. For a deployed resume download, use the explicitly permitted filename `data/resume/public-resume.pdf` and only include a copy intended for public access.

Create `.env` in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

Keep API keys and private resume copies out of Git.

</details>

## Run locally

<details>
<summary><strong>Terminal chat</strong></summary>
<br />

```bash
uv run python -m portfolio_chatbot.chat
```

Parses the resume, builds a validated profile, asks one question, and streams the answer in your terminal.

</details>

<details>
<summary><strong>API</strong></summary>
<br />

```bash
uv run uvicorn portfolio_chatbot.api:app --reload
```

| | Address |
|:--|:--|
| API docs | <http://127.0.0.1:8000/docs> |
| Health check | <http://127.0.0.1:8000/health> |

`POST /chat` accepts a conversation and optional `.txt`, text-based `.pdf`, or `.docx` attachments. Responses stream to the caller. The candidate profile is cached for the life of the process; restart the server after replacing the resume.

</details>

<details>
<summary><strong>Website</strong></summary>
<br />

With the API running, open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually <http://localhost:5173>. The development website forwards API requests to the backend on port 8000.

For a production-style local run, build the website and start FastAPI from the repository root:

```bash
cd frontend
npm run build
cd ..
uv run uvicorn portfolio_chatbot.api:app
```

Then open <http://127.0.0.1:8000>.

</details>

<details>
<summary><strong>Resume reader and checks</strong></summary>
<br />

Extract and print resume text without the LLM:

```bash
uv run python read_resume.py
```

Run the test suite:

```bash
uv run pytest
```

Tests cover role durations, overlapping roles, missing dates, fixed reference dates for current roles, and years-and-months formatting.

</details>

## Privacy & safeguards

<div align="center">

| **4 MB** request cap | **3 files** per request | **80 pages** per PDF | **3** concurrent chats per instance |
|:---:|:---:|:---:|:---:|

</div>

The app does not save conversations or visitor uploads. The parsed resume profile remains in memory while an instance runs and is sent to Groq to generate answers. Use a resume you are authorized to process; keep private copies out of public deployment files.

Additional limits include 1 MB per attached file (2.5 MB combined), 20 messages, and 40,000 characters for conversation text and extracted attachment text. Resume PDFs are limited to 5 MB and 100,000 extracted characters. Groq requests time out after 45 seconds, do not retry, and produce at most 1,000 tokens.

> **Public deployment note** &nbsp; The concurrency cap applies to one running instance; it is not a shared, per-IP rate limit. Configure a Vercel Firewall rate-limit rule for `POST /chat` before broadly sharing the site. The current deployment guidance starts at 10 requests per minute per IP and recommends reviewing traffic before enforcement.

## Deploy to Vercel

The repository is configured to build the website and serve the FastAPI app from the repository root.

1. Import the repository into Vercel, using the repository root as the project root.
2. Add `GROQ_API_KEY` to Vercel environment variables for each deployment environment. Keep it out of frontend settings and source control.
3. To offer a resume download, add a public-safe `data/resume/public-resume.pdf` to the repository. A file available only on your computer will not be available to the deployment.
4. Configure and review a Vercel Firewall rate limit for `POST /chat` before sharing the deployment broadly.
5. Deploy, then check the website, `/health`, `/resume`, and a streamed chat response.

Vercel can start fresh function instances at any time. The profile cache is temporary and may be rebuilt after a cold start. The function is configured for up to 120 seconds.

## Known limitations

- Scanned PDFs need OCR; only text extractable from the PDF is available.
- The profile cache is in-memory and is rebuilt when an instance starts.
- Vercel’s per-instance concurrency cap does not enforce a global traffic limit; use the Firewall for shared rate limiting.
- The deployed site can serve a resume only when the public-safe `public-resume.pdf` is included in the repository.

---

<div align="center">

**Ask.Atandrit** &nbsp; · &nbsp; Built with Python, FastAPI, and Groq

[Try the live chatbot →](https://ask-atandrit.vercel.app/)

</div>
