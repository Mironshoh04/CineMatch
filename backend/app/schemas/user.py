from pydantic import BaseModel


class UserIn(BaseModel):
    display_name: str | None = None
    username: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    created_at: str
    rating_count: int = 0


class UserRatingMovie(BaseModel):
    movie_id: int
    title: str
    genres: str
    poster_url: str = ""
    rating: float
    created_at: str
