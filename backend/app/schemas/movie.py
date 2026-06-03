from pydantic import BaseModel


class MovieOut(BaseModel):
    movie_id: int
    title: str
    genres: str


class MovieList(BaseModel):
    movies: list[MovieOut]
    total: int
