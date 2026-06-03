const API_BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export function getMovies(page = 1, perPage = 50) {
  return request(`/movies?page=${page}&per_page=${perPage}`)
}

export function searchMovies(query) {
  return request(`/movies/search?q=${encodeURIComponent(query)}`)
}

export function getRecommendations(userId, k = 10) {
  return request(`/recommendations/user/${userId}?k=${k}`)
}

export function getSimilarMovies(movieId) {
  return request(`/recommendations/similar/${movieId}`)
}

export function submitRating(userId, movieId, rating) {
  return request('/ratings', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, movie_id: movieId, rating }),
  })
}
