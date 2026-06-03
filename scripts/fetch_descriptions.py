import argparse
import json
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import pandas as pd

from config import TMDB_API_KEY, ROOT

TMDB_BASE = "https://api.themoviedb.org/3/movie"

links_path = ROOT / "data/full_dataset/links.csv"
filtered_ids_path = ROOT / "data/processed/movie_id_to_idx.csv"
output_path = ROOT / "data/processed/descriptions.json"

parser = argparse.ArgumentParser()
parser.add_argument("--retry-failed", action="store_true", help="Retry entries with empty overview")
args = parser.parse_args()

filtered_ids = pd.read_csv(filtered_ids_path, header=None, index_col=0).index.tolist()
print(f"Filtered movies: {len(filtered_ids)}")

links = pd.read_csv(links_path)
links = links[links["movieId"].isin(filtered_ids)]
links = links[links["tmdbId"].notna()].drop_duplicates("movieId")
print(f"Movies with tmdbId: {len(links)}")

if output_path.exists():
    cache = json.loads(output_path.read_text())
    print(f"Existing cache: {len(cache)} entries")
else:
    cache = {}

total = len(links)
for i, (_, row) in enumerate(links.iterrows()):
    movie_id = int(row["movieId"])
    tmdb_id = int(row["tmdbId"])

    key = str(movie_id)
    if key in cache:
        if not args.retry_failed or cache[key].get("overview"):
            continue

    url = f"{TMDB_BASE}/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        req = Request(url, headers={"User-Agent": "CineMatch/1.0"})
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            cache[str(movie_id)] = {
                "overview": data.get("overview", "") or "",
                "tagline": data.get("tagline", "") or "",
            }
    except HTTPError as e:
        if e.code == 404:
            cache[str(movie_id)] = {"overview": "", "tagline": ""}
        else:
            print(f"  Error {e.code} for movie {movie_id} (tmdb {tmdb_id})")
            cache[str(movie_id)] = {"overview": "", "tagline": ""}
    except Exception as e:
        print(f"  Exception for movie {movie_id} (tmdb {tmdb_id}): {e}")
        cache[str(movie_id)] = {"overview": "", "tagline": ""}

    if (i + 1) % 50 == 0:
        output_path.write_text(json.dumps(cache))
        with_text = len([v for v in cache.values() if v.get("overview")])
        print(f"  [{i+1}/{total}] saved, {with_text} with overview")

    if (i + 1) % 20 == 0:
        time.sleep(1)

output_path.write_text(json.dumps(cache))
with_text = len([v for v in cache.values() if v.get("overview")])
print(f"\nDone! {with_text}/{total} with overview, saved to {output_path}")
