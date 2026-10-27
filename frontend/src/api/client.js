// Thin wrapper around fetch for the FastAPI backend.
// In dev, Vite proxies /api to http://localhost:8000 (see vite.config.js).
const API_BASE = import.meta.env.VITE_API_BASE ?? ''

// Cortex calls can be slow, but give up eventually instead of spinning forever.
const TIMEOUT_MS = 90_000

export class ApiError extends Error {
  constructor(message, { kind, status } = {}) {
    super(message)
    this.kind = kind // 'timeout' | 'network' | 'server' | 'input'
    this.status = status
  }
}

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(TIMEOUT_MS),
      ...options,
    })
  } catch (err) {
    if (err.name === 'TimeoutError') {
      throw new ApiError('The spirits took too long to answer.', { kind: 'timeout' })
    }
    throw new ApiError('Could not reach the backend. Is it running?', { kind: 'network' })
  }

  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      // FastAPI sends a string, or a list of validation errors for 422s
      detail = Array.isArray(body.detail) ? body.detail.map((d) => d.msg).join(', ') : body.detail
    } catch {
      // body wasn't JSON; keep the status text
    }
    throw new ApiError(detail, { kind: res.status < 500 ? 'input' : 'server', status: res.status })
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

// Swap one room for a new one that fits the same theme and budget.
export function rerollRoom({ theme, room, avoid }) {
  return request('/api/rooms/reroll', {
    method: 'POST',
    body: JSON.stringify({ theme, order: room.order, budget: room.budget, avoid }),
  })
}
