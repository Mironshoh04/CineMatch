# CineMatch Progress Notes

## Project Goal
- Build a Netflix-like movie recommendation system using MovieLens ml-32m.
- Start with a fast MVP model (item-item cosine similarity).
- Later: switch to ALS or other MF model without major refactor.
- Deliver API + website; store user feedback and retrain periodically.

## Dataset Overview
- Source: MovieLens ml-32m (ratings + tags + movies + links).
- Files: links.csv, movies.csv, ratings.csv, tags.csv.
- Counts (from README): 32,000,204 ratings; 2,000,072 tags; 87,585 movies; 200,948 users.

## Current Status
- EDA notebook created: notebooks/dataset_eda.ipynb
- Loaded datasets and printed shapes.

## Next Steps (MVP - Item-Item Cosine)
1) Deepen EDA
   - Missing values, duplicates, invalid ratings.
   - Ratings distribution and long-tail stats.
   - Activity over time; recent-only slice check.
   - Tag usage and coverage.

2) Data Prep
   - Filter sparse users/movies (e.g., min 20 ratings/user, min 50 ratings/movie).
   - Map userId/movieId to dense indices.
   - Build sparse user-item rating matrix.

3) Baselines + Evaluation
   - Baselines: global mean, user mean, item mean.
   - Split strategy: time-based or leave-one-out.
   - Metrics: precision@k, recall@k, MAP@k; RMSE for sanity.

4) Model v1 (Item-Item Cosine)
   - Normalize ratings (user-mean centered).
   - Compute item-item cosine similarity.
   - Keep top-K neighbors per item.
   - Recommend by aggregating neighbors of user-rated items.

5) Artifacts and Interface (to allow ALS later)
   - Common model API: fit(), recommend(user_id, k), similar_items(item_id, k).
   - Store: item_neighbors.pkl and id mappings.

## Planned MVP API
- GET /recommendations?userId=...
- POST /ratings (store feedback)
- GET /movies/:id

## Open Decisions
- Exact min ratings thresholds for users/movies.
- Split method: time-based vs leave-one-out.
- Explicit ratings vs implicit likes (default: explicit).

## Notes
- Use tmdbId to fetch posters/metadata for UI.
- Retrain cadence: batch schedule once feedback starts.
