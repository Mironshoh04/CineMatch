import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getSimilarMovies, submitRating, getWatchlists, addWatchlistItem, shareMovie } from '../services/api'
import MovieRow from '../components/MovieRow'
import RatingModal from '../components/RatingModal'
import AddToWatchlist from '../components/AddToWatchlist'

export default function MovieDetail() {
  const { id } = useParams()
  const [meta, setMeta] = useState(null)
  const [similar, setSimilar] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [message, setMessage] = useState('')
  const [imgError, setImgError] = useState(false)
  const [watchlists, setWatchlists] = useState([])

  useEffect(() => {
    getSimilarMovies(id).then(setSimilar)
    setMeta(null)
    setImgError(false)
    const userId = localStorage.getItem('cinematch_user_id')
    getWatchlists(userId).then(setWatchlists).catch(() => {})
  }, [id])

  useEffect(() => {
    if (similar.length > 0) {
      setMeta(similar.find((s) => s.movie.movie_id === Number(id))?.movie || similar[0].movie)
    }
  }, [similar, id])

  const handleRate = async (movieId, rating) => {
    const userId = localStorage.getItem('cinematch_user_id') || '1'
    await submitRating(userId, movieId, rating)
    setShowModal(false)
    setMessage('Thanks for rating!')
    setTimeout(() => setMessage(''), 3000)
  }

  const handleAddToWatchlist = async (watchlistId) => {
    try {
      await addWatchlistItem(watchlistId, Number(id))
      setMessage('Added to watchlist!')
    } catch {
      setMessage('Already in watchlist')
    }
    setTimeout(() => setMessage(''), 3000)
  }

  return (
    <div className="detail">
      <div className="header">
        {meta?.poster_url && !imgError ? (
          <img
            className="detail-poster"
            src={meta.poster_url}
            alt={meta.title}
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="poster-placeholder">
            <span>{meta?.title?.charAt(0) || '?'}</span>
          </div>
        )}
        <div className="meta">
          <h1>{meta?.title || 'Loading...'}</h1>
          <div className="genres">{meta?.genres?.replace(/\|/g, ' · ')}</div>
          <div className="detail-actions">
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Rate</button>
            <button className="btn btn-outline" onClick={() => shareMovie(meta)}>Share</button>
            <AddToWatchlist watchlists={watchlists} onSelect={handleAddToWatchlist} />
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
