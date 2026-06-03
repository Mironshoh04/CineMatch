import { useState, useEffect } from 'react'
import { getMovies } from '../services/api'
import MovieCard from '../components/MovieCard'

export default function Home() {
  const [movies, setMovies] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getMovies(page, 50)
      .then((data) => { setMovies(data.movies); setTotal(data.total) })
      .finally(() => setLoading(false))
  }, [page])

  if (loading) return <div className="spinner" />

  return (
    <div>
      <div className="movie-grid">
        {movies.map((m) => (
          <MovieCard key={m.movie_id} movie={m} />
        ))}
      </div>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', padding: '2rem 0' }}>
        <button className="btn btn-outline" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          Previous
        </button>
        <span style={{ alignSelf: 'center', color: '#888' }}>Page {page} of {Math.ceil(total / 50)}</span>
        <button className="btn btn-outline" disabled={page >= Math.ceil(total / 50)} onClick={() => setPage((p) => p + 1)}>
          Next
        </button>
      </div>
    </div>
  )
}
