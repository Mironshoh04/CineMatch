from fastapi import APIRouter, HTTPException

from ..services.database_service import (
    get_user,
    update_user_display_name,
    update_user_username,
    ensure_user_exists,
    get_user_rating_count,
)
from ..services.rating_service import get_user_ratings_with_movies
from ..schemas.user import UserIn, UserOut, UserRatingMovie

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserOut)
def user_profile(user_id: int):
    ensure_user_exists(user_id)
    user = get_user(user_id)
    user["rating_count"] = get_user_rating_count(user_id)
    return UserOut(**user)


@router.put("/{user_id}", response_model=UserOut)
def update_profile(user_id: int, body: UserIn):
    ensure_user_exists(user_id)

    if body.display_name is not None:
        update_user_display_name(user_id, body.display_name)

    if body.username is not None:
        result = update_user_username(user_id, body.username)
        if not result["ok"]:
            raise HTTPException(409, result["error"])

    user = get_user(user_id)
    user["rating_count"] = get_user_rating_count(user_id)
    return UserOut(**user)


@router.get("/{user_id}/ratings", response_model=list[UserRatingMovie])
def user_ratings(user_id: int):
    return [UserRatingMovie(**r) for r in get_user_ratings_with_movies(user_id)]
