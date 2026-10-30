import { useState, useEffect, type FormEvent } from 'react'
import './App.css'
import type { AuthMode, GameId, Player, RankingEntry, ViewMode } from './types.ts'
import { RegisterCard } from './components/RegisterCard.tsx'
import { RecoveryCard } from './components/RecoveryCard.tsx'
import { QuickRanking } from './components/QuickRanking.tsx'
import { LeaderboardView } from './components/LeaderboardView.tsx'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001/api/v1').replace(/\/$/, '')
const RANK_API_URL = (import.meta.env.VITE_RANK_API_URL ?? 'http://localhost:8003/api/v1').replace(/\/$/, '')
const RECOVERY_API_URL = (import.meta.env.VITE_RECOVERY_API_URL ?? 'http://localhost:8004/api/v1').replace(/\/$/, '')

const ACCESS_TOKEN_KEY = 'playground_access_token'
const USERNAME_KEY = 'playground_username'

const games: { id: GameId; icon: string; title: string; description: string; players: string }[] = [
  {
    id: 'tic-tac-toe',
    icon: '⭕',
    title: 'Jogo da Velha',
    description: 'Clássico, rápido e perfeito para dois.',
    players: '2 jogadores',
  },
  {
    id: 'memory',
    icon: '🧠',
    title: 'Jogo da Memória',
    description: 'Encontre todos os pares de cartas.',
    players: '1 jogador',
  },
  {
    id: 'rps',
    icon: '✊',
    title: 'Pedra, Papel e Tesoura',
    description: 'Escolha sua jogada e desafie o computador.',
    players: 'Contra o computador',
  },
]

const winningLines = [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8],
  [2, 4, 6],
]

const cardFaces = ['🍓', '🍋', '🍇', '🍉', '🍒', '🥝']

function createDeck() {
  return [...cardFaces, ...cardFaces]
    .map((face, index) => ({ id: index, face }))
    .sort(() => Math.random() - 0.5)
}

function getComputerMove(options: string[]) {
  return options[Math.floor(Math.random() * options.length)]
}

