# CineMatch — Movie Recommendation System

**Team Project Report**  
Submitted in Partial Fulfillment of the Requirements for the Course Completion of Big Data Analysis

**Prepared by: Team Spark**

| Name | Student ID |
|------|-----------|
| Muhammedov Mironshoh | 12225252 |
| Shokulov Shohruh | 12225260 |
| Zokirov Diyorbek | 12225176 |
| Normuminova Munisa | 12260042 |
| Wang Wenjia | 12260084 |
| Ochilov Shokhrukh | 12214701 |

**Submitted to:** Prof. Humayun Kabir  
**Submission Date:** 10.06.2026

---

## Table of Contents

1. Introduction
2. Motivation & Problem Statement
3. Research Methodology
4. Tools & Technologies
5. Data Analysis
6. Results & Discussion
7. Conclusion
8. References

---

## 1. Introduction

### 1.1 Background

Nowadays, we have thousands of movies available across different platforms like Netflix, Disney+, YouTube, and many others. It is great that there is so much choice, but it is also a big problem. Most of us have had that experience: opening an app, scrolling for 15–20 minutes, and still not knowing what to watch. It is tiring, and it takes away from the fun of watching something good.

This is exactly why recommendation systems exist. They are the engine behind every streaming service, trying to guess what a user will like based on what they have watched, rated, or liked before. But building one is not easy, especially when dealing with millions of users and thousands of movies. Simple methods do not work well at that scale.

That is where CineMatch comes in. We built a full-stack movie recommendation engine, similar to those used by major streaming platforms, but as a student project. We used the MovieLens 32M dataset, one of the largest public datasets available, containing over 32 million ratings from real users covering more than 87,000 movies. This allowed us to work with real big data, exactly as in industry.

Our system uses Collaborative Filtering with the Alternating Least Squares (ALS) algorithm, the standard matrix factorization method that gained prominence during the Netflix Prize competition. We also added AI-powered features using Google Gemini 2.5 Flash, so users can search in natural language — typing queries like "something scary with ghosts" or "funny movies from the 90s" — and receive accurate, catalog-grounded results.

### 1.2 Project Objectives

When we started this work, we set clear goals:

- Build a complete web application where users can browse, search, rate movies, and manage watchlists
- Implement a scalable recommendation engine that works with millions of ratings without slowing down
- Make recommendations personalized — every user gets different results based on their own taste
- Integrate AI-powered natural language search to make discovery easier
- Use modern tools and best practices: React frontend, FastAPI backend, Docker for deployment, SQLite for storage
- Make the entire system open source and well-documented on GitHub
- Use industry-standard big data techniques including sparse matrix computation and distributed-ready containerization

We wanted to demonstrate that we could take what we learned in class and integrate it all into one working product.

### 1.3 Scope and Limitations

This project covers everything from data preparation and exploratory analysis, through model training and hyperparameter tuning, to API development, frontend design, and deployment. We focused on creating a fully functional prototype.

However, there are some limitations:

- We only used the MovieLens 32M dataset, so recommendations are limited to movies in that collection (up to 2019)
- For new users who have not rated anything yet, the model defaults to popularity-based recommendations (cold start)
- We trained on a single machine, not a distributed cluster, which limited the scale of our hyperparameter search
- The system does not include video streaming — only information, posters, and recommendations
- The ALS model is static; new user ratings are used at inference time but do not retrain the model

Even with these constraints, the system works well and demonstrates all core concepts clearly.

### 1.4 Report Structure

This report covers every step of our process. Section 2 discusses the motivation and problems we aimed to solve. Section 3 explains our research methodology. Section 4 details the tools and technologies used. Section 5 describes the data analysis and model training process. Section 6 presents the results and discussion. Section 7 concludes with key learnings and future improvements.

---

## 2. Motivation & Problem Statement

### 2.1 Why We Chose This Project

We all love movies, and we all know how frustrating it is to spend time just choosing what to watch. That was our first motivation — we wanted to solve a problem we actually face every day.

