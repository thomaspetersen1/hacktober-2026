import { useEffect, useState } from 'react'
import { createPlan } from './api/client.js'
import ErrorScreen from './components/ErrorScreen.jsx'
import LoadingScreen from './components/LoadingScreen.jsx'
import NightSky from './components/NightSky.jsx'
import PlanForm from './components/PlanForm.jsx'
import ResultsPage from './components/ResultsPage.jsx'
import './App.css'

// Keep the loading screen up long enough to read, even when the backend is instant.
const MIN_LOADING_MS = 2400
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

function App() {
  const [plan, setPlan] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lastRequest, setLastRequest] = useState(null)

  // The browser's back button returns from the results to the form.
  useEffect(() => {
    const handlePop = () => setPlan(null)
    window.addEventListener('popstate', handlePop)
    return () => window.removeEventListener('popstate', handlePop)
  }, [])

  function handleReset() {
    if (window.history.state?.results) window.history.back()
    else setPlan(null)
  }

  async function handleSubmit(request) {
    setLoading(true)
    setError(null)
    setLastRequest(request)
    try {
      const [result] = await Promise.all([createPlan(request), wait(MIN_LOADING_MS)])
      setPlan(result)
      window.history.pushState({ results: true }, '')
      window.scrollTo(0, 0)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <NightSky />
      {loading && <LoadingScreen />}
      {error && (
        <ErrorScreen error={error} onRetry={() => handleSubmit(lastRequest)} onBack={() => setError(null)} />
      )}

      <main className="app">
        {plan ? (
          <ResultsPage plan={plan} onReset={handleReset} onPlanChange={setPlan} />
        ) : (
          <section className="hero">
            <div className="hero-copy">
              <p className="eyebrow">
                <img src="/images/candle.svg" alt="" /> Hacktober 2026 · Est. Oct 31
              </p>
              <h1 className="title">
                <span className="title-top">Haunted</span>
                <span className="title-bottom">
                  House <em>Planner</em>
                </span>
              </h1>
            </div>

            <PlanForm onSubmit={handleSubmit} loading={loading} />
          </section>
        )}
      </main>
    </>
  )
}

export default App
