from typing import Optional

import numpy as np
from scipy.sparse import csr_matrix

from ..core.model_loader import get_model, get_movie_meta, get_id_mappings, get_movie_poster_url


def _movie_out(movie_id: int) -> dict:
    meta = get_movie_meta().get(movie_id, {})
    return {
        "movie_id": movie_id,
        "title": meta.get("title", "Unknown"),
        "genres": meta.get("genres", ""),
        "poster_url": get_movie_poster_url(movie_id),
    }


def recommend_for_user(user_id: int, user_ratings: Optional[list[tuple[int, float]]] = None, k: int = 10):
    model = get_model()
    movie_id_to_idx, idx_to_movie_id = get_id_mappings()
    n_movies = len(movie_id_to_idx)

    # Build user vector from their ratings
    if user_ratings:
        rows, cols, vals = [], [], []
        for mid, rating in user_ratings:
            if mid in movie_id_to_idx:
                cols.append(movie_id_to_idx[mid])
                rows.append(0)
                vals.append(rating)
        user_vector = csr_matrix(
            (np.array(vals, dtype=np.float32), (rows, cols)),
            shape=(1, n_movies),
        )
    else:
        user_vector = csr_matrix((1, n_movies))

    recs = model.recommend(
        0, user_vector, N=k,
        filter_already_liked_items=bool(user_ratings),
    )

    if isinstance(recs, tuple):
        rec_ids = [int(r) for r in recs[0]]
        rec_scores = [float(s) for s in recs[1]]
    else:
        rec_ids = [int(r[0]) for r in recs]
        rec_scores = [float(r[1]) for r in recs]

    results = []
    for idx, score in zip(rec_ids, rec_scores):
        movie_id = idx_to_movie_id.get(idx)
        if movie_id is None:
            continue
        results.append({
            "movie": _movie_out(int(movie_id)),
            "score": round(score, 4),
        })

    return results


def similar_movies(movie_id: int, n: int = 10):
    model = get_model()
    movie_id_to_idx, idx_to_movie_id = get_id_mappings()

    if movie_id not in movie_id_to_idx:
        return []

    idx = movie_id_to_idx[movie_id]
    ids, scores = model.similar_items(idx, N=n + 1)

    results = []
    for idx, score in zip([int(i) for i in ids], [float(s) for s in scores]):
        mid = idx_to_movie_id.get(idx)
        if mid is None or mid == movie_id:
            continue
        if len(results) >= n:
            break
        results.append({
            "movie": _movie_out(int(mid)),
            "score": round(score, 4),
        })

    return results
