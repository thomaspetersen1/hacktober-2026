// Thin wrapper around fetch for the FastAPI backend.
// In dev, Vite proxies /api to http://localhost:8000 (see vite.config.js).
const API_BASE = import.meta.env.VITE_API_BASE ?? ''

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${detail}`)
  }
  return res.json()
}

export function getHealth() {
  return request('/api/health')
}

export function createPlan({ budget, rooms, squareFeet = null }) {
  return request('/api/plan', {
    method: 'POST',
    body: JSON.stringify({ budget, rooms, square_feet: squareFeet }),
  })
}