Second, we were interested in how major streaming platforms build their recommendation systems. These algorithms process billions of interactions daily, and we wanted to learn those same techniques. This project is ideal for our course because it combines big data processing, machine learning, web development, and database management in one cohesive system.

Third, most recommendation systems are opaque — users receive suggestions without explanation. With CineMatch, we incorporated transparency by showing users why a movie was recommended (e.g., based on similar movies they rated highly).

Additionally, as computer science students, we wanted to build something open source that others could learn from or improve.

### 2.2 Main Problems We Identified

From our research and experience, we identified four main issues with existing platforms:

1. **Volume Saturation** — There are too many movies and too much data. Simple algorithms cannot handle millions of ratings efficiently.
2. **Cognitive Load** — Manual browsing is overwhelming. Users get paralyzed by too many choices.
3. **Generic Recommendations** — Most platforms simply show trending lists that are identical for everyone.
4. **Algorithmic Opacity** — Users receive suggestions without understanding the logic behind them.

These problems are exactly what we aimed to solve with CineMatch.

### 2.3 Problem Statement

The core problem we solved is:

> Existing movie platforms struggle to deliver personalized, fast, and transparent recommendations because they either use simple methods that do not scale or complex algorithms that are not interpretable. Users cannot easily find content they enjoy, and developers face difficulties processing large datasets efficiently.

Our goal was to build a system that addresses all these issues using modern data science and software engineering practices.

### 2.4 Research Questions

Throughout this project, we asked ourselves:

- How can we process 32 million ratings efficiently without excessive memory usage?
- Which algorithm performs best for implicit user-item interaction data at scale?
- How do we ensure recommendations are fast enough for a live website?
- How can AI-powered search be accurate without hallucinating fake movies?
- How do we handle new users who have no rating history?
- How should the codebase be structured for maintainability and easy deployment?

We answer each of these questions in the sections that follow.

---

## 3. Research Methodology

### 3.1 Overall Approach

We followed a standard research and development lifecycle: Plan, Collect Data, Clean and Process, Train Model, Build API, Build Frontend, Integrate, Test, Deploy. Every step was incremental, and we used Git for version control throughout.

### 3.2 Data Collection and Preparation

We used the MovieLens 32M dataset, freely available from GroupLens Research. It contains four files:

- `ratings.csv`: 32,000,204 ratings (userId, movieId, rating, timestamp)
- `movies.csv`: 87,585 movie titles and pipe-separated genres
- `tags.csv`: 2,000,072 user-generated tags
- `links.csv`: External ID mappings to IMDb and TMDB

Before training, we cleaned the data:

1. **Filtering** — Removed users with fewer than 20 ratings and movies with fewer than 50 ratings. This eliminates noise and focuses on high-quality interaction data.

2. **Time-based Split** — We split the data into 80% training and 20% testing based on timestamp ordering per user. This is critical because it simulates real-world conditions: we train on past behavior and predict future preferences.

3. **Sparse Matrix Construction** — We built a user-item interaction matrix. With 200K users and 16K movies, this matrix has 3.2 billion cells, but only 31.5 million are populated (99.8% sparsity). We used SciPy's Compressed Sparse Row (CSR) format to store only non-zero values, reducing memory from an impossible ~250 GB to approximately 400 MB.

After cleaning, we retained 31.5 million valid ratings, 200,947 active users, and 16,034 movies — 98.4% of ratings preserved while eliminating tail noise.

### 3.3 Recommendation Algorithm: ALS

We chose Alternating Least Squares (ALS) for collaborative filtering. ALS factorizes the user-item interaction matrix R into two lower-dimensional matrices:

- X (users × factors): user latent factors
- Y (items × factors): item latent factors

The objective is to approximate R ≈ X · Y^T. ALS alternates between fixing Y and solving for X (and vice versa), with each sub-problem being a weighted least-squares regression solvable in closed form.

We used the binary implicit feedback formulation (Hu, Koren, Volinsky 2008):

