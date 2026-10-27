import { useState } from 'react'

const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

const itemKey = (room, item, i) => `${room.order}-${item.id ?? item.name}-${i}`

// Every prop in the house, grouped by room, with boxes to tick off as you buy.
export default function ShoppingList({ rooms, totalCost, budget, className = '' }) {
  const [bought, setBought] = useState(() => new Set())

  const allKeys = rooms.flatMap((room) => room.items.map((item, i) => itemKey(room, item, i)))
  const boughtCount = allKeys.filter((key) => bought.has(key)).length

  function toggle(key) {
    setBought((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  return (
    <section className={`shopping ${className}`} aria-label="Shopping list">
      {rooms.map((room) => (
        <div key={room.order} className="shop-room">
          <h3>
            <span className="shop-order">{room.order}</span>
            {room.name}
            <span className="shop-room-total">
              {currency.format(room.spent)} <small>of {currency.format(room.budget)}</small>
            </span>
          </h3>
          <ul>
            {room.items.map((item, i) => {
              const key = itemKey(room, item, i)
              return (
                <li key={key} className={bought.has(key) ? 'bought' : ''}>
                  <label>
                    <input type="checkbox" checked={bought.has(key)} onChange={() => toggle(key)} />
                    <span className="shop-name">
                      {item.name}
                      {item.quantity > 1 && <span className="shop-qty"> ×{item.quantity}</span>}
                    </span>
                    <span className="shop-price">{currency.format(item.line_total)}</span>
                  </label>
                </li>
              )
            })}
            {!room.items.length && <li className="shop-empty">No props fit this room&rsquo;s budget.</li>}
          </ul>
        </div>
      ))}

      <footer className="shop-footer">
        <span>
          {boughtCount} of {allKeys.length} bought
        </span>
        <strong>
          {currency.format(totalCost)} <small>of {currency.format(budget)}</small>
        </strong>
      </footer>
      {rooms.some((room) => room.sample) && (
        <p className="shop-sample">Sample props. Real catalog items are coming soon.</p>
      )}
    </section>
  )
}
