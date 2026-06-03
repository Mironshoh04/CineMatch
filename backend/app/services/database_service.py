import sqlite3
from datetime import datetime
from pathlib import Path
from threading import Lock

from ..core.config import settings

_lock = Lock()
_conn = None  # type: sqlite3.Connection | None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        db_path = Path(settings.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(db_path), check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
    return _conn


def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            movie_id INTEGER NOT NULL,
            rating REAL NOT NULL CHECK (rating >= 0.5 AND rating <= 5.0),
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);
        CREATE INDEX IF NOT EXISTS idx_ratings_movie ON ratings(movie_id);

        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            name TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS watchlist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watchlist_id INTEGER NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
            movie_id INTEGER NOT NULL,
            added_at TEXT DEFAULT (datetime('now')),
            UNIQUE(watchlist_id, movie_id)
        );

        CREATE INDEX IF NOT EXISTS idx_watchlists_user ON watchlists(user_id);
        CREATE INDEX IF NOT EXISTS idx_watchlist_items_wl ON watchlist_items(watchlist_id);
    """)
    conn.commit()


def get_or_create_user(username: str, display_name: str = "") -> int:
    conn = _get_conn()
    cur = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO users (username, display_name) VALUES (?, ?)",
        (username, display_name),
    )
    conn.commit()
    return cur.lastrowid


def record_rating(user_id: int, movie_id: int, rating: float):
    conn = _get_conn()
    with _lock:
        conn.execute(
            "INSERT OR IGNORE INTO users (id, username, display_name) VALUES (?, ?, ?)",
            (user_id, f"user_{user_id}", f"User {user_id}"),
        )
        cur = conn.execute(
            "INSERT INTO ratings (user_id, movie_id, rating) VALUES (?, ?, ?)",
            (user_id, movie_id, rating),
        )
        conn.commit()
        return cur.lastrowid


def get_user_ratings(user_id: int) -> list[dict]:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT movie_id, rating, created_at FROM ratings WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    return [dict(row) for row in cur.fetchall()]


def get_user_history(user_id: int) -> list[tuple[int, float]]:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT movie_id, rating FROM ratings WHERE user_id = ?",
        (user_id,),
    )
    return [(row["movie_id"], row["rating"]) for row in cur.fetchall()]


def get_user(user_id: int) -> dict | None:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT id, username, display_name, created_at FROM users WHERE id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def update_user_display_name(user_id: int, display_name: str) -> bool:
    conn = _get_conn()
    with _lock:
        cur = conn.execute(
            "UPDATE users SET display_name = ? WHERE id = ?",
            (display_name, user_id),
        )
        conn.commit()
        return cur.rowcount > 0


def get_user_rating_count(user_id: int) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT COUNT(*) AS cnt FROM ratings WHERE user_id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    return row["cnt"] if row else 0


def ensure_user_exists(user_id: int):
    conn = _get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (id, username, display_name) VALUES (?, ?, ?)",
        (user_id, f"user_{user_id}", f"User {user_id}"),
    )
    conn.commit()


def update_user_username(user_id: int, username: str) -> dict:
    conn = _get_conn()
    with _lock:
        try:
            cur = conn.execute(
                "UPDATE users SET username = ? WHERE id = ?",
                (username, user_id),
            )
            conn.commit()
            return {"ok": cur.rowcount > 0, "error": ""}
        except sqlite3.IntegrityError:
            return {"ok": False, "error": "Username already taken"}


def create_watchlist(user_id: int, name: str) -> int:
    conn = _get_conn()
    with _lock:
        cur = conn.execute(
            "INSERT INTO watchlists (user_id, name) VALUES (?, ?)",
            (user_id, name),
        )
        conn.commit()
        return cur.lastrowid


def get_user_watchlists(user_id: int) -> list[dict]:
    conn = _get_conn()
    cur = conn.execute("""
        SELECT w.id, w.user_id, w.name, w.created_at,
               (SELECT COUNT(*) FROM watchlist_items WHERE watchlist_id = w.id) AS item_count
        FROM watchlists w WHERE w.user_id = ? ORDER BY w.created_at DESC
    """, (user_id,))
    return [dict(row) for row in cur.fetchall()]


def delete_watchlist(watchlist_id: int):
    conn = _get_conn()
    with _lock:
        conn.execute("DELETE FROM watchlist_items WHERE watchlist_id = ?", (watchlist_id,))
        conn.execute("DELETE FROM watchlists WHERE id = ?", (watchlist_id,))
        conn.commit()


def add_to_watchlist(watchlist_id: int, movie_id: int) -> dict:
    conn = _get_conn()
    with _lock:
        try:
            conn.execute(
                "INSERT INTO watchlist_items (watchlist_id, movie_id) VALUES (?, ?)",
                (watchlist_id, movie_id),
            )
            conn.commit()
            return {"ok": True, "error": ""}
        except sqlite3.IntegrityError:
            conn.commit()
            return {"ok": False, "error": "Movie already in watchlist"}


def remove_from_watchlist(watchlist_id: int, movie_id: int):
    conn = _get_conn()
    with _lock:
        conn.execute(
            "DELETE FROM watchlist_items WHERE watchlist_id = ? AND movie_id = ?",
            (watchlist_id, movie_id),
        )
        conn.commit()


def get_watchlist_items(watchlist_id: int) -> list[dict]:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT movie_id, added_at FROM watchlist_items WHERE watchlist_id = ? ORDER BY added_at DESC",
        (watchlist_id,),
    )
    return [dict(row) for row in cur.fetchall()]
