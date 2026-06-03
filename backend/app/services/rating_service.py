from ..core.model_loader import get_id_mappings, get_movie_meta, get_movie_poster_url, get_movie_description
from .database_service import record_rating as db_record_rating
from .database_service import get_user_ratings as db_get_user_ratings


def record_rating(user_id: int, movie_id: int, rating: float):
    movie_id_to_idx, _ = get_id_mappings()
    if movie_id not in movie_id_to_idx:
        return {"user_id": user_id, "movie_id": movie_id, "rating": rating, "message": "Movie not in catalog"}
    db_record_rating(user_id, movie_id, rating)
    return {"user_id": user_id, "movie_id": movie_id, "rating": rating, "message": "Rating recorded"}


def get_user_ratings(user_id: int) -> list[dict]:
    return db_get_user_ratings(user_id)


def get_user_ratings_with_movies(user_id: int) -> list[dict]:
    ratings = db_get_user_ratings(user_id)
    meta = get_movie_meta()
    results = []
    for r in ratings:
        movie_meta = meta.get(r["movie_id"], {})
        desc = get_movie_description(r["movie_id"])
        results.append({
            "movie_id": r["movie_id"],
            "title": movie_meta.get("title", "Unknown"),
            "genres": movie_meta.get("genres", ""),
            "poster_url": get_movie_poster_url(r["movie_id"]),
            "overview": desc["overview"],
            "tagline": desc["tagline"],
            "rating": r["rating"],
            "created_at": r["created_at"],
        })
    return results
