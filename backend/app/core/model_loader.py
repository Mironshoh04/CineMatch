import pickle
from pathlib import Path

import pandas as pd

from .config import settings


_model = None
_movie_meta = None
_movie_id_to_idx = None
_idx_to_movie_id = None


def load_model():
    global _model, _movie_meta, _movie_id_to_idx, _idx_to_movie_id

    model_path = Path(settings.model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")

    with open(model_path, "rb") as f:
        artifacts = pickle.load(f)

    _model = artifacts["model"]
    _movie_id_to_idx = artifacts.get("movie_id_to_idx")
    _idx_to_movie_id = artifacts.get("idx_to_movie_id")

    # Load movie metadata from artifact or CSV
    _movie_meta = artifacts.get("movie_meta")
    if _movie_meta is None:
        movies_csv = Path(settings.data_dir) / "full_dataset" / "movies.csv"
        movies = pd.read_csv(movies_csv)
        _movie_meta = movies.set_index("movieId")[["title", "genres"]].to_dict("index")
        if _movie_id_to_idx:
            _movie_id_to_idx = {int(k): int(v) for k, v in _movie_id_to_idx.items()}
        if _idx_to_movie_id:
            _idx_to_movie_id = {int(k): int(v) for k, v in _idx_to_movie_id.items()}

    return _model


def get_model():
    if _model is None:
        load_model()
    return _model


def get_movie_meta():
    if _movie_meta is None:
        load_model()
    return _movie_meta


def get_id_mappings():
    if _movie_id_to_idx is None:
        load_model()
    return _movie_id_to_idx, _idx_to_movie_id
