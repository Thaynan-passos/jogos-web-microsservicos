export type AuthMode = 'login' | 'register' | 'recovery'
export type ViewMode = 'games' | 'leaderboard'

export type GameId = 'tic-tac-toe' | 'memory' | 'rps'
export type Player = 'X' | 'O'

export interface RankingEntry {
  id: string
  position: number
  userId: string
  username: string
  gameSlug: string
  gameName: string
  score: number
  durationMs: number
  durationFormatted: string
  achievedAt: string
  matchesPlayed: number
  winRate: string
}

