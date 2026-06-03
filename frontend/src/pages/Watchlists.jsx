import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getWatchlists,
  createWatchlist,
  deleteWatchlist,
  getWatchlistItems,
  removeWatchlistItem,
} from '../services/api'

function getUserId() {
  let id = localStorage.getItem('cinematch_user_id')
  if (!id) { id = String(Date.now()); localStorage.setItem('cinematch_user_id', id) }
  return id
}

export default function Watchlists() {
  const navigate = useNavigate()
  const userId = getUserId()
  const [watchlists, setWatchlists] = useState([])
  const [selected, setSelected] = useState(null)
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [newName, setNewName] = useState('')
  const [creating, setCreating] = useState(false)

  const load = () => {
    setLoading(true)
    getWatchlists(userId).then((wls) => {
      setWatchlists(wls)
      if (selected) {
        const stillExists = wls.find((w) => w.id === selected)
        if (!stillExists) { setSelected(null); setItems([]) }
      }
      setLoading(false)
    })
  }

  useEffect(() => { load() }, [])

  useEffect(() => {
    if (selected) {
      getWatchlistItems(selected).then(setItems).catch(() => setItems([]))
    }
  }, [selected])

  const handleCreate = async () => {
    if (!newName.trim()) return
    setCreating(true)
    await createWatchlist(userId, newName.trim())
    setNewName('')
    setCreating(false)
    load()
  }

  const handleDelete = async (id) => {
    await deleteWatchlist(id)
    load()
  }

  const handleRemoveItem = async (movieId) => {
    await removeWatchlistItem(selected, movieId)
    setItems((prev) => prev.filter((i) => i.movie_id !== movieId))
  }

  if (loading && watchlists.length === 0) return <div className="spinner" />

  return (
    <div className="watchlists-page">
      <h1 className="page-title">My Watchlists</h1>

      <div className="watchlist-create">
        <input
          className="search-input"
          placeholder="New watchlist name..."
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
        />
        <button className="btn btn-primary" onClick={handleCreate} disabled={creating || !newName.trim()}>
          Create
        </button>
      </div>

      {watchlists.length === 0 ? (
        <p style={{ color: '#888', marginTop: '2rem' }}>No watchlists yet. Create one above!</p>
      ) : (
        <div className="watchlists-layout">
          <div className="watchlists-sidebar">
            {watchlists.map((wl) => (
              <div
                key={wl.id}
                className={`watchlist-sidebar-item ${selected === wl.id ? 'active' : ''}`}
                onClick={() => setSelected(wl.id)}
              >
                <div className="watchlist-sidebar-info">
                  <div className="watchlist-sidebar-name">{wl.name}</div>
                  <div className="watchlist-sidebar-count">{wl.item_count} movies</div>
                </div>
                <button
                  className="btn-icon btn-icon-danger"
                  title="Delete"
                  onClick={(e) => { e.stopPropagation(); handleDelete(wl.id); }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>

          <div className="watchlist-items">
            {!selected ? (
              <p style={{ color: '#888' }}>Select a watchlist to view its items</p>
            ) : items.length === 0 ? (
              <p style={{ color: '#888' }}>This watchlist is empty</p>
            ) : (
              <div className="movie-grid">
                {items.map((item) => (
                  <div key={item.movie_id} className="movie-card" onClick={() => navigate(`/movie/${item.movie_id}`)}>
                    <div className="poster">
                      {item.poster_url ? (
                        <img src={item.poster_url} alt={item.title} loading="lazy" />
                      ) : (
                        <span>{item.title?.charAt(0) || '?'}</span>
                      )}
                    </div>
                    <div className="info">
                      <h3>{item.title}</h3>
                      <div className="genres">{item.genres?.replace(/\|/g, ' · ')}</div>
                    </div>
                    <div className="watchlist-item-remove" onClick={(e) => { e.stopPropagation(); handleRemoveItem(item.movie_id); }}>
                      <button className="btn-icon btn-icon-danger" title="Remove">✕</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
