from pydantic import BaseModel


class WatchlistIn(BaseModel):
    user_id: int
    name: str


class WatchlistOut(BaseModel):
    id: int
    user_id: int
    name: str
    item_count: int = 0
    created_at: str


class WatchlistItemOut(BaseModel):
    movie_id: int
    title: str
    genres: str
    poster_url: str = ""
    added_at: str


class WatchlistItemIn(BaseModel):
    movie_id: int
