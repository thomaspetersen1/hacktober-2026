import { useState } from 'react'
import { rerollRoom } from '../api/client.js'
import { roomTheme, sampleItems } from '../data/roomThemes.js'
import RoomDialog from './RoomDialog.jsx'
import ShoppingList from './ShoppingList.jsx'
import './ResultsPage.css'

const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

const RADIUS = 40 // ring radius, in % of the ring's width

// Accepts either the full item shape ({unit_price, quantity, line_total})
// or a simpler {name, price} from the backend while it's being built.
function normalizeItem(item) {
  const price = item.unit_price ?? item.price ?? 0
  const quantity = item.quantity ?? 1
  return { ...item, unit_price: price, quantity, line_total: item.line_total ?? price * quantity }
}

function withItems(room) {
  // Rooms from an older backend have no items list; [] means nothing fit the budget
  const sample = !Array.isArray(room.items)
  const items = (sample ? sampleItems(room) : room.items).map(normalizeItem)
  const spentCents = items.reduce((sum, item) => sum + Math.round(item.line_total * 100), 0)
  return { ...room, items, sample, spent: spentCents / 100, theme: roomTheme(room) }
}

// Point on the ring for room i of n, starting at 12 o'clock and going clockwise.
function ringPoint(i, n, radius = RADIUS) {
  const angle = ((-90 + (i * 360) / n) * Math.PI) / 180
  return { x: 50 + radius * Math.cos(angle), y: 50 + radius * Math.sin(angle) }
}

function pathArc(n) {
  if (n < 2) return null
  const start = ringPoint(0, n)
  const end = ringPoint(n - 1, n)
  const largeArc = (n - 1) / n > 0.5 ? 1 : 0
  return `M ${start.x} ${start.y} A ${RADIUS} ${RADIUS} 0 ${largeArc} 1 ${end.x} ${end.y}`
}

export default function ResultsPage({ plan, onReset, onPlanChange }) {
  const [openIndex, setOpenIndex] = useState(null)
  const [view, setView] = useState('house')
  const rooms = plan.rooms.map(withItems)
  const n = rooms.length

  const totalCost = rooms.reduce((sum, room) => sum + Math.round(room.spent * 100), 0) / 100
  // Rooms shrink as there are more of them so they don't overlap on the ring.
  const nodeSize = Math.min(0.26, 1.85 / n)
  const gap = n > 1 ? ringPoint(n - 0.5, n, RADIUS + 9) : null

  async function handleReroll(index) {
    const room = plan.rooms[index]
    const fresh = await rerollRoom({ theme: plan.theme, room, avoid: plan.rooms.map((r) => r.name) })
    onPlanChange({ ...plan, rooms: plan.rooms.map((r, i) => (i === index ? fresh : r)) })
  }

  return (
    <section className="results">
      <header className="results-head">
        <button type="button" className="back" onClick={onReset}>
          ← Plan another house
        </button>
        <h1 className="total-cost">
          <span>Total Cost:</span> {currency.format(totalCost)}
        </h1>
      </header>

      <div className="view-tabs" role="tablist" aria-label="Results view">
        <button type="button" role="tab" aria-selected={view === 'house'} onClick={() => setView('house')}>
          House map
        </button>
        <button type="button" role="tab" aria-selected={view === 'list'} onClick={() => setView('list')}>
          Shopping list
        </button>
      </div>

      <div className={`cycle ${view === 'house' ? '' : 'screen-hidden'}`} style={{ '--node': nodeSize, '--sweep': `${((n - 1) * 360) / n}deg` }}>
        <svg className="cycle-path" viewBox="0 0 100 100" aria-hidden="true">
          <circle className="cycle-track" cx="50" cy="50" r={RADIUS} />
          {n > 1 && <path className="cycle-march" d={pathArc(n)} />}
        </svg>

        {n > 1 && (
          <div className="walker" aria-hidden="true">
            <img src="/images/ghost.svg" alt="" />
          </div>
        )}

        {gap && (
          <p className="gap-label" style={{ left: `${gap.x}%`, top: `${gap.y}%` }} aria-hidden="true">
            Exit <span>·</span> Enter
          </p>
        )}

        <div className="cycle-center">
          <p className="cycle-kicker">Your haunted house</p>
          <h2>{plan.theme}</h2>
          {plan.story && <p className="cycle-story">{plan.story}</p>}
          <p className="cycle-hint">Click a room to see its props</p>
        </div>

        <ol className="cycle-rooms">
          {rooms.map((room, i) => {
            const point = ringPoint(i, n)
            return (
              <li
                key={room.order}
                className="cycle-room"
                style={{ '--x': `${point.x}%`, '--y': `${point.y}%`, animationDelay: `${150 + i * 110}ms` }}
              >
                <button type="button" onClick={() => setOpenIndex(i)}>
                  <span className="room-order">{room.order}</span>
                  <img src={room.theme.image} alt="" loading="lazy" className={room.theme.animated ? '' : 'bob'} />
                  <span className="room-name">{room.name}</span>
                  <span className="room-spent">{currency.format(room.spent)}</span>
                </button>
              </li>
            )
          })}
        </ol>
      </div>

      {/* Stays mounted so ticked items survive switching tabs. */}
      <ShoppingList
        rooms={rooms}
        totalCost={totalCost}
        budget={plan.budget}
        className={view === 'list' ? '' : 'screen-hidden'}
      />

      {openIndex !== null && (
        <RoomDialog
          room={rooms[openIndex]}
          count={n}
          onClose={() => setOpenIndex(null)}
          onReroll={() => handleReroll(openIndex)}
          onPrev={openIndex > 0 ? () => setOpenIndex(openIndex - 1) : null}
          onNext={openIndex < n - 1 ? () => setOpenIndex(openIndex + 1) : null}
        />
      )}
    </section>
  )
}
