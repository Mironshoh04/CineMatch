from fastapi import APIRouter

from ..services.rating_service import record_rating, get_user_ratings
from ..schemas.rating import RatingIn, RatingOut

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("", response_model=RatingOut)
def submit_rating(body: RatingIn):
    return record_rating(body.user_id, body.movie_id, body.rating)


@router.get("/user/{user_id}", response_model=list[RatingOut])
def user_ratings(user_id: int):
    ratings = get_user_ratings(user_id)
    return [RatingOut(**r) for r in ratings]
