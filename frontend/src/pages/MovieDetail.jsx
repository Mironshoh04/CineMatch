import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getSimilarMovies, submitRating } from '../services/api'
import MovieRow from '../components/MovieRow'
import RatingModal from '../components/RatingModal'

export default function MovieDetail() {
  const { id } = useParams()
  const [meta, setMeta] = useState(null)
  const [similar, setSimilar] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    getSimilarMovies(id).then(setSimilar)
    // Load movie metadata from similar results or a separate lookup
    // For now, store the movie from the similar list
    setMeta(null)
  }, [id])

  useEffect(() => {
    if (similar.length > 0) {
      setMeta(similar.find((s) => s.movie.movie_id === Number(id))?.movie || similar[0].movie)
    }
  }, [similar, id])

  const handleRate = async (movieId, rating) => {
    await submitRating(1, movieId, rating)
    setShowModal(false)
    setMessage('Thanks for rating!')
    setTimeout(() => setMessage(''), 3000)
  }

  return (
    <div className="detail">
      <div className="header">
        <div className="poster-placeholder">
          <span>{meta?.title?.charAt(0) || '?'}</span>
        </div>
        <div className="meta">
          <h1>{meta?.title || 'Loading...'}</h1>
          <div className="genres">{meta?.genres?.replace(/\|/g, ' · ')}</div>
          <div style={{ display: 'flex', gap: '.75rem' }}>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Rate</button>
          </div>
          {message && <p style={{ marginTop: '1rem', color: '#4ade80' }}>{message}</p>}
        </div>
      </div>
      <MovieRow title="Similar Movies" movies={similar.map((s) => s.movie)} />
      {showModal && (
        <RatingModal
          movie={meta || { movie_id: Number(id), title: '' }}
          onClose={() => setShowModal(false)}
          onSubmit={handleRate}
        />
      )}
    </div>
  )
}
