import { useState, useEffect } from 'react'
import { getMovies, getGenres } from '../services/api'
import MovieCard from '../components/MovieCard'

export default function Home() {
  const [movies, setMovies] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [genres, setGenres] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedGenre, setSelectedGenre] = useState('')
  const [activeSearch, setActiveSearch] = useState('')
  const [activeGenre, setActiveGenre] = useState('')

  useEffect(() => {
    getGenres().then(setGenres).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    getMovies(page, 50, { q: activeSearch, genre: activeGenre })
      .then((data) => { setMovies(data.movies); setTotal(data.total) })
      .finally(() => setLoading(false))
  }, [page, activeSearch, activeGenre])

  function handleSearch(e) {
    e.preventDefault()
    setPage(1)
    setActiveSearch(searchQuery)
    setActiveGenre(selectedGenre)
  }

  function handleGenreChange(e) {
    const genre = e.target.value
    setSelectedGenre(genre)
    setPage(1)
    setActiveSearch(searchQuery)
    setActiveGenre(genre)
  }

  return (
    <div>
      <form className="filter-bar" onSubmit={handleSearch}>
        <input
          type="text"
          className="search-input"
          placeholder="Search movies..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <select className="genre-select" value={selectedGenre} onChange={handleGenreChange}>
          <option value="">All Genres</option>
          {genres.map((g) => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
        <button type="submit" className="btn btn-primary">Search</button>
      </form>

      {loading ? (
        <div className="spinner" />
      ) : (
        <>
          <p style={{ color: '#888', marginBottom: '.5rem' }}>
            {total} movie{total !== 1 ? 's' : ''} found
          </p>
          <div className="movie-grid">
            {movies.length === 0 && <p style={{ color: '#888' }}>No movies match your criteria.</p>}
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
        </>
      )}
    </div>
  )
}
