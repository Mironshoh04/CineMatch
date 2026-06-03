import pandas as pd

from typing import Optional

from ..core.config import settings
from ..core.model_loader import get_id_mappings, get_movie_poster_url

_movies_df: Optional[pd.DataFrame] = None


def _load_movies():
    global _movies_df
    if _movies_df is not None:
        return
    raw = pd.read_csv(f"{settings.data_dir}/full_dataset/movies.csv")
    movie_id_to_idx, _ = get_id_mappings()
    known = set(movie_id_to_idx.keys()) if movie_id_to_idx else set()
    if known:
        raw = raw[raw["movieId"].isin(known)]
    _movies_df = raw


def get_all_movies(page: int = 1, per_page: int = 50, query: str = "", genre: str = ""):
    _load_movies()
    df = _movies_df.copy()

    if query:
        df = df[df["title"].str.contains(query, case=False, na=False)]

    if genre:
        df = df[df["genres"].str.contains(genre, case=False, na=False)]

    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    page_data = df.iloc[start:end].copy()
    page_data.rename(columns={"movieId": "movie_id"}, inplace=True)
    movies = page_data.to_dict(orient="records")
    for m in movies:
        m["poster_url"] = get_movie_poster_url(m["movie_id"])
    return {
        "movies": movies,
        "total": total,
    }


def search_movies(query: str, limit: int = 20):
    _load_movies()
    mask = _movies_df["title"].str.contains(query, case=False, na=False)
    results = _movies_df[mask].head(limit).copy()
    results.rename(columns={"movieId": "movie_id"}, inplace=True)
    movies = results.to_dict(orient="records")
    for m in movies:
        m["poster_url"] = get_movie_poster_url(m["movie_id"])
    return movies


def get_genres() -> list[str]:
    _load_movies()
    all_genres = set()
    for g in _movies_df["genres"].dropna():
        for part in g.split("|"):
            part = part.strip()
            if part:
                all_genres.add(part)
    return sorted(all_genres)


def get_known_movie_ids() -> set[int]:
    _load_movies()
    return set(_movies_df["movieId"].tolist())
