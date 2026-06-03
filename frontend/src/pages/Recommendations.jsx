import { useState, useEffect } from 'react'
import { getRecommendations } from '../services/api'

export default function Recommendations() {
  const [userId, setUserId] = useState(1)
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    getRecommendations(userId, 10)
      .then((data) => setRecs(data.recommendations || []))
      .finally(() => setLoading(false))
  }, [userId])

  return (
    <div>
      <h1 style={{ marginBottom: '1rem' }}>Recommended For You</h1>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '.5rem' }}>
        <label htmlFor="uid">User ID:</label>
        <input
          id="uid"
          type="number"
          min={1}
          value={userId}
          onChange={(e) => setUserId(Number(e.target.value))}
          style={{
            background: '#1f1f1f', border: '1px solid #333', color: '#e5e5e5',
            borderRadius: '6px', padding: '.4rem .75rem', width: '100px',
          }}
        />
      </div>
      {loading ? (
        <div className="spinner" />
      ) : (
        <div className="recommendations-list">
          {recs.length === 0 && <p style={{ color: '#888' }}>No recommendations yet.</p>}
          {recs.map((r, i) => (
            <div key={r.movie.movie_id} className="recommendation-item">
              <div className="rank">#{i + 1}</div>
              <div className="title">{r.movie.title}</div>
              <div className="score">{r.score.toFixed(2)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
