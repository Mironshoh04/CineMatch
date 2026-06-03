from fastapi import APIRouter, Query

from ..services.recommendation_service import recommend_for_user, similar_movies
from ..services.database_service import get_user_history
from ..schemas.recommendation import RecommendationList, RecommendationOut

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/user/{user_id}", response_model=RecommendationList)
def recommend(user_id: int, k: int = Query(10, ge=1, le=100)):
    past_ratings = get_user_history(user_id)
    recs = recommend_for_user(user_id, user_ratings=past_ratings if past_ratings else None, k=k)
    return RecommendationList(
        user_id=user_id,
        recommendations=[RecommendationOut(**r) for r in recs],
    )


@router.get("/cold-start", response_model=RecommendationList)
def cold_start(genres: str = Query("", description="Comma-separated genres")):
    recs = recommend_for_user(user_id=0, user_ratings=None, k=20)
    return RecommendationList(
        user_id=0,
        recommendations=[RecommendationOut(**r) for r in recs],
    )


@router.get("/similar/{movie_id}", response_model=list[RecommendationOut])
def similar(movie_id: int, n: int = Query(10, ge=1, le=50)):
    results = similar_movies(movie_id, n=n)
    return [RecommendationOut(**r) for r in results]
