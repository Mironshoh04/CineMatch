import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

from ..core.model_loader import get_movie_meta, get_all_descriptions, get_movie_poster_url

_vectorizer: TfidfVectorizer | None = None
_doc_matrix: csr_matrix | None = None
_doc_ids: list[int] = []
_doc_data: list[dict] = []


def _build():
    global _vectorizer, _doc_matrix, _doc_ids, _doc_data
    if _vectorizer is not None:
        return

    meta = get_movie_meta()
    descriptions = get_all_descriptions()

    documents = []
    _doc_ids = []
    _doc_data = []

    for mid_str, movie in meta.items():
        mid = int(mid_str)
        desc = descriptions.get(mid_str, {})
        text = f"{movie['title']} {movie['genres'].replace('|', ' ')}"
        overview = (desc.get("overview", "") or "")[:500]
        tagline = (desc.get("tagline", "") or "")
        if overview:
            text += f" {overview}"
        if tagline:
            text += f" {tagline}"
        documents.append(text.lower())
        _doc_ids.append(mid)
        _doc_data.append({
            "title": movie["title"],
            "genres": movie["genres"],
            "overview": overview,
            "tagline": tagline,
        })

    _vectorizer = TfidfVectorizer(
        max_features=20000,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    _doc_matrix = _vectorizer.fit_transform(documents)
    print(f"[embedding] TF-IDF built: {len(_doc_ids)} docs, {_doc_matrix.shape[1]} features")


def search(query: str, top_n: int = 30) -> list[dict]:
    _build()
    query_vec = _vectorizer.transform([query.lower()])
    scores = (_doc_matrix @ query_vec.T).toarray().flatten()
    top_indices = scores.argsort()[::-1][:top_n]

    results = []
    for idx in top_indices:
        score = float(scores[idx])
        if score == 0:
            continue
        mid = _doc_ids[idx]
        d = _doc_data[idx]
        results.append({
            "movie_id": mid,
            "title": d["title"],
            "genres": d["genres"],
            "overview": d["overview"],
            "tagline": d["tagline"],
            "poster_url": get_movie_poster_url(mid),
            "score": round(score, 4),
        })
    return results
