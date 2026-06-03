from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

ENV_PATH = ROOT / ".env"
load_dotenv(ENV_PATH)

import os

TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "")
if not TMDB_API_KEY:
    raise RuntimeError(f"TMDB_API_KEY not set in {ENV_PATH}")