- **Preference** p_ui = 1 if rating ≥ 4.0, else 0
- **Confidence** c_ui = 1 + α × p_ui (alpha = 20)

This treats unobserved interactions as negative with low confidence rather than assuming all unrated items are negative.

### 3.4 AI Search and Discovery

For natural language search, we used TF-IDF vectorization from scikit-learn. We combined each movie's title, genres, and TMDB overview into a single text document, then built a vocabulary of 20,000 features across all 87,585 movies using TfidfVectorizer with unigram and bigram n-grams.

When a user types a query, it is transformed using the same vocabulary, and cosine similarity is computed against all movie vectors. The top 30 results are then sent to Google Gemini 2.5 Flash as catalog context, along with the user's query. Gemini returns 3–5 recommendations with explanations. Crucially, by restricting Gemini to select only from the pre-filtered 30 movies, we eliminate hallucination — the AI cannot invent movies that do not exist in our catalog.

This entire pipeline loads at application startup and runs entirely in memory (~50 MB for the TF-IDF matrix).

### 3.5 System Architecture

The system follows a layered architecture:

```
Presentation Layer:    React SPA (port 5173) with Tailwind CSS
API Layer:             FastAPI with 18 endpoints running on Uvicorn
Model Layer:           ALS model + TF-IDF index loaded in memory
Data Layer:            SQLite database (users, ratings, watchlists, watchlist_items)
External Services:     TMDB API (posters + descriptions), Gemini API (AI chat)
```

**Key data flow:**

1. The ALS model is trained once offline on MovieLens 32M and saved as `als_model.pkl`
2. At runtime, the model is loaded into memory along with movie metadata and the TF-IDF index
3. User ratings are stored in SQLite and used to build a temporary user vector for `model.recommend()`
4. AI chat queries are processed via TF-IDF search, then passed to Gemini
5. All external API data (TMDB posters, descriptions) is cached in JSON files to avoid repeated API calls

The entire system runs in Docker containers orchestrated by Docker Compose and deployed via Cloudflare Tunnel.

### 3.6 Evaluation Methods

We used standard ranking metrics for implicit-feedback recommenders:

- **Precision@K** — Fraction of recommended items that are relevant
- **Recall@K** — Fraction of relevant items that appear in the top K
- **MAP@K** — Mean Average Precision, which accounts for the ranking position of relevant items

Evaluation was performed using leave-one-out: for each of 5,000 sampled users, one liked item (rating ≥ 4.0) was held out, and the model was asked to rank all unrated items. If the held-out item appeared in the top K, it counted as a hit.

---

## 4. Tools and Technologies

### 4.1 Overview

We chose every tool carefully based on four criteria: industry adoption, open-source availability, performance at scale, and learning value for our careers. All dependencies are listed in our repository's `requirements.txt` and `package.json`.

### 4.2 Data Processing and Machine Learning

**Python 3.9.6** — The main programming language. Python dominates data science and machine learning, with a mature ecosystem of numerical libraries.

**Pandas and NumPy** — Pandas was used for data loading, exploration, filtering, and transformation. NumPy provided the numerical foundation for all matrix operations.

**SciPy Sparse Module** — Essential for memory-efficient storage of the 99.8% sparse user-item matrix. The CSR format stores only non-zero entries, reducing memory from ~250 GB to ~400 MB.

**Implicit Library** — A fast, optimized implementation of ALS for implicit feedback data. We configured it with factors=256, regularization=0.1, alpha=20, and trained for 20 iterations. The trained model (221 MB) includes the factor matrices, ID mappings, and movie metadata, all saved as a single pickle file.

**Scikit-Learn** — Used for TF-IDF vectorization (TfidfVectorizer with 20,000 features, English stop words, unigram+bigram n-grams) and cosine similarity computation.

### 4.3 Backend Development

**FastAPI** — Chosen for its async support, automatic OpenAPI documentation, Pydantic-based validation, and strong performance. It serves 18 API endpoints covering movies, recommendations, ratings, users, watchlists, similar items, group recommendations, and AI chat.

