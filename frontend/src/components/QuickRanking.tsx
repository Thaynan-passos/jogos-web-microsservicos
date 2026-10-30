import type { RankingEntry } from '../types.ts'

interface QuickRankingProps {
  entries: RankingEntry[]
  onOpenFullLeaderboard: () => void
}

export function QuickRanking({ entries, onOpenFullLeaderboard }: QuickRankingProps) {
  const topThree = entries.slice(0, 3)

  const medals = ['🥇', '🥈', '🥉']

  return (
    <section className="quick-ranking-card" aria-label="Ranking Rápido">
      <div className="quick-ranking-header">
        <div className="quick-ranking-title-group">
          <span className="eyebrow">DESTAQUES DA COMUNIDADE</span>
          <h3>⚡ Top Jogadores da Semana</h3>
        </div>
        <button
          className="view-full-ranking-btn"
          type="button"
          onClick={onOpenFullLeaderboard}
        >
          <span>Ranking Completo</span>
          <span aria-hidden="true">↗</span>
        </button>
      </div>

      <div className="quick-ranking-list">
        {topThree.map((item, index) => (
          <div key={item.id} className={`quick-ranking-item rank-pos-${index + 1}`}>
            <div className="quick-ranking-pos">
              <span className="medal-icon">{medals[index] || `#${index + 1}`}</span>
            </div>
            <div className="quick-ranking-info">
              <span className="quick-ranking-name">{item.username}</span>
              <span className="quick-ranking-game">
                {item.gameName} · {item.durationFormatted}
              </span>
            </div>
            <div className="quick-ranking-score">
              <span className="score-val">{item.score}</span>
              <span className="score-label">pts</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

