from fastapi import APIRouter

from ..services.rating_service import record_rating, get_user_ratings
from ..schemas.rating import RatingIn, RatingOut, UserRating

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("", response_model=RatingOut)
def submit_rating(body: RatingIn):
    return record_rating(body.user_id, body.movie_id, body.rating)


@router.get("/user/{user_id}", response_model=list[UserRating])
def user_ratings(user_id: int):
    return get_user_ratings(user_id)
