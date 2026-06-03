import { Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import MovieDetail from './pages/MovieDetail'
import Recommendations from './pages/Recommendations'
import Profile from './pages/Profile'

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

  return (
    <div className="app">
      <header className="navbar">
        <Link to="/" className="logo">CineMatch</Link>
        <nav>
          <Link to="/">Browse</Link>
          <Link to="/recommendations">For You</Link>
        </nav>
        <div className="navbar-right">
          <Link to="/profile" className="user-badge">User {userId.slice(-6)}</Link>
        </div>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/movie/:id" element={<MovieDetail />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
    </div>
  )
}
