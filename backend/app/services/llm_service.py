import json

import httpx

from ..core.config import settings
from ..core.model_loader import get_movie_meta, get_movie_poster_url
from .embedding_service import search as semantic_search

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:streamGenerateContent?alt=sse"


def search_catalog(query: str, top_n: int = 30) -> list[dict]:
    return semantic_search(query, top_n=top_n)


def build_prompt(query: str, movies: list[dict]) -> str:
    lines = []
    for m in movies:
        overview = m["overview"][:300] if m["overview"] else ""
        line = f"- {m['title']} ({m['genres'].replace('|', ', ')})"
        if overview:
            line += f": {overview}"
        lines.append(line)

    catalog = "\n".join(lines)

    return f"""You are CineMatch AI, a movie recommendation assistant. You have access to this movie catalog:

{catalog}

The user says: "{query}"

Recommend 3-5 movies from the catalog above that best match what they're looking for. For each recommendation:
- State the movie title
- Explain why it fits
- Mention the genre

If nothing closely matches, suggest the closest options and explain the mismatch. Keep responses friendly and concise."""


def format_history(history: list[dict]) -> str:
    parts = []
    for msg in history:
        role = msg.get("role", "user")
        text = msg.get("text", "")
        parts.append(f"{'User' if role == 'user' else 'Assistant'}: {text}")
    return "\n".join(parts)


async def stream_chat(message: str, history: list[dict] | None = None):
    if not settings.gemini_api_key:
        yield "AI is not configured yet. Add a GEMINI_API_KEY to your .env file.\n__DONE__"
        return

    movies = search_catalog(message)
    if not movies:
        yield "I couldn't find any movies in the catalog matching your request. Try being more specific!\n__DONE__"
        return

    prompt = build_prompt(message, movies)
    if history:
        hist = format_history(history)
        prompt = f"Previous conversation:\n{hist}\n\n{prompt}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        },
    }

    url = f"{GEMINI_URL}&key={settings.gemini_api_key}"
    async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", url, json=payload) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    yield f"AI service error ({resp.status_code}). Try again later.\n__DONE__"
                    return

                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if isinstance(data, dict) and "candidates" in data:
                                candidates = data.get("candidates", [])
                                if candidates:
                                    parts = candidates[0].get("content", {}).get("parts", [])
                                    for part in parts:
                                        text = part.get("text", "")
                                        if text:
                                            yield text
                        except json.JSONDecodeError:
                            continue

                yield "\n__DONE__"
