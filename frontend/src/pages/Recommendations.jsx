import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getRecommendations } from '../services/api'

function getUserId() {
  let id = localStorage.getItem('cinematch_user_id')
  if (!id) {
    id = String(Date.now())
    localStorage.setItem('cinematch_user_id', id)
  }
  return id
}

export default function Recommendations() {
  const navigate = useNavigate()
  const [userId] = useState(getUserId)
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getRecommendations(userId, 10)
      .then((data) => setRecs(data.recommendations || []))
      .finally(() => setLoading(false))
  }, [userId])

  return (
    <div>
      <h1 style={{ marginBottom: '1rem' }}>Recommended For You</h1>
      {loading ? (
        <div className="spinner" />
      ) : (
        <div className="recommendations-list">
          {recs.length === 0 && <p style={{ color: '#888' }}>No recommendations yet. Rate some movies first!</p>}
          {recs.map((r, i) => (
            <div key={r.movie.movie_id} className="recommendation-item" onClick={() => navigate(`/movie/${r.movie.movie_id}`)}>
              <div className="rank">#{i + 1}</div>
              <div className="poster-thumb">
                {r.movie.poster_url ? (
                  <img src={r.movie.poster_url} alt={r.movie.title} loading="lazy" />
                ) : (
                  <span>{r.movie.title?.charAt(0)}</span>
                )}
              </div>
              <div className="title">{r.movie.title}</div>
              <div className="score">{r.score.toFixed(2)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
