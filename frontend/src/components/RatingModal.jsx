import { useState } from 'react'

export default function RatingModal({ movie, onClose, onSubmit }) {
  const [rating, setRating] = useState(0)
  const [hovered, setHovered] = useState(0)

  const handleSubmit = () => {
    if (rating > 0) onSubmit(movie.movie_id, rating)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Rate "{movie.title}"</h2>
        <div className="stars">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              className={(hovered || rating) >= n ? 'active' : ''}
              onClick={() => setRating(n)}
              onMouseEnter={() => setHovered(n)}
              onMouseLeave={() => setHovered(0)}
            >
              ★
            </button>
          ))}
        </div>
        <div className="actions">
          <button className="btn btn-outline" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={rating === 0}>
            Submit
          </button>
        </div>
      </div>
    </div>
  )
}
