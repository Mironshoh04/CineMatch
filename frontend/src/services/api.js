const API_BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export function getMovies(page = 1, perPage = 50, params = {}) {
  const q = params.q ? `&q=${encodeURIComponent(params.q)}` : ''
  const genre = params.genre ? `&genre=${encodeURIComponent(params.genre)}` : ''
  return request(`/movies?page=${page}&per_page=${perPage}${q}${genre}`)
}

export function searchMovies(query) {
  return request(`/movies/search?q=${encodeURIComponent(query)}`)
}

export function getGenres() {
  return request('/movies/genres')
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

export function getUser(userId) {
  return request(`/users/${userId}`)
}

export function updateUser(userId, data) {
  return request(`/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export function getUserRatings(userId) {
  return request(`/users/${userId}/ratings`)
}

/* Watchlists */
export function getWatchlists(userId) {
  return request(`/watchlists/${userId}`)
}

export function createWatchlist(userId, name) {
  return request('/watchlists', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, name }),
  })
}

export function deleteWatchlist(watchlistId) {
  return request(`/watchlists/${watchlistId}`, { method: 'DELETE' })
}

export function getWatchlistItems(watchlistId) {
  return request(`/watchlists/${watchlistId}/items`)
}

export function addWatchlistItem(watchlistId, movieId) {
  return request(`/watchlists/${watchlistId}/items`, {
    method: 'POST',
    body: JSON.stringify({ movie_id: movieId }),
  })
}

export function removeWatchlistItem(watchlistId, movieId) {
  return request(`/watchlists/${watchlistId}/items/${movieId}`, { method: 'DELETE' })
}

/* Group */
export function getGroupRecommendations(userIds, k = 10) {
  return request('/recommendations/group', {
    method: 'POST',
    body: JSON.stringify({ user_ids: userIds, k }),
  })
}

/* Share */
export function shareMovie(movie) {
  const url = `${window.location.origin}/movie/${movie.movie_id}`
  if (navigator.share) {
    navigator.share({ title: movie.title, url }).catch(() => {})
  } else {
    navigator.clipboard.writeText(url)
  }
}

/* AI Chat */
export async function chatStream(message, history, onToken) {
  const res = await fetch(`${API_BASE}/ai/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  if (!res.ok) throw new Error(`Chat error: ${res.status}`)
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let done = false
  while (true) {
    const { done: streamEnd, value } = await reader.read()
    if (streamEnd) break
    const chunk = decoder.decode(value, { stream: true })
    if (chunk.endsWith('__DONE__')) {
      onToken(chunk.slice(0, -9))
      done = true
      break
    }
    if (chunk) onToken(chunk)
  }
  if (!done) onToken('\n\n_[Response truncated — try a more specific query]_')
}
