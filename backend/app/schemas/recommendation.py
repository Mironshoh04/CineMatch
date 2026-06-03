from pydantic import BaseModel

from .movie import MovieOut


class RecommendationOut(BaseModel):
    movie: MovieOut
    score: float


class RecommendationList(BaseModel):
    user_id: int
    recommendations: list[RecommendationOut]
