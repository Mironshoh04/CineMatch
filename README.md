# 🎬 CineMatch

CineMatch is a Netflix-style movie recommendation engine built on the **MovieLens 32M dataset** using **ALS (Alternating Least Squares)** matrix factorization with implicit feedback. Features a FastAPI backend, React frontend, live TMDB posters & descriptions, and an AI chat assistant powered by Gemini.

---

## Table of Contents

- [Features](#features)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Scripts](#scripts)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Tech Stack](#tech-stack)

---

## Features

- **Personalized recommendations** — ALS model trained on 31.5M ratings
- **Search + genre filter** — find movies by title or category
- **Movie detail page** — poster, genres, similar movies, rate, share, watchlist
- **User profiles** — editable username / display name, list of past ratings
- **Watchlists** — create named lists, add/remove movies
- **Group mode** — merge ratings from multiple users for shared recommendations
- **AI chat assistant** — natural language movie recommendations via Gemini 2.5 Flash (uses descriptions.json for catalog context)
- **TMDB posters** — poster images on every movie card / detail page
- **TMDB descriptions** — overview + tagline cached for AI chat context
- **Share** — Web Share API (or clipboard fallback)

---

## Dataset

**Source**: [MovieLens 32M](https://grouplens.org/datasets/movielens/32m/)

| File | Records |
|------|---------|
| `ratings.csv` | 32,000,204 ratings (0.5–5.0) |
| `tags.csv` | 2,000,072 tags |
| `movies.csv` | 87,585 movies |
| `links.csv` | 87,585 IMDb/TMDB ID mappings |

**Filtering**: Users with < 20 ratings and movies with < 50 ratings are removed, keeping **~31.5M ratings**, **200,947 users**, and **16,034 movies**.

---

## Project Structure

```
CineMatch/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/             # movies, recommendations, ratings, users, watchlists, ai
│   │   ├── core/            # config, model_loader
│   │   ├── schemas/         # Pydantic models
│   │   ├── services/        # database_service, recommendation_service, llm_service, watchlist_service
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React + Vite application
│   ├── src/
│   │   ├── pages/           # Home, MovieDetail, Recommendations, Profile, Watchlists, GroupMode
│   │   ├── components/      # MovieCard, MovieRow, RatingModal, AddToWatchlist, ChatModal
│   │   ├── services/        # API client (api.js)
│   │   └── hooks/
│   ├── nginx.conf
│   ├── package.json
│   └── Dockerfile
├── data/                    # Dataset (gitignored)
│   ├── full_dataset/        # Raw MovieLens files
│   └── processed/           # Filtered CSVs, idx mappings, posters.json, descriptions.json
├── models/                  # Trained model artifacts
├── notebooks/               # Jupyter notebooks
├── scripts/                 # Utility scripts
│   ├── config.py            # Shared config (loads .env, sets ROOT)
│   ├── fetch_posters.py     # TMDB poster batch fetch
│   ├── fetch_descriptions.py# TMDB overview + tagline fetch
│   └── evaluate_models.py
├── .env                     # API keys (gitignored)
├── docker-compose.yml
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.9+
- Node.js 20+
- Docker + Docker Compose (recommended)

### Clone and install

```bash
git clone https://github.com/Mironshoh04/CineMatch.git
cd CineMatch

# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### Environment variables

Create a `.env` file in the project root:

```bash
DEBUG=false
MODEL_PATH=models/als_model.pkl
TMDB_API_KEY=your_tmdb_api_key          # for poster/description scripts
GEMINI_API_KEY=your_gemini_api_key      # for AI chat
```

### Download the dataset

Place the MovieLens 32M dataset files in `data/full_dataset/`:
- `ratings.csv`
- `movies.csv`
- `tags.csv`
- `links.csv`

### Fetch TMDB posters & descriptions (optional)

```bash
python3 scripts/fetch_posters.py
python3 scripts/fetch_descriptions.py
```

Posters are required for the UI. Descriptions are needed for the AI chat feature. Both cache results in `data/processed/` and resume if interrupted. Re-run with `--retry-failed` to retry null/empty entries after fixing network issues.

---

## Running the Application

### Docker (recommended)

```bash
docker compose up --build -d
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/health

### Local development

**Terminal 1 — Backend:**

```bash
source .venv/bin/activate
OPENBLAS_NUM_THREADS=1 uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/fetch_posters.py` | Fetch poster paths from TMDB for all 16K movies |
| `scripts/fetch_descriptions.py` | Fetch overview + tagline from TMDB for AI chat context |
| `scripts/evaluate_models.py` | Compare ALS model variants |
| `scripts/config.py` | Shared config loader (reads `.env`, exposes `ROOT` + `TMDB_API_KEY`) |

Both fetch scripts support `--retry-failed` to retry only null/empty entries.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server health check |
| GET | `/movies?page=&per_page=&q=&genre=` | Paginated movie list with search + genre filter |
| GET | `/movies/genres` | List all genres |
| POST | `/ratings` | Submit a rating |
| GET | `/recommendations/user/{id}?k=` | Personalized recommendations |
| GET | `/recommendations/similar/{id}?n=` | Similar movies (item-item) |
| POST | `/recommendations/group` | Group recommendations (merges user ratings) |
| GET | `/users/{id}` | Get user profile (auto-creates if new) |
| PUT | `/users/{id}` | Update username / display name |
| GET | `/users/{id}/ratings` | List user's ratings with movie metadata |
| GET | `/watchlists/{user_id}` | List user's watchlists |
| POST | `/watchlists` | Create a watchlist |
| DELETE | `/watchlists/{id}` | Delete a watchlist |
| GET | `/watchlists/{id}/items` | List items in a watchlist (with movie data) |
| POST | `/watchlists/{id}/items` | Add movie to watchlist |
| DELETE | `/watchlists/{id}/items/{movie_id}` | Remove movie from watchlist |
| POST | `/ai/chat` | Streaming AI chat (Gemini 2.5 Flash) |

### Rating payload

```json
{
  "user_id": 1,
  "movie_id": 1,
  "rating": 4.5
}
```

### Group recommendation payload

```json
{
  "user_ids": [1712345678, 1712345679],
  "k": 10
}
```

### AI chat payload

```json
{
  "message": "funny sci-fi from the 90s",
  "history": []
}
```

Returns a streaming plain-text response.

---

## Deployment

See the [Deployment Guide](docs/deployment.md) for:
- **Laptop + Cloudflare Tunnel** — run from your laptop, no open ports, free SSL
- **VPS** — Hetzner / DigitalOcean with Nginx reverse proxy
- **Render Free Tier** — platform-as-a-service option

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Recommender** | `implicit` ALS (Alternating Least Squares) |
| **Frontend** | React 18, Vite, React Router 6, react-markdown |
| **AI** | Gemini 2.5 Flash API, httpx streaming |
| **Infrastructure** | Docker, Docker Compose, Cloudflare Tunnel |
| **Database** | SQLite (via Python `sqlite3`) |
| **Data** | Pandas, NumPy, SciPy (sparse matrices) |