**Uvicorn** — ASGI server for running FastAPI. Lightweight and production-ready.

**Pydantic** — Data validation schemas ensuring type safety across all API inputs and outputs.

### 4.4 Frontend Development

**React 18 + Vite** — React provides a component-based UI architecture. Vite offers fast development server startup and optimized production builds.

**Tailwind CSS** — Utility-first CSS framework for rapid, consistent styling without separate CSS files.

**React Router** — Client-side routing between Home, Movie Detail, Recommendations, Profile, Watchlists, and Group Mode pages.

**Axios** — HTTP client for API communication with the FastAPI backend.

### 4.5 Database

**SQLite** — File-based, zero-configuration database. Ideal for this project scope. Schema includes:

- `users` — id, username, display_name, created_at
- `ratings` — user_id, movie_id, rating, created_at
- `watchlists` — user_id, name, created_at
- `watchlist_items` — watchlist_id, movie_id, added_at

Indexes on foreign key columns accelerate JOIN operations. Movie metadata is not stored in SQLite — it is loaded from the model pickle and CSV files.

### 4.6 External APIs

**TMDB API** — Provides movie poster URLs and descriptions (overview + tagline). We batch-fetched these for all 16,034 filtered movies at ~20 requests/second and cached the results in `posters.json` and `descriptions.json`. A `--retry-failed` flag allows re-fetching only null/empty entries.

**Google Gemini 2.5 Flash** — Powers the AI chat feature. We use it for natural language understanding only — it selects from a pre-filtered list of 30 movies from our catalog, preventing hallucination.

### 4.7 DevOps and Deployment

**Docker + Docker Compose** — Two containers (backend + frontend) orchestrated by Docker Compose. The backend Dockerfile includes `libgomp1` for the implicit C extension. Host volumes mount `./models:/models` and `./data:/data` for persistence. A single `docker compose up --build -d` command starts the entire application.

**Nginx** — Serves as a reverse proxy. It serves frontend static assets, proxies `/api/*` requests to the backend (stripping the `/api` prefix), and routes all other requests to the SPA. `proxy_buffering off` is configured for the AI chat streaming endpoint.

**Cloudflare Tunnel** — Provides HTTPS access without open ports. Routes `cinematch.mironshoh.me` to the local Docker instance.

---

## 5. Data Analysis

### 5.1 Introduction

Data analysis was the foundation of our project. Before building any models, we needed to understand the data, clean it, and find optimal hyperparameters. All steps are documented in our Jupyter notebooks.

### 5.2 Understanding the Raw Dataset

The MovieLens 32M dataset contains:

| Metric | Value |
|--------|-------|
| Total ratings | 32,000,204 |
| Unique movies | 87,585 (1915–2019) |
| Unique users | 2,000,072 |
| Rating scale | 0.5–5.0 (0.5 increments) |
| Time range | January 1995 – November 2019 |

#### 5.2.1 Rating Distribution

The rating distribution is left-skewed:

- Most common ratings: 3.0, 3.5, 4.0, and 4.5
- Very few ratings below 2.0 — users tend to rate only movies they have watched, which creates a positive selection bias
- Ratings of 5.0 are relatively rare

This distribution motivated our binary implicit approach (rating ≥ 4.0 = positive), since the data is already skewed toward positive signals.

#### 5.2.2 Genre Analysis

The most frequent genres in the dataset are Drama (~40% of movies), Comedy (~30%), Action (~20%), Thriller (~15%), and Romance (~15%). Rare genres include Film-Noir, IMAX, and Western. This means the model learns better for common genres, which is an expected limitation.

#### 5.2.3 User Activity

Most users rated between 20 and 200 movies. After filtering (minimum 20 ratings per user), we retained 200,947 active users. The long tail of users with very few ratings was removed to improve model quality.

### 5.3 Data Cleaning and Filtering

#### 5.3.1 Filtering Criteria

