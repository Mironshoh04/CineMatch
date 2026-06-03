from pydantic import BaseModel


class MovieOut(BaseModel):
    movie_id: int
    title: str
    genres: str
    poster_url: str = ""


class MovieList(BaseModel):
    movies: list[MovieOut]
    total: int
