import { useEffect, useRef, useState } from 'react'

const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

export default function RoomDialog({ room, count, onClose, onPrev, onNext, onReroll }) {
  const dialogRef = useRef(null)
  const [rerolling, setRerolling] = useState(false)
  const [rerollError, setRerollError] = useState(null)

  async function handleReroll() {
    setRerolling(true)
    setRerollError(null)
    try {
      await onReroll()
    } catch (err) {
      setRerollError(err.message)
    } finally {
      setRerolling(false)
    }
  }

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog.open) dialog.showModal()
  }, [])

  // Clicks on the dimmed backdrop land on the <dialog> itself.
  function handleClick(event) {
    if (event.target === dialogRef.current) onClose()
  }

  function handleKeyDown(event) {
    if (event.key === 'ArrowLeft' && onPrev) onPrev()
    if (event.key === 'ArrowRight' && onNext) onNext()
  }

  const over = room.spent > room.budget

  return (
    <dialog
      ref={dialogRef}
      className="room-dialog"
      onClose={onClose}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      aria-labelledby="room-dialog-title"
    >
      <div className="dialog-card" key={room.order}>
        <button type="button" className="dialog-close" onClick={onClose} aria-label="Close">
          ×
        </button>

        <div className="dialog-head">
          <img src={room.theme.image} alt="" className={room.theme.animated ? '' : 'bob'} />
          <div>
            <p className="dialog-kicker">
              Room {room.order} of {count}
            </p>
            <h2 id="room-dialog-title">{room.name}</h2>
          </div>
        </div>

        <p className="dialog-concept">{room.concept}</p>
        {room.scare && (
          <p className="dialog-scare">
            <strong>The scare:</strong> {room.scare}
          </p>
        )}

        <h3>Props to buy</h3>
        {room.items.length ? (
          <ul className="dialog-items">
            {room.items.map((item, i) => (
              <li key={item.id ?? `${item.name}-${i}`}>
                <span className="item-name">
                  {item.name}
                  {item.quantity > 1 && <span className="item-qty"> ×{item.quantity}</span>}
                </span>
                <span className="item-price">{currency.format(item.line_total)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="dialog-empty">No props fit this room&rsquo;s budget yet.</p>
        )}

        <p className={`dialog-total ${over ? 'over' : ''}`}>
          Spent <strong>{currency.format(room.spent)}</strong> of {currency.format(room.budget)}
        </p>
        {room.sample && <p className="dialog-sample">Sample props. Real catalog items are coming soon.</p>}

        <button type="button" className="dialog-reroll" onClick={handleReroll} disabled={rerolling}>
          <img src="/images/pumpkin.svg" alt="" className={rerolling ? 'spin' : ''} />
          {rerolling ? 'Rerolling…' : 'Reroll this room'}
        </button>
        {rerollError && (
          <p className="dialog-error" role="alert">
            {rerollError}
          </p>
        )}

        <div className="dialog-nav">
          <button type="button" onClick={onPrev} disabled={!onPrev}>
            ← Previous room
          </button>
          <button type="button" onClick={onNext} disabled={!onNext}>
            Next room →
          </button>
        </div>
      </div>
    </dialog>
  )
}
