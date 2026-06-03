from fastapi import APIRouter, Query

from ..services.movie_service import get_all_movies, search_movies, get_genres
from ..schemas.movie import MovieList, MovieOut

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=MovieList)
def list_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    q: str = Query("", description="Search by title"),
    genre: str = Query("", description="Filter by genre"),
):
    data = get_all_movies(page=page, per_page=per_page, query=q, genre=genre)
    return MovieList(movies=[MovieOut(**m) for m in data["movies"]], total=data["total"])


@router.get("/search", response_model=list[MovieOut])
def search(q: str = Query("", min_length=1), limit: int = Query(20, ge=1, le=100)):
    results = search_movies(q, limit=limit)
    return [MovieOut(**m) for m in results]


@router.get("/genres", response_model=list[str])
def genres():
    return get_genres()
