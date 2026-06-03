from datetime import datetime
from typing import Optional

import pandas as pd

from ..core.config import settings
from ..core.model_loader import get_id_mappings

_ratings: list[dict] = []


def record_rating(user_id: int, movie_id: int, rating: float):
    movie_id_to_idx, _ = get_id_mappings()
    if movie_id not in movie_id_to_idx:
        return {"user_id": user_id, "movie_id": movie_id, "rating": rating, "message": "Movie not in catalog"}
    _ratings.append({
        "user_id": user_id,
        "movie_id": movie_id,
        "rating": rating,
        "timestamp": datetime.utcnow().isoformat(),
    })
    return {"user_id": user_id, "movie_id": movie_id, "rating": rating, "message": "Rating recorded"}


def get_user_ratings(user_id: int) -> list[dict]:
    return [r for r in _ratings if r["user_id"] == user_id]


def get_training_ratings(user_id: int) -> list[tuple[int, float]]:
    """Return (movie_id, rating) pairs from the training set for a known user."""
    ratings_csv = f"{settings.data_dir}/full_dataset/ratings.csv"
    try:
        chunk = pd.read_csv(ratings_csv, usecols=["userId", "movieId", "rating"])
        chunk = chunk[chunk["userId"] == user_id]
        return list(zip(chunk["movieId"].tolist(), chunk["rating"].tolist()))
    except FileNotFoundError:
        return []
