import { Routes, Route, Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Home from './pages/Home'
import MovieDetail from './pages/MovieDetail'
import Recommendations from './pages/Recommendations'
import Profile from './pages/Profile'
import Watchlists from './pages/Watchlists'
import GroupMode from './pages/GroupMode'
import ChatModal from './components/ChatModal'
import { getUser } from './services/api'

function getUserId() {
  let id = localStorage.getItem('cinematch_user_id')
  if (!id) {
    id = String(Date.now())
    localStorage.setItem('cinematch_user_id', id)
  }
  return id
}

export default function App() {
  const userId = getUserId()
  const [userName, setUserName] = useState('')

  useEffect(() => {
    getUser(userId).then((u) => {
      setUserName(u.display_name || u.username || `User ${userId.slice(-6)}`)
    }).catch(() => {
      setUserName(`User ${userId.slice(-6)}`)
    })
  }, [])

  return (
    <div className="app">
      <header className="navbar">
        <Link to="/" className="logo">CineMatch</Link>
        <nav>
          <Link to="/">Browse</Link>
          <Link to="/recommendations">For You</Link>
          <Link to="/watchlists">Watchlists</Link>
          <Link to="/group">Group</Link>
        </nav>
        <div className="navbar-right">
          <Link to="/profile" className="user-badge">{userName}</Link>
        </div>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/movie/:id" element={<MovieDetail />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/watchlists" element={<Watchlists />} />
          <Route path="/group" element={<GroupMode />} />
        </Routes>
      </main>
      <ChatModal />
    </div>
  )
}