- Remove users with fewer than 20 ratings
- Remove movies with fewer than 50 ratings

**Results:**

| Metric | Before | After |
|--------|--------|-------|
| Users | 2,000,072 | 200,947 |
| Movies | 87,585 | 16,034 |
| Ratings | 32,000,204 | 31,498,689 (98.4% retained) |

We preserved nearly all ratings while eliminating noisy users and movies.

#### 5.3.2 Train/Test Split

We used a time-based split (not random) to simulate realistic evaluation:

- Training set: earliest 80% of ratings per user
- Test set: most recent 20% of ratings per user

This respects temporal ordering — we train on past behavior and predict future preferences.

### 5.4 Sparse Matrix Construction

The user-item matrix dimensions are 200,947 × 16,034 = 3.2 billion cells, but only 31.5 million (0.6%) contain ratings. Storing this as a dense matrix would require approximately 250 GB of RAM.

**Solution:** Compressed Sparse Row (CSR) format from SciPy. This stores only three arrays: data values, column indices, and row pointers. Memory usage: approximately 400 MB. All subsequent operations (factorization, prediction) operate directly on the sparse representation.

### 5.5 Model Training and Hyperparameter Tuning

#### 5.5.1 Hyperparameter Grid

We tested the following combinations:

| Parameter | Values Tested | Description |
|-----------|--------------|-------------|
| Factors | 64, 128, 256 | Number of latent dimensions |
| Regularization | 0.01, 0.05, 0.1 | L2 regularization strength |
| Alpha | 20, 40, 80 | Confidence scaling for implicit feedback |

All models were trained for 20 iterations.

#### 5.5.2 Best Configuration

| Parameter | Value |
|-----------|-------|
| Factors | 256 |
| Regularization | 0.1 |
| Alpha | 20 |
| Iterations | 20 |
| Rating threshold | ≥ 4.0 (binary like) |

Training the best model took approximately 15 minutes on a laptop with 12 CPU threads.

#### 5.5.3 Model Persistence

The trained model is saved as `als_model.pkl` (221 MB), containing:
- The ALS model object (user and item factor matrices)
- `user_id_to_idx` and `movie_id_to_idx` mapping dictionaries
- `idx_to_movie_id` reverse mapping
- `movie_meta` dictionary (movieId → title, genres)
- Training configuration parameters

This is loaded at application startup and remains in memory.

### 5.6 Similarity Calculation

For the "Similar Movies" feature, we compute cosine similarity between item factor vectors:

```
similarity(i, j) = (y_i · y_j) / (||y_i|| × ||y_j||)
```

This returns values from 0 (not similar) to 1 (identical). The `model.similar_items()` method from the implicit library performs this computation efficiently.

---

## 6. Results and Discussion

### 6.1 Introduction

In this section, we present the model evaluation results, describe the working features of the application, discuss challenges faced, and reflect on what we learned.

### 6.2 Model Performance Evaluation

#### 6.2.1 Evaluation Protocol

We used leave-one-out evaluation: for 5,000 sampled users, one liked item (rating ≥ 4.0, latest by timestamp) was held out. The model ranked all unrated items, and we measured whether the held-out item appeared in the top K.

#### 6.2.2 Results

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Precision@10 | 0.0541 | ~0.5 of 10 recommendations match the held-out item |
| Recall@10 | 0.5408 | 54% of users had their held-out item in the top 10 |
| MAP@10 | **0.3006** | Relevant items appear at position ~3 on average |

These results are competitive with published benchmarks for ALS-based recommenders on MovieLens data.

#### 6.2.3 RMSE and MSE

Since ALS with implicit feedback is a ranking model, not a rating predictor, RMSE is not the primary evaluation metric. However, for reference:

| Metric | Value |
|--------|-------|
| RMSE (binary label, raw scores) | 0.489 |
| RMSE (min-max scaled to 0.5–5.0) | 0.865 |
| MAE (min-max scaled) | 0.692 |

These values are expectedly high because the model optimizes for ranking (MAP@K), not for minimizing squared error against rating values.

