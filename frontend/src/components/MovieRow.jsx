import MovieCard from './MovieCard'

export default function MovieRow({ title, movies }) {
  if (!movies?.length) return null
  return (
    <div className="movie-row">
      <h2>{title}</h2>
      <div className="scroll">
        {movies.map((m) => (
          <MovieCard key={m.movie_id} movie={m} />
        ))}
      </div>
    </div>
  )
}
