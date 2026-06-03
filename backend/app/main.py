from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.model_loader import load_model
from .services.database_service import init_db
from .api import movies, recommendations, ratings, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_model()
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies.router)
app.include_router(recommendations.router)
app.include_router(ratings.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}
