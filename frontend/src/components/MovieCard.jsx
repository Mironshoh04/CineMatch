import { useNavigate } from 'react-router-dom'

export default function MovieCard({ movie, onRate }) {
  const navigate = useNavigate()

  return (
    <div className="movie-card" onClick={() => navigate(`/movie/${movie.movie_id}`)}>
      <div className="poster">
        <span>{movie.title?.charAt(0) || '?'}</span>
      </div>
      <div className="info">
        <h3>{movie.title}</h3>
        <div className="genres">{movie.genres?.replace(/\|/g, ' · ')}</div>
      </div>
    </div>
  )
}
