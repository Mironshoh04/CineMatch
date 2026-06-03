import { Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import MovieDetail from './pages/MovieDetail'
import Recommendations from './pages/Recommendations'

export default function App() {
  return (
    <div className="app">
      <header className="navbar">
        <Link to="/" className="logo">CineMatch</Link>
        <nav>
          <Link to="/">Browse</Link>
          <Link to="/recommendations">For You</Link>
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/movie/:id" element={<MovieDetail />} />
          <Route path="/recommendations" element={<Recommendations />} />
        </Routes>
      </main>
    </div>
  )
}