### 6.3 System Features and Functionality

CineMatch includes the following working features:

1. **Home Page** — Displays movies with poster images. Includes a search bar (by title) and genre dropdown filter. Results are paginated.

2. **Movie Detail Page** — Shows poster, title, genres, overview, and tagline from TMDB. Users can rate the movie (0.5–5 stars) and add it to a watchlist. A "Similar Movies" section shows 10 related movies computed from ALS item factors.

3. **Personalized Recommendations** — For users with ratings, builds a user vector from their SQLite history and calls `model.recommend()` to generate 20 personalized suggestions. For new users (empty history), the model defaults to globally popular items.

4. **AI Chat** — Floating chat bubble on every page. Users type natural language queries. The system performs TF-IDF semantic search over all 87,585 movie descriptions, sends the top 30 results to Gemini 2.5 Flash, and streams the AI response via Server-Sent Events. No hallucination — Gemini can only recommend movies from our catalog.

5. **Group Mode** — Merge multiple users' rating histories by averaging per-movie scores, then generate recommendations for the combined group. Useful for finding movies everyone will enjoy.

6. **Watchlists** — Create, rename, and delete named watchlists. Add or remove movies. Each user can maintain multiple lists (e.g., "To Watch", "Favorites").

7. **User Profile** — Auto-created on first visit (INSERT OR IGNORE). Editable username and display name. Shows rating history with star display.

8. **Social Sharing** — Share button on movie cards and detail pages using the Web Share API (fallback to clipboard copy).

9. **Responsive Design** — Works on desktop, tablet, and mobile.

### 6.4 Challenges Faced and Solutions

**Problem 1: Memory Limit**  
*Issue:* Loading 32 million ratings as a dense matrix would require ~250 GB of RAM.  
*Solution:* Used SciPy Compressed Sparse Row (CSR) format, reducing memory to ~400 MB.

**Problem 2: Cold Start**  
*Issue:* New users have no rating history, so collaborative filtering cannot generate personalized recommendations.  
*Solution:* The ALS model with an empty user vector returns globally high-scored items (popularity-based). After the user rates a few movies, recommendations become personalized.

**Problem 3: AI Hallucinations**  
*Issue:* Gemini would occasionally recommend movies that do not exist in our catalog.  
*Solution:* We restrict Gemini's output space. The system first retrieves the top 30 matching movies from our catalog using TF-IDF, then sends only those 30 as context. Gemini selects from this restricted list — it cannot invent titles.

**Problem 4: Model Not Updating**  
*Issue:* New user ratings are stored in SQLite but do not retrain the ALS model.  
*Solution:* At inference time, the user's ratings are used to build a temporary user vector, which is passed to `model.recommend()`. The model's item factors remain static, but the user vector shifts recommendations toward items similar to what the user has liked.

**Problem 5: Deployment Complexity**  
*Issue:* Setting up dependencies across different machines was inconsistent.  
*Solution:* Docker containers with a single `docker compose up` command. The backend container includes `libgomp1` for the implicit C extension.

**Problem 6: Gemini API Rate Limits**  
*Issue:* Free tier Gemini has daily quota and per-minute rate limits (429 errors under sustained testing).  
*Solution:* Rate limit errors are surfaced to the user. The system falls back gracefully.

### 6.5 What Worked Well

- **ALS Algorithm** — Fast training (~15 minutes), fast inference (~50 ms per user), and strong ranking metrics (MAP@10 = 0.3006)
- **TF-IDF Search** — ~50 ms on 87,585 documents, zero model files to manage, automatically reflects updated descriptions on restart
- **Tech Stack** — Every tool performed as expected. FastAPI's async support was especially valuable for the SSE streaming endpoint.
- **Docker Compose** — Simplified deployment dramatically. New contributors can run the entire system with one command.
- **API Documentation** — FastAPI's automatic OpenAPI docs at `/docs` made testing and debugging straightforward.

### 6.6 Limitations

