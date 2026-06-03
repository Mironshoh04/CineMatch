from .database_service import get_watchlist_items as db_get_items
from ..core.model_loader import get_movie_meta, get_movie_poster_url


def get_watchlist_items_with_movies(watchlist_id: int) -> list[dict]:
    items = db_get_items(watchlist_id)
    meta = get_movie_meta()
    results = []
    for item in items:
        movie_meta = meta.get(item["movie_id"], {})
        results.append({
            "movie_id": item["movie_id"],
            "title": movie_meta.get("title", "Unknown"),
            "genres": movie_meta.get("genres", ""),
            "poster_url": get_movie_poster_url(item["movie_id"]),
            "added_at": item["added_at"],
        })
    return results
