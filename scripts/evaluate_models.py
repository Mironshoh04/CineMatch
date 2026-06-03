import os
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from implicit.als import AlternatingLeastSquares

os.environ['OPENBLAS_NUM_THREADS'] = '1'

processed_dir = Path('data/processed')
full_dir = Path('data/full_dataset')

# ── Load data ──
print('Loading data...')
ratings_f = pd.read_csv(processed_dir / 'ratings_filtered.csv')

if not pd.api.types.is_datetime64_any_dtype(ratings_f['timestamp']):
    ratings_f['timestamp'] = pd.to_datetime(ratings_f['timestamp'])

# Build idx mappings
user_ids = ratings_f['userId'].unique()
movie_ids = ratings_f['movieId'].unique()
user_id_to_idx = {uid: i for i, uid in enumerate(user_ids)}
movie_id_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
ratings_f['user_idx'] = ratings_f['userId'].map(user_id_to_idx)
ratings_f['movie_idx'] = ratings_f['movieId'].map(movie_id_to_idx)
n_users, n_movies = len(user_ids), len(movie_ids)
print(f'Users: {n_users}, Movies: {n_movies}')

# ── Leave-one-out split (rating >= 4.0 as relevance) ──
relevance = ratings_f[ratings_f['rating'] >= 4.0].sort_values(['user_idx', 'timestamp'])
test_holdout = relevance.groupby('user_idx').tail(1)
test_users = test_holdout['user_idx'].unique()
print(f'Total users with >=4.0 ratings: {len(test_users)}')

# Sample 5000 users for eval
rng = np.random.default_rng(42)
eval_users = rng.choice(test_users, size=min(5000, len(test_users)), replace=False)
test_sample = test_holdout[test_holdout['user_idx'].isin(eval_users)]
print(f'Sampled {len(test_sample)} users for evaluation')

# ── Training set: exclude all test items ──
test_indices = test_sample.index
train_set = relevance.drop(test_indices)

# Also include 3.5-4.0 ratings for v2 but NOT for v1
extra_pos = ratings_f[(ratings_f['rating'] >= 3.5) & (ratings_f['rating'] < 4.0)]

# ── Hyperparams ──
BEST_FACTORS = 256
BEST_REG = 0.1
BEST_ALPHA = 20
ITERATIONS = 20

# ── Build v1 matrix (binary >=4.0 train) ──
X_v1 = csr_matrix(
    (np.ones(len(train_set), dtype=np.float32), (train_set['user_idx'], train_set['movie_idx'])),
    shape=(n_users, n_movies)
)
print(f'v1 train shape: {X_v1.shape}, non-zeros: {X_v1.nnz}')

# ── Build v2 matrix (confidence-weighted >=3.5 train) ──
v2_parts = [
    (train_set['user_idx'].values, train_set['movie_idx'].values,
     1.0 + (train_set['rating'].values - 3.5)),  # >=4.0 → conf > 1.5
    (extra_pos['user_idx'].values, extra_pos['movie_idx'].values,
     1.0 + (extra_pos['rating'].values - 3.5)),  # 3.5-4.0 → conf 1.0-1.5
]
v2_users = np.concatenate([p[0] for p in v2_parts])
v2_movies = np.concatenate([p[1] for p in v2_parts])
v2_vals = np.concatenate([p[2] for p in v2_parts]).astype(np.float32)

X_v2 = csr_matrix((v2_vals, (v2_users, v2_movies)), shape=(n_users, n_movies))
print(f'v2 train shape: {X_v2.shape}, non-zeros: {X_v2.nnz}')

# ── Evaluation function ──
def evaluate_model(model, X_mat, test_df, k=10):
    users = test_df['user_idx'].unique()
    test_map = test_df.set_index('user_idx')['movie_idx'].to_dict()
    precisions, recalls, aps = [], [], []
    for user_idx in users:
        relevant = {test_map[user_idx]}
        recs = model.recommend(user_idx, X_mat[user_idx], N=k, filter_already_liked_items=True)
        if isinstance(recs, tuple):
            recs_items = [int(r) for r in recs[0]]
        else:
            recs_items = [int(r[0]) for r in recs]
        hits = [1 if r in relevant else 0 for r in recs_items]
        precisions.append(sum(hits) / k)
        recalls.append(sum(hits) / len(relevant))
        cum = 0
        ap = 0.0
        for i, h in enumerate(hits, 1):
            if h:
                cum += 1
                ap += cum / i
        aps.append(ap / min(len(relevant), k))
    return {
        'precision@10': float(np.mean(precisions)),
        'recall@10': float(np.mean(recalls)),
        'map@10': float(np.mean(aps)),
        'users_evaluated': len(precisions)
    }

# ── Train and evaluate v1 ──
print('\n── Training v1 (binary >=4.0) ──')
model1 = AlternatingLeastSquares(factors=BEST_FACTORS, regularization=BEST_REG,
                                  iterations=ITERATIONS, random_state=42)
t0 = time.time()
model1.fit(X_v1 * BEST_ALPHA)
print(f'v1 training: {time.time() - t0:.0f}s')

print('Evaluating v1...')
t0 = time.time()
r1 = evaluate_model(model1, X_v1, test_sample, k=10)
print(f'v1 eval: {time.time() - t0:.0f}s')

# ── Train and evaluate v2 ──
print('\n── Training v2 (conf-weighted >=3.5) ──')
model2 = AlternatingLeastSquares(factors=BEST_FACTORS, regularization=BEST_REG,
                                  iterations=ITERATIONS, random_state=42)
t0 = time.time()
model2.fit(X_v2 * BEST_ALPHA)
print(f'v2 training: {time.time() - t0:.0f}s')

print('Evaluating v2...')
t0 = time.time()
r2 = evaluate_model(model2, X_v2, test_sample, k=10)
print(f'v2 eval: {time.time() - t0:.0f}s')

# ── Results ──
print('\n' + '='*70)
print('COMPARISON (proper leave-one-out, no leakage)')
print('='*70)
for label, r in [('v1 (binary >=4.0)', r1), ('v2 (conf-weighted >=3.5)', r2)]:
    print(f'{label:>30s}  prec@10={r["precision@10"]:.4f}  '
          f'recall@10={r["recall@10"]:.4f}  '
          f'map@10={r["map@10"]:.4f}  users={r["users_evaluated"]}')

winner = 'v1' if r1['map@10'] > r2['map@10'] else 'v2'
print(f'\nWinner by MAP@10: {winner}')
