import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getGroupRecommendations } from '../services/api'

export default function GroupMode() {
  const navigate = useNavigate()
  const [userIds, setUserIds] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async () => {
    const ids = userIds.split(/[\s,]+/).map((s) => Number(s)).filter((n) => n > 0)
    if (ids.length < 2) {
      setError('Enter at least 2 user IDs')
      return
    }
    setError('')
    setLoading(true)
    try {
      const data = await getGroupRecommendations(ids, 20)
      setResults(data.recommendations || [])
    } catch (e) {
      setError(e.message)
    }
    setLoading(false)
  }

  return (
    <div className="group-mode">
      <h1 className="page-title">Group Mode</h1>
      <p style={{ color: '#888', marginBottom: '1.5rem' }}>
        Enter multiple user IDs to find movies everyone will enjoy
      </p>

      <div className="group-input-row">
        <input
          className="search-input"
          placeholder="e.g. 1712345678, 1712345679"
          value={userIds}
          onChange={(e) => setUserIds(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button className="btn btn-primary" onClick={handleSearch} disabled={loading}>
          {loading ? 'Merging...' : 'Find Group Picks'}
        </button>
      </div>
      {error && <p className="profile-error">{error}</p>}

      {results.length > 0 && (
        <div className="recommendations-list" style={{ marginTop: '2rem' }}>
          {results.map((r, i) => (
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
              <div className="score">{r.score.toFixed(4)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
