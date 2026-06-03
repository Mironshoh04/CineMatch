from fastapi import APIRouter, HTTPException

from ..services.database_service import (
    ensure_user_exists,
    create_watchlist,
    get_user_watchlists,
    delete_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
)
from ..services.watchlist_service import get_watchlist_items_with_movies
from ..schemas.watchlist import WatchlistIn, WatchlistOut, WatchlistItemOut, WatchlistItemIn

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


@router.get("/{user_id}", response_model=list[WatchlistOut])
def list_watchlists(user_id: int):
    ensure_user_exists(user_id)
    return [WatchlistOut(**w) for w in get_user_watchlists(user_id)]


@router.post("", response_model=WatchlistOut)
def create(body: WatchlistIn):
    ensure_user_exists(body.user_id)
    wl_id = create_watchlist(body.user_id, body.name)
    wls = get_user_watchlists(body.user_id)
    wl = next((w for w in wls if w["id"] == wl_id), None)
    if not wl:
        raise HTTPException(500, "Failed to create watchlist")
    return WatchlistOut(**wl)


@router.delete("/{watchlist_id}")
def remove(watchlist_id: int):
    delete_watchlist(watchlist_id)
    return {"ok": True}


@router.get("/{watchlist_id}/items", response_model=list[WatchlistItemOut])
def list_items(watchlist_id: int):
    return [WatchlistItemOut(**i) for i in get_watchlist_items_with_movies(watchlist_id)]


@router.post("/{watchlist_id}/items", response_model=dict)
def add_item(watchlist_id: int, body: WatchlistItemIn):
    result = add_to_watchlist(watchlist_id, body.movie_id)
    if not result["ok"]:
        raise HTTPException(409, result["error"])
    return {"ok": True}


@router.delete("/{watchlist_id}/items/{movie_id}")
def remove_item(watchlist_id: int, movie_id: int):
    remove_from_watchlist(watchlist_id, movie_id)
    return {"ok": True}
