import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUser, updateUser, getUserRatings } from '../services/api'

function getUserId() {
  let id = localStorage.getItem('cinematch_user_id')
  if (!id) {
    id = String(Date.now())
    localStorage.setItem('cinematch_user_id', id)
  }
  return id
}

function stars(rating) {
  const full = Math.round(rating)
  return '★'.repeat(full) + '☆'.repeat(5 - full)
}

export default function Profile() {
  const navigate = useNavigate()
  const [userId] = useState(getUserId)
  const [profile, setProfile] = useState(null)
  const [ratings, setRatings] = useState([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [displayName, setDisplayName] = useState('')
  const [username, setUsername] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      getUser(userId),
      getUserRatings(userId).catch(() => []),
    ]).then(([prof, r]) => {
      setProfile(prof)
      setRatings(r || [])
      setDisplayName(prof.display_name)
      setUsername(prof.username)
      setLoading(false)
    })
  }, [userId])

  async function handleSave() {
    setSaving(true)
    setError('')
    try {
      const payload = {}
      if (displayName !== profile.display_name) payload.display_name = displayName
      if (username !== profile.username) payload.username = username
      if (Object.keys(payload).length === 0) { setEditing(false); setSaving(false); return }
      const updated = await updateUser(userId, payload)
      setProfile(updated)
      setDisplayName(updated.display_name)
      setUsername(updated.username)
      setEditing(false)
    } catch (e) {
      setError(e.message || 'Username already taken')
    }
    setSaving(false)
  }

  if (loading) return <div className="spinner" />

  return (
    <div className="profile">
      {!profile ? (
        <div className="spinner" />
      ) : (
        <>
          <div className="profile-header">
        {editing ? (
          <div className="profile-edit-form">
            <div className="profile-edit-row">
              <label>Username</label>
              <div className="profile-input-wrap">
                <span className="profile-input-prefix">@</span>
                <input
                  className="search-input"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="username"
                  autoFocus
                />
              </div>
            </div>
            <div className="profile-edit-row">
              <label>Display Name</label>
              <input
                className="search-input"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Display name"
              />
            </div>
            {error && <p className="profile-error">{error}</p>}
            <div className="profile-edit-actions">
              <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button className="btn btn-outline" onClick={() => { setEditing(false); setDisplayName(profile.display_name); setUsername(profile.username); setError('') }}>
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="profile-info">
            <h1>{profile.display_name || `User ${profile.id}`}</h1>
            <div className="profile-meta">
              <span className="profile-username">@{profile.username || `user_${profile.id}`}</span>
              <span>·</span>
              <span>ID: {profile.id}</span>
              <span>·</span>
              <span>Member since {profile.created_at?.slice(0, 10)}</span>
              <span>·</span>
              <span>{profile.rating_count} rating{profile.rating_count !== 1 ? 's' : ''}</span>
            </div>
            <button className="btn btn-outline" onClick={() => setEditing(true)} style={{ marginTop: '.75rem' }}>
              Edit Profile
            </button>
          </div>
        )}
      </div>

      <h2 style={{ margin: '2rem 0 1rem' }}>My Ratings</h2>
      {ratings.length === 0 ? (
        <p style={{ color: '#888' }}>No ratings yet. Browse movies and rate some!</p>
      ) : (
        <div className="profile-ratings">
          {ratings.map((r) => (
            <div key={`${r.movie_id}-${r.created_at}`} className="profile-rating-item" onClick={() => navigate(`/movie/${r.movie_id}`)}>
              <div className="profile-rating-poster">
                {r.poster_url ? (
                  <img src={r.poster_url} alt={r.title} loading="lazy" />
                ) : (
                  <span>{r.title?.charAt(0)}</span>
                )}
              </div>
              <div className="profile-rating-info">
                <div className="profile-rating-title">{r.title}</div>
                <div className="profile-rating-stars">{stars(r.rating)}</div>
                <div className="profile-rating-date">{r.created_at?.slice(0, 10)}</div>
              </div>
            </div>
          ))}
        </div>
      )}
      </>
      )}
    </div>
  )
}
