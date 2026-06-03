import { useState } from 'react'

export default function AddToWatchlist({ watchlists, onSelect }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="watchlist-dropdown-wrap">
      <button className="btn btn-outline" onClick={() => setOpen(!open)}>
        + Watchlist
      </button>
      {open && (
        <div className="watchlist-dropdown">
          {watchlists.length === 0 ? (
            <div className="watchlist-dropdown-empty">No watchlists yet</div>
          ) : (
            watchlists.map((wl) => (
              <button
                key={wl.id}
                className="watchlist-dropdown-item"
                onClick={() => { onSelect(wl.id); setOpen(false); }}
              >
                {wl.name}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  )
}