1. **Static Model** — The ALS model is trained once and never updated. A production system would benefit from periodic retraining or online learning.
2. **Dataset Boundary** — Recommendations are limited to the MovieLens catalog (pre-2019). Newer movies are not included.
3. **No Content Features** — The model uses only collaborative filtering. Incorporating content features (actors, directors, plot keywords) would improve cold-start performance and recommendation diversity.
4. **No Distributed Training** — We used a single machine. Training on a Spark cluster would allow processing larger datasets and more extensive hyperparameter search.
5. **Free API Rate Limits** — Gemini's free tier quota can be exhausted under heavy use, requiring a paid upgrade for production deployment.

---

## 7. Conclusion

### 7.1 Summary of the Project

We successfully built CineMatch, a full-stack movie recommendation engine, from scratch. We started with 32 million raw ratings, cleaned and processed the data using sparse matrix techniques, trained an ALS model with hyperparameter optimization, built a modern web interface with React, integrated AI-powered natural language search with Gemini, and deployed the entire system using Docker and Cloudflare Tunnel.

Every objective we set was achieved:

- Processed 32 million ratings efficiently using sparse matrix formats
- Implemented industry-standard collaborative filtering with ALS
- Built personalized recommendations with sub-second inference time
- Created a responsive, user-friendly web application
- Added AI-powered natural language search without hallucination
- Solved cold start and performance challenges
- Made the project open source and well-documented

The system achieves a MAP@10 of 0.3006, which is competitive with published benchmarks for ALS recommenders on the MovieLens dataset.

### 7.2 Key Learnings

This project taught us far more than just programming:

- **Big data in practice** — How to process, store, and analyze millions of records efficiently using sparse representations
- **Recommendation system theory** — Deep understanding of collaborative filtering, matrix factorization, implicit feedback, and cold start
- **Full-stack integration** — Connecting a Python machine learning model to a JavaScript frontend through a REST API
- **System design** — Choosing appropriate tools, structuring code for maintainability, and containerizing for deployment
- **Problem solving** — Overcoming real-world challenges including memory constraints, API rate limits, and AI hallucination
- **Teamwork** — Dividing responsibilities across data processing, model training, backend, frontend, testing, and deployment

### 7.3 Future Improvements

1. **Hybrid Model** — Combine collaborative filtering with content-based features (actors, directors, plot) for improved cold-start and diversity
2. **Distributed Training** — Port the training pipeline to Apache Spark for larger datasets and faster hyperparameter search
3. **Online Learning** — Implement incremental model updates so new ratings immediately affect recommendations
4. **User Explanations** — Show specifically which rated movie triggered each recommendation (e.g., "Because you liked The Matrix")
5. **Social Features** — Friend following, shared watchlists, and social recommendations
6. **Mobile App** — Build a React Native mobile version

### 7.4 Final Thoughts

Building CineMatch was one of the most rewarding experiences of our studies. It demonstrated that the concepts we learn in class — matrix factorization, sparse computation, REST APIs, containerization — are not just academic exercises. They are the building blocks of real systems used by millions of people.

We are proud of what we built. This project is a concrete example of how big data, machine learning, and software engineering come together to solve a practical problem. Everything is open source on GitHub, and we welcome contributions from anyone who wants to learn or improve upon our work.

---

## 8. References

1. Hu, Y., Koren, Y., & Volinsky, C. (2008). *Collaborative Filtering for Implicit Feedback Datasets*. IEEE International Conference on Data Mining (ICDM).
2. Harper, F. M., & Konstan, J. A. (2016). *The MovieLens Datasets: History and Context*. ACM Transactions on Interactive Intelligent Systems.
3. implicit library: https://github.com/benfred/implicit
4. FastAPI: https://fastapi.tiangolo.com/
5. MovieLens 32M Dataset: https://grouplens.org/datasets/movielens/32m/
6. TMDB API: https://developers.themoviedb.org/3
7. Gemini API: https://ai.google.dev/
8. Scikit-learn TfidfVectorizer: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
