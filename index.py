"""Vercel entrypoint for the FastAPI application."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from portfolio_chatbot.api import app  # noqa: E402
