import { useState, useMemo } from 'react'
import type { RankingEntry } from '../types.ts'

interface LeaderboardViewProps {
  entries: RankingEntry[]
  onBackToGames: () => void
}

export function LeaderboardView({ entries, onBackToGames }: LeaderboardViewProps) {
  const [selectedGame, setSelectedGame] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'score' | 'recent'>('score')

  const gameOptions = [
    { slug: 'all', label: 'Todos os Jogos', icon: '🎮' },
    { slug: 'tic-tac-toe', label: 'Jogo da Velha', icon: '⭕' },
    { slug: 'memory', label: 'Jogo da Memória', icon: '🧠' },
    { slug: 'rps', label: 'Pedra, Papel e Tesoura', icon: '✊' },
  ]

  const filteredEntries = useMemo(() => {
    return entries
      .filter((entry) => {
        const matchesGame =
          selectedGame === 'all' ||
          entry.gameSlug === selectedGame ||
          (selectedGame === 'tic-tac-toe' && entry.gameSlug === 'jogo-da-velha') ||
          (selectedGame === 'memory' && entry.gameSlug === 'jogo-da-memoria') ||
          (selectedGame === 'rps' && entry.gameSlug === 'pedra-papel-tesoura')

        const matchesSearch =
          entry.username.toLowerCase().includes(searchTerm.toLowerCase().trim()) ||
          entry.gameName.toLowerCase().includes(searchTerm.toLowerCase().trim())

        return matchesGame && matchesSearch
      })
      .sort((a, b) => {
        if (sortBy === 'score') {
          return b.score - a.score || a.durationMs - b.durationMs
        }
        return new Date(b.achievedAt).getTime() - new Date(a.achievedAt).getTime()
      })
  }, [entries, selectedGame, searchTerm, sortBy])

  const stats = useMemo(() => {
    const highestScore = entries.length > 0 ? Math.max(...entries.map((e) => e.score)) : 0
    const topPlayer = entries.find((e) => e.score === highestScore)?.username ?? 'Nenhum'
    return {
      total: entries.length,
      highestScore,
      topPlayer,
    }
  }, [entries])

  function getMedal(index: number) {
    if (index === 0) return '🥇'
    if (index === 1) return '🥈'
    if (index === 2) return '🥉'
    return `#${index + 1}`
  }

  function getInitials(name: string) {
    return name.slice(0, 2).toUpperCase()
  }

  function formatDate(iso: string) {
    try {
      const date = new Date(iso)
      return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return iso
    }
  }

  return (
    <div className="leaderboard-page">
      <header className="leaderboard-top">
        <button
          className="back-button"
          type="button"
          onClick={onBackToGames}
        >
          <span>← Voltar aos Jogos</span>
        </button>
        <div className="leaderboard-title-block">
          <span className="eyebrow">HALL DA FAMA</span>
          <h1>Quadro de Líderes</h1>
          <p>Confira os melhores recordes e tempos conquistados na plataforma.</p>
        </div>
      </header>

      {/* Cards de Métricas */}
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-icon">🏆</span>
          <div className="metric-details">
            <span className="metric-title">Maior Pontuação</span>
            <span className="metric-value">{stats.highestScore} pts</span>
            <span className="metric-sub">Por {stats.topPlayer}</span>
          </div>
        </div>

        <div className="metric-card">
          <span className="metric-icon">👥</span>
          <div className="metric-details">
            <span className="metric-title">Recordes Registrados</span>
            <span className="metric-value">{stats.total}</span>
            <span className="metric-sub">Em 3 categorias ativas</span>
          </div>
        </div>

        <div className="metric-card">
          <span className="metric-icon">⚡</span>
          <div className="metric-details">
            <span className="metric-title">Jogo Mais Concorrido</span>
            <span className="metric-value">Jogo da Memória</span>
            <span className="metric-sub">Maior disputa de tempo</span>
          </div>
        </div>
      </div>

      {/* Controles de Filtro e Busca */}
      <div className="leaderboard-controls">
        <div className="game-tabs" role="tablist">
          {gameOptions.map((game) => (
            <button
              key={game.slug}
              className={`game-tab ${selectedGame === game.slug ? 'active' : ''}`}
              type="button"
              onClick={() => setSelectedGame(game.slug)}
            >
              <span>{game.icon}</span>
              <span>{game.label}</span>
            </button>
          ))}
        </div>

        <div className="search-and-sort">
          <input
            className="search-input"
            type="search"
            placeholder="Buscar jogador..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select
            className="sort-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'score' | 'recent')}
          >
            <option value="score">Maior Pontuação</option>
            <option value="recent">Mais Recentes</option>
          </select>
        </div>
      </div>

      {/* Tabela Complexa de Ranking */}
      <div className="leaderboard-table-wrap">
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>Pos.</th>
              <th>Jogador</th>
              <th>Jogo</th>
              <th>Pontuação</th>
              <th>Tempo</th>
              <th>Partidas / Eficiência</th>
              <th>Data & Hora</th>
            </tr>
          </thead>
          <tbody>
            {filteredEntries.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-state">
                  <span>🔍 Nenhum registro encontrado com os filtros atuais.</span>
                </td>
              </tr>
            ) : (
              filteredEntries.map((entry, index) => (
                <tr
                  key={entry.id}
                  className={`leaderboard-row ${index < 3 ? `top-${index + 1}` : ''}`}
                >
                  <td className="pos-cell">
                    <span className={`position-badge pos-${index + 1}`}>
                      {getMedal(index)}
                    </span>
                  </td>
                  <td className="player-cell">
                    <div className="player-info">
                      <div className="player-avatar">
                        {getInitials(entry.username)}
                      </div>
                      <span className="player-name">{entry.username}</span>
                    </div>
                  </td>
                  <td className="game-cell">
                    <span className="game-tag">{entry.gameName}</span>
                  </td>
                  <td className="score-cell">
                    <span className="score-badge">{entry.score} pts</span>
                  </td>
                  <td className="duration-cell">
                    <span className="time-badge">⏱ {entry.durationFormatted}</span>
                  </td>
                  <td className="stats-cell">
                    <span className="winrate-badge">
                      {entry.matchesPlayed} partidas ({entry.winRate})
                    </span>
                  </td>
                  <td className="date-cell">{formatDate(entry.achievedAt)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

