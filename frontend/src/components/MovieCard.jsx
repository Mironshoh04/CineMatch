import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { shareMovie } from '../services/api'

export default function MovieCard({ movie, onRate }) {
  const navigate = useNavigate()
  const [imgError, setImgError] = useState(false)

  return (
    <div className="movie-card">
      <div className="movie-card-poster" onClick={() => navigate(`/movie/${movie.movie_id}`)}>
        <div className="poster">
          {movie.poster_url && !imgError ? (
            <img
              src={movie.poster_url}
              alt={movie.title}
              loading="lazy"
              onError={() => setImgError(true)}
            />
          ) : (
            <span>{movie.title?.charAt(0) || '?'}</span>
          )}
        </div>
        <div className="info">
          <h3>{movie.title}</h3>
          <div className="genres">{movie.genres?.replace(/\|/g, ' · ')}</div>
        </div>
      </div>
      <div className="movie-card-actions">
        <button className="btn-icon" title="Share" onClick={(e) => { e.stopPropagation(); shareMovie(movie); }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
        </button>
      </div>
    </div>
  )
}
