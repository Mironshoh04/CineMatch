from ..core.model_loader import get_id_mappings
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
