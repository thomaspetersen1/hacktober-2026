// Picks an image for each room by matching keywords in its name and concept,
// so it keeps working once the AI starts inventing room names.
//
// Animated images are Noto Animated Emoji (CC-BY 4.0) served by Google Fonts.
// The ones Noto doesn't animate fall back to Twemoji SVGs in public/images.

const noto = (code) => `https://fonts.gstatic.com/s/e/notoemoji/latest/${code}/512.webp`
const local = (name) => `/images/${name}.svg`

// Order matters: the first match wins, so specific themes come before broad ones.
const THEMES = [
  { key: 'vampire', match: /^(vampire|dracula|fang|blood|count)/, image: local('vampire'), animated: false, emoji: '🧛' },
  { key: 'doll', match: /^(chucky|doll|toy|nursery|clown|carnival|circus|jester)/, image: noto('1f921'), animated: true, emoji: '🤡' },
  { key: 'mirror', match: /^(mirror|reflection|vanish|invisible)/, image: noto('1fae5'), animated: true, emoji: '🫥' },
  { key: 'witch', match: /^(witch|cauldron|coven|kitchen|brew|potion|hex)/, image: local('witch'), animated: false, emoji: '🧙‍♀️' },
  { key: 'seance', match: /^(seance|séance|crystal|psychic|fortune|oracle)/, image: noto('1f52e'), animated: true, emoji: '🔮' },
  { key: 'zombie', match: /^(zombie|undead|corpse|morgue|infect)/, image: local('zombie'), animated: false, emoji: '🧟' },
  { key: 'coffin', match: /^(coffin|funeral|mortuary|wake)/, image: local('coffin'), animated: false, emoji: '⚰️' },
  { key: 'skull', match: /^(skull|bone|crypt|tomb|grave|catacomb|skeleton)/, image: noto('1f480'), animated: true, emoji: '💀' },
  { key: 'spider', match: /^(spider|web|attic|archive|dust)/, image: noto('1f577_fe0f'), animated: true, emoji: '🕷️' },
  { key: 'bat', match: /^(bat|cellar|cave|belfry|basement|tunnel)/, image: noto('1f987'), animated: true, emoji: '🦇' },
  { key: 'devil', match: /^(devil|demon|hell|chapel|altar|ritual|cult|possess)/, image: noto('1f608'), animated: true, emoji: '😈' },
  { key: 'brain', match: /^(asylum|brain|lab|doctor|surgeon|experiment|ward)/, image: noto('1f9e0'), animated: true, emoji: '🧠' },
  { key: 'eye', match: /^(eye|portrait|gallery|watch|stare)/, image: noto('1f441_fe0f'), animated: true, emoji: '👁️' },
  { key: 'clock', match: /^(clock|tower|time|landing)/, image: noto('23f0'), animated: true, emoji: '⏰' },
  { key: 'fire', match: /^(fire|furnace|burn|flame|inferno)/, image: noto('1f525'), animated: true, emoji: '🔥' },
  { key: 'storm', match: /^(storm|lightning|thunder)/, image: noto('26a1'), animated: true, emoji: '⚡' },
  { key: 'snake', match: /^(snake|serpent|swamp|bog)/, image: noto('1f40d'), animated: true, emoji: '🐍' },
  { key: 'garden', match: /^(garden|vine|forest|graveyard|thorn|flower)/, image: noto('1f940'), animated: true, emoji: '🥀' },
  { key: 'alien', match: /^(alien|ufo|space)/, image: noto('1f47d'), animated: true, emoji: '👽' },
  { key: 'scream', match: /^(exit|escape|final|scream|climax)/, image: noto('1f631'), animated: true, emoji: '😱' },
  { key: 'pumpkin', match: /^(entry|entrance|hall|foyer|threshold|porch|pumpkin)/, image: noto('1f383'), animated: true, emoji: '🎃' },
  { key: 'ghost', match: /^(ghost|spirit|whisper|haunt|phantom|poltergeist)/, image: noto('1f47b'), animated: true, emoji: '👻' },
]

const FALLBACK = { key: 'ghost', image: noto('1f47b'), animated: true, emoji: '👻' }

export function roomTheme(room) {
  // The backend tags each room (the LLM picks it), so prefer that over guessing
  const tagged = THEMES.find((t) => t.key === room.theme_key)
  if (tagged) return tagged
  const words = `${room.name} ${room.concept}`.toLowerCase().split(/[^a-zé]+/)
  // Match whole-word prefixes, so "bat" hits "bats" but not "battery".
  return THEMES.find((t) => words.some((w) => t.match.test(w))) ?? FALLBACK
}

