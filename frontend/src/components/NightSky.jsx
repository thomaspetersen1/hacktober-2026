// Decorative backdrop: moon, stars, bats, fog, haunted manor and pumpkins.
// Purely visual, so everything here is aria-hidden.
import './NightSky.css'

const img = (name) => `/images/${name}.svg`

const BATS = [
  { top: '8%', size: 46, duration: 18, delay: 0 },
  { top: '16%', size: 30, duration: 24, delay: 4 },
  { top: '4%', size: 22, duration: 30, delay: 9 },
  { top: '26%', size: 38, duration: 21, delay: 13 },
  { top: '12%', size: 26, duration: 27, delay: 17 },
  { top: '34%', size: 20, duration: 33, delay: 6 },
  { top: '20%', size: 52, duration: 16, delay: 22 },
]

// Bats circling the moon, separate from the ones crossing the sky.
const MOON_BATS = [
  { size: 28, duration: 9, delay: 0 },
  { size: 20, duration: 12, delay: -4 },
  { size: 16, duration: 7, delay: -2 },
]

const PUMPKINS = [
  { left: '2%', size: 92, delay: 0 },
  { left: '9%', size: 58, delay: 0.7 },
  { left: '15%', size: 40, delay: 1.3 },
  { left: '71%', size: 44, delay: 0.4 },
  { left: '79%', size: 104, delay: 1.1 },
  { left: '89%', size: 64, delay: 0.2 },
  { left: '95%', size: 42, delay: 1.6 },
]

// Glowing windows: [x, y, width, height, cornerRadius, flickerDelay]
const WINDOWS = [
  [178, 132, 24, 36, 12, 0],
  [178, 204, 24, 36, 12, 1.7],
  [236, 174, 26, 34, 0, 0.4],
  [290, 174, 26, 34, 0, 2.3],
  [404, 174, 26, 34, 0, 1.1],
  [458, 174, 26, 34, 0, 3.0],
  [236, 240, 26, 34, 0, 2.6],
  [458, 240, 26, 34, 0, 0.8],
  [518, 222, 24, 34, 0, 1.9],
  [562, 222, 24, 34, 0, 0.2],
]

// Fence pickets, leaving a gap for the front gate.
const PICKETS = Array.from({ length: 29 }, (_, i) => 66 + i * 22).filter(
  (x) => x < 318 || x > 404,
)

function Manor() {
  return (
    <div className="manor">
      <svg className="hill" viewBox="0 0 100 110" preserveAspectRatio="none">
        <path d="M0 110 V58 Q22 34 50 52 T100 46 V110 Z" />
      </svg>

      <svg className="house" viewBox="0 0 700 340">
        {/* dead tree */}
        <path
          className="branch"
          d="M50 320 C46 270 56 240 42 190 M47 262 C28 246 20 228 6 222 M50 240 C68 222 80 220 98 204 M44 214 C36 192 40 176 30 156 M74 222 C82 204 94 196 98 180 M30 232 C22 218 12 214 4 200"
        />

        {/* main structure, outlined with a faint moonlit rim */}
        <g className="walls">
          <rect x="440" y="78" width="22" height="64" />
          <rect x="490" y="190" width="110" height="130" />
          <polygon points="480,196 545,140 610,196" />
          <rect x="210" y="150" width="300" height="170" />
          <polygon points="190,156 360,62 530,156" />
          <polygon points="326,132 360,100 394,132" />
          <rect x="150" y="100" width="80" height="220" />
          <polygon points="140,106 190,18 240,106" />
          <polygon points="300,258 360,228 420,258" />
          <rect x="308" y="258" width="8" height="62" />
          <rect x="404" y="258" width="8" height="62" />
          <rect x="326" y="312" width="68" height="8" />
        </g>
        <path className="trim" d="M190 18 V2 M184 8 H196 M210 196 H510 M490 236 H600" />

        {/* windows */}
        <g className="windows">
          {WINDOWS.map(([x, y, w, h, r, delay]) => (
            <g key={`${x}-${y}`}>
              <rect x={x} y={y} width={w} height={h} rx={r} style={{ animationDelay: `${delay}s` }} />
              <path className="mullion" d={`M${x + w / 2} ${y} V${y + h} M${x} ${y + h / 2} H${x + w}`} />
            </g>
          ))}
          <circle cx="360" cy="118" r="10" style={{ animationDelay: '1.4s' }} />
          <path className="door" d="M342 312 V282 a18 18 0 0 1 36 0 V312 Z" />
        </g>

        {/* fence + gravestones */}
        <path
          className="fence"
          d={`M60 310 H318 M404 310 H690 M60 296 H318 M404 296 H690 ${PICKETS.map(
            (x) => `M${x} 324 V286 l4 -8 4 8 V324`,
          ).join(' ')}`}
        />
        <path d="M612 324 v-26 a14 14 0 0 1 28 0 v26 Z" />
        <path d="M650 324 v-18 a10 10 0 0 1 20 0 v18 Z" />
        <path d="M676 324 v-30 h8 v-10 h6 v10 h8 v6 h-8 v24 Z" />
      </svg>
    </div>
  )
}

export default function NightSky() {
  return (
    <div className="night-sky" aria-hidden="true">
      <div className="stars stars-a" />
      <div className="stars stars-b" />

      <div className="moon">
        {MOON_BATS.map((bat, i) => (
          <span
            key={i}
            className="moon-bat"
            style={{
              '--size': `${bat.size}px`,
              '--orbit': `${120 + i * 26}px`,
              animationDuration: `${bat.duration}s`,
              animationDelay: `${bat.delay}s`,
            }}
          >
            <img src={img('bat')} alt="" />
          </span>
        ))}
      </div>

      <img className="web web-left" src={img('web')} alt="" />
      <img className="web web-right" src={img('web')} alt="" />

      <div className="spider">
        <span className="thread" />
        <img src={img('spider')} alt="" />
      </div>

      {BATS.map((bat, i) => (
        <div
          key={i}
          className="bat"
          style={{
            top: bat.top,
            animationDuration: `${bat.duration}s`,
            animationDelay: `-${bat.delay}s`,
          }}
        >
          <img
            src={img('bat')}
            alt=""
            style={{ width: bat.size, animationDuration: `${0.18 + bat.size / 400}s` }}
          />
        </div>
      ))}

      <img className="ghost" src={img('ghost')} alt="" />

      <Manor />
      <div className="fog fog-a" />
      <div className="fog fog-b" />

      <div className="pumpkin-patch">
        {PUMPKINS.map((p, i) => (
          <img
            key={i}
            className="patch-pumpkin"
            src={img('pumpkin')}
            alt=""
            style={{ left: p.left, width: p.size, animationDelay: `${p.delay}s` }}
          />
        ))}
        <img className="patch-cat" src={img('cat')} alt="" />
      </div>

      <div className="grain" />
    </div>
  )
}
