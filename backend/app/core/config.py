from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "CineMatch API"
    debug: bool = False

    # Paths (relative to backend/)
    model_path: str = str(Path(__file__).parent.parent.parent.parent / "models" / "als_model.pkl")
    data_dir: str = str(Path(__file__).parent.parent.parent.parent / "data")
    processed_dir: str = str(Path(__file__).parent.parent.parent.parent / "data" / "processed")
    db_path: str = str(Path(__file__).parent.parent.parent.parent / "data" / "processed" / "cinematch.db")

    # API
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Recommender
    top_k: int = 20

    # AI
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
