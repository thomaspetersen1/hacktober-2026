import { useEffect, useState } from 'react'
import { createPlan, getHealth } from './api/client.js'
import './App.css'

const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
})

function App() {
  const [budget, setBudget] = useState(500)
  const [rooms, setRooms] = useState(4)
  const [plan, setPlan] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    getHealth()
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'))
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      setPlan(await createPlan({ budget: Number(budget), rooms: Number(rooms) }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app">
      <header>
        <h1>Haunted House Planner</h1>
        <p className={`status status-${apiStatus}`}>API: {apiStatus}</p>
      </header>

      <form className="plan-form" onSubmit={handleSubmit}>
        <label>
          Budget ($)
          <input
            type="number"
            min="1"
            step="1"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            required
          />
        </label>
        <label>
          Rooms
          <input
            type="number"
            min="1"
            max="12"
            value={rooms}
            onChange={(e) => setRooms(e.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Summoning…' : 'Design my haunted house'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {plan && (
        <section className="plan">
          <h2>{plan.theme}</h2>
          <ol className="rooms">
            {plan.rooms.map((room) => (
              <li key={room.order} className="room-card">
                <h3>{room.name}</h3>
                <p>{room.concept}</p>
                <p className="room-budget">{currency.format(room.budget)}</p>
              </li>
            ))}
          </ol>
          <p className="total">
            Total allocated: {currency.format(plan.total_allocated)} of{' '}
            {currency.format(plan.budget)}
          </p>
        </section>
      )}
    </main>
  )
}

export default App
