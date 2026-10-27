import './LoadingScreen.css'

const COPY = {
  timeout: {
    title: 'The spirits are restless',
    body: 'Planning took longer than 90 seconds. The AI might be busy, so give it another try.',
  },
  network: {
    title: 'The house is unreachable',
    body: 'We couldn’t reach the backend. Make sure it’s running, then try again.',
  },
  server: {
    title: 'Something went bump',
    body: 'The planner hit an error or isn’t running. Trying again usually fixes it.',
  },
  input: {
    title: 'That budget won’t haunt',
    body: null, // the backend's message is more useful here
  },
}

export default function ErrorScreen({ error, onRetry, onBack }) {
  const copy = COPY[error.kind] ?? COPY.server

  return (
    <div className="loading" role="alertdialog" aria-labelledby="error-title" aria-describedby="error-body">
      <div className="loading-card">
        <div className="cauldron">
          <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f480/512.webp" alt="" className="on" />
        </div>
        <h2 id="error-title">{copy.title}</h2>
        <p id="error-body" className="error-body">
          {copy.body ?? error.message}
        </p>
        {error.kind === 'server' && error.message && <p className="error-detail">{error.message}</p>}
        <div className="error-actions">
          {error.kind !== 'input' && (
            <button type="button" className="error-retry" onClick={onRetry}>
              Try again
            </button>
          )}
          <button type="button" className="error-back" onClick={onBack}>
            Back to the form
          </button>
        </div>
      </div>
    </div>
  )
}
