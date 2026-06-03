from pydantic import BaseModel


class RatingIn(BaseModel):
    user_id: int
    movie_id: int
    rating: float


class RatingOut(BaseModel):
    user_id: int
    movie_id: int
    rating: float
    message: str = "Rating recorded"


class UserRating(BaseModel):
    movie_id: int
    rating: float
    created_at: str
