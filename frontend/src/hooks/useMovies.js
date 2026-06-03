import { useEffect, useState } from 'react'

export function useMovies(page = 1) {
  const [data, setData] = useState({ movies: [], total: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    import('../services/api').then(({ getMovies }) =>
      getMovies(page)
        .then(setData)
        .catch(setError)
        .finally(() => setLoading(false))
    )
  }, [page])

  return { ...data, loading, error }
}
