"""Install and build the frontend during Vercel's Python build step."""

import subprocess
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"


def main() -> None:
    subprocess.run(["npm", "ci"], cwd=FRONTEND_DIR, check=True)
    subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, check=True)


if __name__ == "__main__":
    main()