const DEFAULT_RANKINGS: RankingEntry[] = [
  {
    id: 'r1',
    position: 1,
    userId: 'u1',
    username: 'AnaMemoryQueen',
    gameSlug: 'memory',
    gameName: 'Jogo da Memória',
    score: 820,
    durationMs: 28500,
    durationFormatted: '28s',
    achievedAt: '2026-10-30T10:15:00Z',
    matchesPlayed: 24,
    winRate: '95%',
  },
  {
    id: 'r2',
    position: 2,
    userId: 'u2',
    username: 'DiegoCards',
    gameSlug: 'memory',
    gameName: 'Jogo da Memória',
    score: 690,
    durationMs: 34000,
    durationFormatted: '34s',
    achievedAt: '2026-10-30T11:45:00Z',
    matchesPlayed: 19,
    winRate: '84%',
  },
  {
    id: 'r3',
    position: 3,
    userId: 'u3',
    username: 'LucasMestre',
    gameSlug: 'tic-tac-toe',
    gameName: 'Jogo da Velha',
    score: 450,
    durationMs: 42000,
    durationFormatted: '42s',
    achievedAt: '2026-10-29T16:20:00Z',
    matchesPlayed: 18,
    winRate: '89%',
  },
  {
    id: 'r4',
    position: 4,
    userId: 'u4',
    username: 'Beatriz_Gamer',
    gameSlug: 'tic-tac-toe',
    gameName: 'Jogo da Velha',
    score: 390,
    durationMs: 48000,
    durationFormatted: '48s',
    achievedAt: '2026-10-30T09:10:00Z',
    matchesPlayed: 14,
    winRate: '78%',
  },
  {
    id: 'r5',
    position: 5,
    userId: 'u5',
    username: 'GabrielTactics',
    gameSlug: 'rps',
    gameName: 'Pedra, Papel e Tesoura',
    score: 380,
    durationMs: 35000,
    durationFormatted: '35s',
    achievedAt: '2026-10-29T18:00:00Z',
    matchesPlayed: 15,
    winRate: '80%',
  },
]

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => sessionStorage.getItem(ACCESS_TOKEN_KEY) !== null,
  )
  const [currentUsername, setCurrentUsername] = useState(
    () => sessionStorage.getItem(USERNAME_KEY) ?? 'Jogador',
  )
  const [authMode, setAuthMode] = useState<AuthMode>('login')
  const [viewMode, setViewMode] = useState<ViewMode>('games')
  const [registrationNotice, setRegistrationNotice] = useState('')

  // Login form state
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoggingIn, setIsLoggingIn] = useState(false)
  const [loginError, setLoginError] = useState('')

  // Game state
  const [activeGame, setActiveGame] = useState<GameId>('tic-tac-toe')
  const [board, setBoard] = useState<Array<Player | null>>(Array(9).fill(null))
  const [turn, setTurn] = useState<Player>('X')
  const [scores, setScores] = useState({ X: 0, O: 0, draws: 0 })

  const [cards, setCards] = useState(() =>
    cardFaces.flatMap((face) => [face, face]).map((face, index) => ({ id: index, face })),
  )
  const [flipped, setFlipped] = useState<number[]>([])
  const [matched, setMatched] = useState<number[]>([])
  const [moves, setMoves] = useState(0)

  const [choice, setChoice] = useState<string | null>(null)
  const [computerChoice, setComputerChoice] = useState<string | null>(null)
  const [rpsResult, setRpsResult] = useState('')
  const [rpsScore, setRpsScore] = useState({ player: 0, computer: 0 })

  // Ranking state
  const [rankings, setRankings] = useState<RankingEntry[]>(DEFAULT_RANKINGS)

  // Carregar rankings do backend se disponível
  useEffect(() => {
    async function fetchRankings() {
      try {
        const response = await fetch(`${RANK_API_URL}/rankings/`)
        if (response.ok) {
          const data = await response.json()
          if (Array.isArray(data) && data.length > 0) {
            const formatted: RankingEntry[] = data.map((item: any, idx: number) => ({
              id: item.id || `rank-${idx}`,
              position: item.position || idx + 1,
              userId: item.user_id || `u-${idx}`,
              username: item.username || 'Jogador',
              gameSlug: item.game_slug || 'all',
              gameName: item.game_name || 'Geral',
              score: item.score || 0,
              durationMs: item.duration_ms || 0,
              durationFormatted: item.duration_formatted || `${Math.round((item.duration_ms || 0) / 1000)}s`,
              achievedAt: item.achieved_at || new Date().toISOString(),
              matchesPlayed: item.matches_played || 1,
              winRate: item.win_rate || '100%',
            }))
            setRankings(formatted)
          }
        }
      } catch {
        // Usa dados pré-configurados em caso de offline
      }
    }
    fetchRankings()
  }, [])

  // Registrar pontuação de partidas
  async function submitScore(gameSlug: string, score: number, durationMs: number = 30000) {
    const userToSave = currentUsername || 'Jogador'
    try {
      await fetch(`${RANK_API_URL}/rankings/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: userToSave,
          game_slug: gameSlug,
          score,
          duration_ms: durationMs,
        }),
      })
    } catch {
      // Ignora falha de rede para não travar a jogatina
    }

    // Atualiza localmente
    setRankings((prev) => {
      const existing = prev.find(
        (e) => e.username.toLowerCase() === userToSave.toLowerCase() && e.gameSlug === gameSlug,
      )
      if (existing) {
        return prev.map((e) =>
          e.id === existing.id
            ? {
                ...e,
                score: Math.max(e.score, score),
                matchesPlayed: e.matchesPlayed + 1,
              }
            : e,
        )
      }
      const newEntry: RankingEntry = {
        id: `r-${Date.now()}`,
        position: prev.length + 1,
        userId: 'current-user',
        username: userToSave,
        gameSlug,
        gameName:
          gameSlug === 'tic-tac-toe'
            ? 'Jogo da Velha'
            : gameSlug === 'memory'
            ? 'Jogo da Memória'
            : 'Pedra, Papel e Tesoura',
        score,
        durationMs,
        durationFormatted: `${Math.round(durationMs / 1000)}s`,
        achievedAt: new Date().toISOString(),
        matchesPlayed: 1,
        winRate: '100%',
      }
      return [newEntry, ...prev]
    })
  }

  const winner = winningLines
    .map((line) => (board[line[0]] && board[line[0]] === board[line[1]] && board[line[0]] === board[line[2]] ? board[line[0]] : null))
    .find(Boolean)
  const isDraw = !winner && board.every(Boolean)

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsLoggingIn(true)
    setLoginError('')
    setRegistrationNotice('')

    const trimmedUser = username.trim()

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: trimmedUser, password }),
      })
      const payload: unknown = await response.json()

      if (!response.ok) {
        setLoginError(
          response.status === 401
            ? 'Usuário ou senha não conferem. Confira seus dados e tente novamente.'
            : 'Não foi possível entrar agora. Tente novamente em instantes.',
        )
        return
      }

      if (
        typeof payload !== 'object' ||
        payload === null ||
        !('access_token' in payload) ||
        typeof payload.access_token !== 'string'
      ) {
        setLoginError('O servidor retornou uma resposta inesperada. Tente novamente.')
        return
      }

      sessionStorage.setItem(ACCESS_TOKEN_KEY, payload.access_token)
      sessionStorage.setItem(USERNAME_KEY, trimmedUser)
      setCurrentUsername(trimmedUser)
      setPassword('')
      setIsAuthenticated(true)
    } catch (error) {
      setLoginError(
        error instanceof TypeError
          ? 'Não foi possível conectar ao servidor. Verifique se o User Service está ativo.'
          : 'Não foi possível concluir o login. Tente novamente.',
      )
    } finally {
      setIsLoggingIn(false)
    }
  }

  function handleLogout() {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY)
    sessionStorage.removeItem(USERNAME_KEY)
    setPassword('')
    setIsAuthenticated(false)
    setAuthMode('login')
  }

  function playCell(index: number) {
    if (board[index] || winner || isDraw) return

    const nextBoard = [...board]
    nextBoard[index] = turn
    setBoard(nextBoard)

    const gameWinner = winningLines
      .map((line) =>
        nextBoard[line[0]] &&
        nextBoard[line[0]] === nextBoard[line[1]] &&
        nextBoard[line[0]] === nextBoard[line[2]]
          ? nextBoard[line[0]]
          : null,
      )
      .find(Boolean)

    if (gameWinner) {
      setScores((current) => ({ ...current, [gameWinner]: current[gameWinner] + 1 }))
      submitScore('tic-tac-toe', (scores.X + 1) * 60)
    } else if (nextBoard.every(Boolean)) {
      setScores((current) => ({ ...current, draws: current.draws + 1 }))
    } else {
      setTurn(turn === 'X' ? 'O' : 'X')
    }
  }

  function resetTicTacToe() {
    setBoard(Array(9).fill(null))
    setTurn('X')
  }

  function resetMemory() {
    setCards(createDeck())
    setFlipped([])
    setMatched([])
    setMoves(0)
  }

  function flipCard(index: number) {
    if (flipped.length === 2 || flipped.includes(index) || matched.includes(index)) return

    const nextFlipped = [...flipped, index]
    setFlipped(nextFlipped)

    if (nextFlipped.length === 2) {
      setMoves((current) => current + 1)
      if (cards[nextFlipped[0]].face === cards[nextFlipped[1]].face) {
        const nextMatched = [...matched, ...nextFlipped]
        setMatched(nextMatched)
        setFlipped([])
        if (nextMatched.length === cards.length) {
          // Concluiu todos os pares
          const memoryScore = Math.max(100, 1000 - (moves + 1) * 35)
          submitScore('memory', memoryScore, 25000)
        }
      } else {
        window.setTimeout(() => setFlipped([]), 850)
      }
    }
  }

  function playRps(playerChoice: string) {
    const options = ['Pedra', 'Papel', 'Tesoura']
    const cpuChoice = getComputerMove(options)
    setChoice(playerChoice)
    setComputerChoice(cpuChoice)

    if (playerChoice === cpuChoice) {
      setRpsResult('Empate! Boa jogada dos dois.')
    } else if (
      (playerChoice === 'Pedra' && cpuChoice === 'Tesoura') ||
      (playerChoice === 'Papel' && cpuChoice === 'Pedra') ||
      (playerChoice === 'Tesoura' && cpuChoice === 'Papel')
    ) {
      setRpsResult('Você venceu esta rodada!')
      setRpsScore((current) => {
        const newPlayerScore = current.player + 1
        submitScore('rps', newPlayerScore * 50)
        return { ...current, player: newPlayerScore }
      })
    } else {
      setRpsResult('O computador venceu esta rodada.')
      setRpsScore((current) => ({ ...current, computer: current.computer + 1 }))
    }
  }

  function renderGame() {
    if (activeGame === 'tic-tac-toe') {
      const status = winner
        ? `Jogador ${winner} venceu!`
        : isDraw
        ? 'Deu velha! Que tal outra?'
        : `Vez do jogador ${turn}`
      return (
        <section className="game-panel" aria-label="Jogo da Velha">
          <div className="game-heading">
            <div>
              <span className="eyebrow">DOIS JOGADORES</span>
              <h2>Jogo da Velha</h2>
              <p className="game-status" aria-live="polite">
                {status}
              </p>
            </div>
            <button className="secondary-button" onClick={resetTicTacToe}>
              ↻ <span>Recomeçar</span>
            </button>
          </div>
          <div className="scoreboard">
            <div className={turn === 'X' && !winner && !isDraw ? 'score active' : 'score'}>
              <span className="score-mark x-mark">X</span>
              <span>Jogador X</span>
              <strong>{scores.X}</strong>
            </div>
            <div className="score">
              <span className="draw-mark">＝</span>
              <span>Empates</span>
              <strong>{scores.draws}</strong>
            </div>
            <div className={turn === 'O' && !winner && !isDraw ? 'score active' : 'score'}>
              <span className="score-mark o-mark">O</span>
              <span>Jogador O</span>
              <strong>{scores.O}</strong>
            </div>
          </div>
          <div className="tic-board" role="grid" aria-label="Tabuleiro do Jogo da Velha">
            {board.map((cell, index) => (
              <button
                key={index}
                className={`tic-cell ${cell === 'X' ? 'x-mark' : cell === 'O' ? 'o-mark' : ''}`}
                onClick={() => playCell(index)}
                disabled={Boolean(cell || winner || isDraw)}
                aria-label={`Casa ${index + 1}${cell ? `, ${cell}` : ', vazia'}`}
                role="gridcell"
              >
                {cell}
              </button>
            ))}
          </div>
          <p className="game-hint">Alinhe três símbolos na horizontal, vertical ou diagonal.</p>
        </section>
      )
    }

    if (activeGame === 'memory') {
      const isComplete = matched.length === cards.length
      return (
        <section className="game-panel" aria-label="Jogo da Memória">
          <div className="game-heading">
            <div>
              <span className="eyebrow">TREINE SUA MEMÓRIA</span>
              <h2>Jogo da Memória</h2>
              <p className="game-status" aria-live="polite">
                {isComplete
                  ? `Parabéns! Você encontrou todos os pares em ${moves} jogadas.`
                  : 'Encontre os pares de frutas iguais.'}
              </p>
            </div>
            <button className="secondary-button" onClick={resetMemory}>
              ↻ <span>Embaralhar</span>
            </button>
          </div>
          <div className="memory-stats">
            <span>
              Jogadas <strong>{moves}</strong>
            </span>
            <span>
              Pares <strong>{matched.length / 2} / {cards.length / 2}</strong>
            </span>
          </div>
          <div className="memory-board">
            {cards.map((card, index) => {
              const isVisible = flipped.includes(index) || matched.includes(index)
              return (
                <button
                  key={card.id}
                  className={`memory-card ${isVisible ? 'revealed' : ''} ${
                    matched.includes(index) ? 'matched' : ''
                  }`}
                  onClick={() => flipCard(index)}
                  disabled={isVisible || flipped.length === 2}
                  aria-label={isVisible ? `Carta ${card.face}` : `Revelar carta ${index + 1}`}
                >
                  {isVisible ? card.face : '?'}
                </button>
              )
            })}
          </div>
        </section>
      )
    }

    const options = [
      { name: 'Pedra', emoji: '✊' },
      { name: 'Papel', emoji: '✋' },
      { name: 'Tesoura', emoji: '✌️' },
    ]

    return (
      <section className="game-panel" aria-label="Pedra, Papel e Tesoura">
        <div className="game-heading">
          <div>
            <span className="eyebrow">VOCÊ CONTRA O COMPUTADOR</span>
            <h2>Pedra, Papel e Tesoura</h2>
            <p className="game-status" aria-live="polite">
              {rpsResult || 'Faça sua escolha para começar!'}
            </p>
          </div>
        </div>
        <div className="rps-score">
          <span>
            Você <strong>{rpsScore.player}</strong>
          </span>
          <span className="versus">PLACAR</span>
          <span>
            Computador <strong>{rpsScore.computer}</strong>
          </span>
        </div>
        <div className="rps-choices">
          {options.map((option) => (
            <button
              className={`rps-choice ${choice === option.name ? 'selected' : ''}`}
              key={option.name}
              onClick={() => playRps(option.name)}
            >
              <span className="rps-emoji">{option.emoji}</span>
              <span>{option.name}</span>
            </button>
          ))}
        </div>
        {choice && computerChoice && (
          <p className="rps-round">
            Você escolheu <strong>{choice}</strong> · O computador escolheu{' '}
            <strong>{computerChoice}</strong>
          </p>
        )}
      </section>
    )
  }

  // Visualização de telas não autenticadas
  if (!isAuthenticated) {
    return (
      <main className="login-page">
        <header className="login-topbar">
          <a className="brand" href="#" aria-label="Playground início">
            <span className="brand-icon">P</span> playground<span className="brand-dot">.</span>
          </a>
          <span className="login-topbar-note">PLATAFORMA DE JOGOS & DESAFIOS</span>
        </header>

        <div className="login-layout">
          <section className="login-intro" aria-labelledby="login-title">
            <span className="login-kicker">
              <span>✦</span> SEU CANTINHO DE DIVERSÃO
            </span>
            <h1 id="login-title">
              Boas jogadas<br />
              começam com<br />
              <span>um olá.</span>
            </h1>
            <p>Faça login ou crie sua conta para registrar suas vitórias e pontuações no ranking.</p>
            <div className="login-game-preview" aria-hidden="true">
              <span className="preview-tile preview-purple">✕</span>
              <span className="preview-tile preview-yellow">◉</span>
              <span className="preview-tile preview-green">✦</span>
              <span className="preview-sparkle">✳</span>
            </div>
            <span className="login-intro-caption">MICROSSERVIÇOS · MULTIPLAYER · RANKINGS</span>
          </section>

          {authMode === 'register' && (
            <RegisterCard
              apiBaseUrl={API_BASE_URL}
              onSwitchToLogin={(registeredUser) => {
                if (registeredUser) {
                  setUsername(registeredUser)
                  setRegistrationNotice('Conta criada com sucesso! Faça login abaixo.')
                }
                setAuthMode('login')
              }}
            />
          )}

          {authMode === 'recovery' && (
            <RecoveryCard
              recoveryApiUrl={RECOVERY_API_URL}
              onSwitchToLogin={() => setAuthMode('login')}
            />
          )}

          {authMode === 'login' && (
            <section className="login-card" aria-label="Entrar na sua conta">
              <div className="login-card-icon" aria-hidden="true">✦</div>
              <span className="login-card-eyebrow">BEM-VINDO DE VOLTA</span>
              <h2>Entre na sua conta</h2>
              <p className="login-card-description">Que bom ter você por aqui. Vamos jogar?</p>

              {registrationNotice && (
                <div className="auth-alert auth-alert-success" role="status">
                  <span>🎉</span> {registrationNotice}
                </div>
              )}

              {loginError && (
                <div className="auth-alert auth-alert-error" role="alert">
                  <span>⚠️</span> {loginError}
                </div>
              )}

              <form className="login-form" onSubmit={handleLogin}>
                <label htmlFor="username">Usuário ou e-mail</label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  placeholder="Como podemos te chamar?"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  required
                />

                <div className="password-label-row">
                  <label htmlFor="password">Senha</label>
                  <button
                    className="forgot-link-btn"
                    type="button"
                    onClick={() => {
                      setLoginError('')
                      setAuthMode('recovery')
                    }}
                  >
                    Esqueceu a senha?
                  </button>
                </div>
                <div className="password-input-wrap">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    placeholder="Digite sua senha"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                  />
                  <button
                    className="password-toggle"
                    type="button"
                    onClick={() => setShowPassword((current) => !current)}
                    aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                    aria-pressed={showPassword}
                  >
                    {showPassword ? 'ocultar' : 'mostrar'}
                  </button>
                </div>

                <button className="login-button" type="submit" disabled={isLoggingIn}>
                  <span>{isLoggingIn ? 'Entrando...' : 'Entrar no Playground'}</span>
                  {!isLoggingIn && <span aria-hidden="true">→</span>}
                </button>
              </form>

              <div className="auth-footer-links">
                <span>Ainda não tem conta?</span>
                <button
                  className="link-button"
                  type="button"
                  onClick={() => {
                    setLoginError('')
                    setAuthMode('register')
                  }}
                >
                  Criar conta gratuita
                </button>
              </div>

              <p className="login-security-note">
                <span aria-hidden="true">⌑</span> Seus dados são protegidos com segurança.
              </p>
            </section>
          )}
        </div>

        <footer className="login-footer">
          <span>FEITO PARA UMA PAUSA FELIZ <span className="footer-heart">♥</span></span>
          <span>ESCOLHA · JOGUE · REPITA</span>
        </footer>
      </main>
    )
  }

  // Visualização Autenticada
  return (
    <main className="arcade">
      <header className="topbar">
        <a className="brand" href="#" aria-label="Playground início" onClick={() => setViewMode('games')}>
          <span className="brand-icon">P</span> playground<span className="brand-dot">.</span>
        </a>
        <div className="topbar-nav">
          <button
            className={`nav-tab-btn ${viewMode === 'games' ? 'active' : ''}`}
            type="button"
            onClick={() => setViewMode('games')}
          >
            🎮 Jogos
          </button>
          <button
            className={`nav-tab-btn ${viewMode === 'leaderboard' ? 'active' : ''}`}
            type="button"
            onClick={() => setViewMode('leaderboard')}
          >
            🏆 Leaderboard
          </button>
        </div>
        <div className="topbar-actions">
          <span className="user-greeting">Olá, <strong>{currentUsername}</strong></span>
          <button className="logout-button" type="button" onClick={handleLogout}>
            Sair
          </button>
        </div>
      </header>

      {viewMode === 'leaderboard' ? (
        <LeaderboardView
          entries={rankings}
          onBackToGames={() => setViewMode('games')}
        />
      ) : (
        <>
          <section className="welcome">
            <span className="welcome-label">
              <span>✦</span> SEU CANTINHO DE DIVERSÃO
            </span>
            <h1>
              Uma pausa para<br />
              <span>brincar um pouco.</span>
            </h1>
            <p>
              Jogos simples, boas disputas e diversão garantida.
              <br className="desktop-break" /> Escolha um jogo e vamos nessa!
            </p>
            <div className="welcome-doodle doodle-one">✳</div>
            <div className="welcome-doodle doodle-two">✦</div>
          </section>

          {/* Rank Básico em Destaque no Dashboard */}
          <QuickRanking
            entries={rankings}
            onOpenFullLeaderboard={() => setViewMode('leaderboard')}
          />

          <section className="games-section">
            <div className="section-heading">
              <div>
                <span className="eyebrow">ESCOLHA SEU JOGO</span>
                <h2>O que vamos jogar?</h2>
              </div>
              <span className="game-count">03 JOGOS DISPONÍVEIS</span>
            </div>
            <div className="game-picker">
              {games.map((game, index) => (
                <button
                  key={game.id}
                  className={`game-card ${activeGame === game.id ? 'selected' : ''}`}
                  onClick={() => setActiveGame(game.id)}
                  aria-pressed={activeGame === game.id}
                >
                  <span className={`game-icon game-icon-${index}`}>{game.icon}</span>
                  <span className="game-card-title">{game.title}</span>
                  <span className="game-card-description">{game.description}</span>
                  <span className="game-card-footer">
                    <span>{game.players}</span>
                    <span className="card-arrow">↗</span>
                  </span>
                </button>
              ))}
            </div>
            {renderGame()}
          </section>
        </>
      )}

      <footer className="footer">
        <span>FEITO PARA UMA PAUSA FELIZ <span className="footer-heart">♥</span></span>
        <span>ESCOLHA · JOGUE · REPITA</span>
      </footer>
    </main>
  )
}

export default App