// PLACEHOLDER until the backend returns real items from the catalog.
// These prices are made up; they only exist so the popup has something to show.
const SAMPLE_PROPS = {
  vampire: [['Foam coffin prop', 34.99], ['Fake blood (16 oz)', 9.99], ['Red LED uplight', 14.99], ['Candelabra', 19.99]],
  doll: [['Creepy porcelain doll', 18.99], ['Talking doll animatronic', 49.99], ['Broken toy box', 24.99], ['Music box loop (sound)', 6.99]],
  mirror: [['Cracked mirror panel', 22.99], ['Silver mylar sheeting', 11.99], ['Strobe light', 17.99], ['Hidden speaker', 15.99]],
  witch: [['Cauldron (24 in)', 27.99], ['Hanging dried herbs', 12.99], ['Green fog fluid', 13.99], ['Witch costume', 39.99]],
  seance: [['Light-up crystal ball', 24.99], ['Black velvet drape', 21.99], ['Floating candle set', 19.99], ['Spirit board', 14.99]],
  zombie: [['Crawling zombie prop', 44.99], ['Torn sheet set', 9.99], ['Green flicker bulb', 7.99], ['Groaning sound loop', 4.99]],
  coffin: [['Standing coffin', 49.99], ['Funeral lily bouquet', 12.99], ['Purple LED wash', 16.99], ['Organ music loop', 4.99]],
  skull: [['Skull pile (12 pk)', 21.99], ['Life-size skeleton', 34.99], ['Candle-flicker LEDs', 13.99], ['Stone wall backdrop', 18.99]],
  spider: [['Giant hairy spider', 29.99], ['Stretch cobweb (bulk)', 8.99], ['Drop-down spider gag', 26.99], ['Dust sheet covers', 11.99]],
  bat: [['Hanging bat garland', 12.99], ['Flapping bat animatronic', 32.99], ['Blacklight bar', 22.99], ['Dripping water loop', 4.99]],
  devil: [['Ritual candle set', 16.99], ['Glowing pentagram rug', 24.99], ['Red strobe', 17.99], ['Hooded robe', 22.99]],
  brain: [['Specimen jars (set)', 19.99], ['Bloody surgical tray', 15.99], ['Flicker fluorescent tube', 18.99], ['Gurney prop', 49.99]],
  eye: [['Changing-portrait frame', 29.99], ['Moving-eye picture', 19.99], ['Picture lights', 14.99], ['Whisper sound loop', 4.99]],
  clock: [['Grandfather clock facade', 39.99], ['Ticking sound loop', 4.99], ['Cobweb clock hands', 9.99], ['Fog machine', 39.99]],
  fire: [['Fake flame lantern', 24.99], ['Orange flicker light', 14.99], ['Smoke machine', 39.99], ['Crackling fire loop', 4.99]],
  storm: [['Lightning flash effect', 29.99], ['Thunder sound loop', 4.99], ['Rain curtain', 16.99], ['Wind fan', 19.99]],
  snake: [['Rubber snake bundle', 12.99], ['Swamp moss netting', 14.99], ['Low-lying fog chiller', 34.99], ['Frog sound loop', 4.99]],
  garden: [['Dead rose bouquet', 11.99], ['Creeping vine garland', 13.99], ['Tombstone set', 27.99], ['Ground fog machine', 39.99]],
  alien: [['Alien pod prop', 34.99], ['Green laser projector', 29.99], ['Smoke fluid', 13.99], ['Beeping sound loop', 4.99]],
  scream: [['Air-blast jump scare', 39.99], ['Scream sound trigger', 14.99], ['Strobe light', 17.99], ['Exit sign (glowing)', 9.99]],
  pumpkin: [['Light-up jack-o-lantern', 19.99], ['Hay bale', 12.99], ['Fog machine', 39.99], ['Welcome sign', 11.99]],
  ghost: [['Hanging ghost', 16.99], ['Flying sheet ghost (motor)', 36.99], ['Blue flicker bulb', 7.99], ['Whisper sound loop', 4.99]],
}

// Greedily fits sample props into the room's budget, in whole cents.
export function sampleItems(room) {
  const props = SAMPLE_PROPS[roomTheme(room).key] ?? SAMPLE_PROPS.ghost
  let leftCents = Math.round(room.budget * 100)
  const items = []
  for (const [name, price] of props) {
    const cents = Math.round(price * 100)
    const quantity = Math.min(3, Math.floor(leftCents / cents))
    if (quantity < 1) continue
    leftCents -= quantity * cents
    items.push({ name, unit_price: price, quantity, line_total: (quantity * cents) / 100 })
  }
  return items
}
