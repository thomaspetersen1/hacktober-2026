import { useState } from 'react'

const MIN_ROOMS = 1
const MAX_ROOMS = 12
const BUDGET_PRESETS = [250, 500, 1000, 2500]

const compactUsd = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  notation: 'compact',
})

export default function PlanForm({ onSubmit, loading }) {
  const [budget, setBudget] = useState('500')
  const [rooms, setRooms] = useState(4)
  const [squareFeet, setSquareFeet] = useState('')

  const clampRooms = (n) => Math.min(MAX_ROOMS, Math.max(MIN_ROOMS, n))

  function handleSubmit(event) {
    event.preventDefault()
    onSubmit({
      budget: Number(budget),
      rooms,
      squareFeet: squareFeet === '' ? null : Number(squareFeet),
    })
  }

  return (
    <form className="tombstone" onSubmit={handleSubmit}>
      <div className="tombstone-head">
        <span className="rip">R.I.P.</span>
        <p>Here lies your budget.</p>
      </div>

      <div className="field">
        <label htmlFor="budget">Budget</label>
        <div className="input-shell">
          <span className="affix">$</span>
          <input
            id="budget"
            type="number"
            inputMode="decimal"
            min="1"
            step="any"
            placeholder="500"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            required
          />
        </div>
        <div className="chips" role="group" aria-label="Budget presets">
          {BUDGET_PRESETS.map((amount) => (
            <button
              key={amount}
              type="button"
              className={`chip ${Number(budget) === amount ? 'chip-on' : ''}`}
              onClick={() => setBudget(String(amount))}
            >
              {compactUsd.format(amount)}
            </button>
          ))}
        </div>
      </div>

      <div className="field">
        <label htmlFor="rooms">Number of rooms</label>
        <div className="stepper">
          <button
            type="button"
            aria-label="Remove a room"
            onClick={() => setRooms((n) => clampRooms(n - 1))}
            disabled={rooms <= MIN_ROOMS}
          >
            −
          </button>
          <input
            id="rooms"
            type="number"
            min={MIN_ROOMS}
            max={MAX_ROOMS}
            value={rooms}
            onChange={(e) => setRooms(clampRooms(Number(e.target.value) || MIN_ROOMS))}
            required
          />
          <button
            type="button"
            aria-label="Add a room"
            onClick={() => setRooms((n) => clampRooms(n + 1))}
            disabled={rooms >= MAX_ROOMS}
          >
            +
          </button>
        </div>
        <div className="room-pumpkins" aria-hidden="true">
          {Array.from({ length: rooms }, (_, i) => (
            <img key={i} src="/images/pumpkin.svg" alt="" style={{ animationDelay: `${i * 40}ms` }} />
          ))}
        </div>
      </div>

      <div className="field">
        <label htmlFor="sqft">
          Square footage <span className="optional">optional</span>
        </label>
        <div className="input-shell">
          <input
            id="sqft"
            type="number"
            inputMode="numeric"
            min="1"
            step="any"
            placeholder="e.g. 1200"
            value={squareFeet}
            onChange={(e) => setSquareFeet(e.target.value)}
          />
          <span className="affix affix-end">sq ft</span>
        </div>
        <p className="hint">Leave it blank and we&rsquo;ll size the rooms for you.</p>
      </div>

      <button type="submit" className="summon" disabled={loading}>
        <img src="/images/pumpkin.svg" alt="" className={loading ? 'spin' : ''} />
        {loading ? 'Summoning spirits…' : 'Summon my haunted house'}
      </button>
    </form>
  )
}
