import { useEffect, useRef, useState } from 'react'
import { createPlan } from './api/client.js'
import NightSky from './components/NightSky.jsx'
import PlanForm from './components/PlanForm.jsx'
import './App.css'

const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
})

function App() {
  const [plan, setPlan] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const resultsRef = useRef(null)

  useEffect(() => {
    if (plan) resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [plan])

  async function handleSubmit(request) {
    setLoading(true)
    setError(null)
    try {
      setPlan(await createPlan(request))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <NightSky />

      <main className="app">
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

        {error && (
          <p className="error" role="alert">
            <img src="/images/skull.svg" alt="" /> {error}
          </p>
        )}

        {plan && (
          <section className="plan" ref={resultsRef}>
            <h2>{plan.theme}</h2>
            <ol className="rooms">
              {plan.rooms.map((room) => (
                <li key={room.order} className="room-card" style={{ animationDelay: `${room.order * 90}ms` }}>
                  <span className="room-number">{room.order}</span>
                  <h3>{room.name}</h3>
                  <p>{room.concept}</p>
                  <p className="room-budget">{currency.format(room.budget)}</p>
                </li>
              ))}
            </ol>
            <p className="total">
              Total allocated: {currency.format(plan.total_allocated)} of{' '}
              {currency.format(plan.budget)}
              {plan.square_feet && <> · {plan.square_feet.toLocaleString()} sq ft</>}
            </p>
          </section>
        )}
      </main>
    </>
  )
}

export default App
