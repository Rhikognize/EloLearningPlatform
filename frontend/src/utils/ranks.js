export const RANKS = {
  Bronze:   { name: 'Bronze',   color: '#CD7F32', icon: 'shield'  },
  Silver:   { name: 'Silver',   color: '#C0C0C0', icon: 'shield'  },
  Gold:     { name: 'Gold',     color: '#FFD700', icon: 'crown'   },
  Platinum: { name: 'Platinum', color: '#E5E4E2', icon: 'gem'     },
  Diamond:  { name: 'Diamond',  color: '#B9F2FF', icon: 'diamond' },
}

export function getRank(elo) {
  if (elo < 1000) return RANKS.Bronze
  if (elo < 1400) return RANKS.Silver
  if (elo < 1800) return RANKS.Gold
  if (elo < 2200) return RANKS.Platinum
  return RANKS.Diamond
}