export const RANKS = {
  BRONZE:   { name: 'Bronze',   min: 0,    max: 999,  color: '#CD7F32', icon: 'shield'  },
  SILVER:   { name: 'Silver',   min: 1000, max: 1399, color: '#C0C0C0', icon: 'shield'  },
  GOLD:     { name: 'Gold',     min: 1400, max: 1799, color: '#FFD700', icon: 'crown'   },
  PLATINUM: { name: 'Platinum', min: 1800, max: 2199, color: '#E5E4E2', icon: 'gem'     },
  DIAMOND:  { name: 'Diamond',  min: 2200, max: Infinity, color: '#B9F2FF', icon: 'diamond' },
}

export function getRank(elo) {
  if (elo < 1000) return RANKS.BRONZE
  if (elo < 1400) return RANKS.SILVER
  if (elo < 1800) return RANKS.GOLD
  if (elo < 2200) return RANKS.PLATINUM
  return RANKS.DIAMOND
}