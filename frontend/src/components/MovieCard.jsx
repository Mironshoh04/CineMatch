import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function MovieCard({ movie, onRate }) {
  const navigate = useNavigate()
  const [imgError, setImgError] = useState(false)

  return (
    <div className="movie-card" onClick={() => navigate(`/movie/${movie.movie_id}`)}>
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
  )
}
