import { useEffect, useState } from 'react'
import './LoadingScreen.css'

// Mirrors the backend pipeline. The request is a single call, so these advance
// on a timer; the last step keeps spinning until the plan actually arrives.
const STEPS = [
  { label: 'Conjuring a theme', image: 'https://fonts.gstatic.com/s/e/notoemoji/latest/1f52e/512.webp' },
  { label: 'Hunting for props within budget', image: 'https://fonts.gstatic.com/s/e/notoemoji/latest/1f577_fe0f/512.webp' },
  { label: 'Making sure the house flows', image: 'https://fonts.gstatic.com/s/e/notoemoji/latest/1f47b/512.webp' },
]
const STEP_MS = 1800

export default function LoadingScreen() {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), STEP_MS)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="loading" role="status" aria-live="polite">
      <div className="loading-card">
        <div className="cauldron">
          {STEPS.map((s, i) => (
            <img key={s.label} src={s.image} alt="" className={i === step ? 'on' : ''} />
          ))}
        </div>

        <h2>Summoning your haunted house…</h2>

        <ol className="loading-steps">
          {STEPS.map((s, i) => (
            <li key={s.label} className={i < step ? 'done' : i === step ? 'active' : ''}>
              <span className="step-mark" aria-hidden="true">
                {i < step ? '✓' : ''}
              </span>
              {s.label}
            </li>
          ))}
        </ol>

        <div className="loading-bar" aria-hidden="true">
          <span />
        </div>
      </div>
    </div>
  )
}
