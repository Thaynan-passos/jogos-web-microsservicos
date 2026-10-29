import { useState, type FormEvent } from 'react'
import './App.css'

type GameId = 'tic-tac-toe' | 'memory' | 'rps'
type Player = 'X' | 'O'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api/v1').replace(/\/$/, '')
const ACCESS_TOKEN_KEY = 'playground_access_token'

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

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => sessionStorage.getItem(ACCESS_TOKEN_KEY) !== null,
  )
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isRegistering, setIsRegistering] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [isLoggingIn, setIsLoggingIn] = useState(false)
  const [isCreatingAccount, setIsCreatingAccount] = useState(false)
  const [loginError, setLoginError] = useState('')
  const [registrationError, setRegistrationError] = useState('')
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

  const winner = winningLines
    .map((line) => line.every((index) => board[index] && board[index] === board[line[0]]) ? board[line[0]] : null)
    .find(Boolean)
  const isDraw = !winner && board.every(Boolean)

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsLoggingIn(true)
    setLoginError('')

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), password }),
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

  async function handleRegistration(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsCreatingAccount(true)
    setRegistrationError('')

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), email: email.trim(), password }),
      })

      if (!response.ok) {
        setRegistrationError(
          response.status === 409
            ? 'Este usuário ou e-mail já está cadastrado.'
            : 'Não foi possível criar sua conta. Confira os dados e tente novamente.',
        )
        return
      }

      setPassword('')
      setEmail('')
      setRegistrationError('')
      setIsRegistering(false)
    } catch (error) {
      setRegistrationError(
        error instanceof TypeError
          ? 'Não foi possível conectar ao servidor. Verifique se o User Service está ativo.'
          : 'Não foi possível criar sua conta. Tente novamente.',
      )
    } finally {
      setIsCreatingAccount(false)
    }
  }

  function showRegistration() {
    setRegistrationError('')
    setLoginError('')
    setIsRegistering(true)
  }

  function showLogin() {
    setRegistrationError('')
    setLoginError('')
    setIsRegistering(false)
  }

  function handleLogout() {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY)
    setPassword('')
    setIsAuthenticated(false)
  }

  function playCell(index: number) {
    if (board[index] || winner || isDraw) return

    const nextBoard = [...board]
    nextBoard[index] = turn
    setBoard(nextBoard)
    const gameWinner = winningLines
      .map((line) => line.every((cell) => nextBoard[cell] && nextBoard[cell] === nextBoard[line[0]]) ? nextBoard[line[0]] : null)
      .find(Boolean)

    if (gameWinner) {
      setScores((current) => ({ ...current, [gameWinner]: current[gameWinner] + 1 }))
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
        setMatched((current) => [...current, ...nextFlipped])
        setFlipped([])
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
      setRpsScore((current) => ({ ...current, player: current.player + 1 }))
    } else {
      setRpsResult('O computador venceu esta rodada.')
      setRpsScore((current) => ({ ...current, computer: current.computer + 1 }))
    }
  }

  function renderGame() {
    if (activeGame === 'tic-tac-toe') {
      const status = winner ? `Jogador ${winner} venceu!` : isDraw ? 'Deu velha! Que tal outra?' : `Vez do jogador ${turn}`
      return (
        <section className="game-panel" aria-label="Jogo da Velha">
          <div className="game-heading">
            <div>
              <span className="eyebrow">DOIS JOGADORES</span>
              <h2>Jogo da Velha</h2>
              <p className="game-status" aria-live="polite">{status}</p>
            </div>
            <button className="secondary-button" onClick={resetTicTacToe}>↻ <span>Recomeçar</span></button>
          </div>
          <div className="scoreboard">
            <div className={turn === 'X' && !winner && !isDraw ? 'score active' : 'score'}><span className="score-mark x-mark">X</span><span>Jogador X</span><strong>{scores.X}</strong></div>
            <div className="score"><span className="draw-mark">＝</span><span>Empates</span><strong>{scores.draws}</strong></div>
            <div className={turn === 'O' && !winner && !isDraw ? 'score active' : 'score'}><span className="score-mark o-mark">O</span><span>Jogador O</span><strong>{scores.O}</strong></div>
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
              <p className="game-status" aria-live="polite">{isComplete ? `Parabéns! Você encontrou todos os pares em ${moves} jogadas.` : 'Encontre os pares de frutas iguais.'}</p>
            </div>
            <button className="secondary-button" onClick={resetMemory}>↻ <span>Embaralhar</span></button>
          </div>
          <div className="memory-stats"><span>Jogadas <strong>{moves}</strong></span><span>Pares <strong>{matched.length / 2} / {cards.length / 2}</strong></span></div>
          <div className="memory-board">
            {cards.map((card, index) => {
              const isVisible = flipped.includes(index) || matched.includes(index)
              return (
                <button
                  key={card.id}
                  className={`memory-card ${isVisible ? 'revealed' : ''} ${matched.includes(index) ? 'matched' : ''}`}
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
            <p className="game-status" aria-live="polite">{rpsResult || 'Faça sua escolha para começar!'}</p>
          </div>
        </div>
        <div className="rps-score"><span>Você <strong>{rpsScore.player}</strong></span><span className="versus">PLACAR</span><span>Computador <strong>{rpsScore.computer}</strong></span></div>
        <div className="rps-choices">
          {options.map((option) => (
            <button className={`rps-choice ${choice === option.name ? 'selected' : ''}`} key={option.name} onClick={() => playRps(option.name)}>
              <span className="rps-emoji">{option.emoji}</span>
              <span>{option.name}</span>
            </button>
          ))}
        </div>
        {choice && computerChoice && (
          <p className="rps-round">Você escolheu <strong>{choice}</strong> · O computador escolheu <strong>{computerChoice}</strong></p>
        )}
      </section>
    )
  }

  if (!isAuthenticated) {
    return (
      <main className="login-page">
        <header className="login-topbar">
          <a className="brand" href="#" aria-label="Playground início">
            <span className="brand-icon">P</span> playground<span className="brand-dot">.</span>
          </a>
          <span className="login-topbar-note">UM INTERVALO BEM JOGADO</span>
        </header>

        <div className="login-layout">
          <section className="login-intro" aria-labelledby="login-title">
            <span className="login-kicker"><span>✦</span> SEU CANTINHO DE DIVERSÃO</span>
            <h1 id="login-title">Boas jogadas<br />começam com<br /><span>um olá.</span></h1>
            <p>{isRegistering ? 'Crie seu espaço para guardar suas jogadas e continuar se divertindo.' : 'Entre para continuar sua pausa e escolher o próximo desafio.'}</p>
            <div className="login-game-preview" aria-hidden="true">
              <span className="preview-tile preview-purple">✕</span>
              <span className="preview-tile preview-yellow">◉</span>
              <span className="preview-tile preview-green">✦</span>
              <span className="preview-sparkle">✳</span>
            </div>
            <span className="login-intro-caption">JOGUE NO SEU RITMO · DIVIRTA-SE</span>
          </section>

          <section className="login-card" aria-label={isRegistering ? 'Criar uma conta' : 'Entrar na sua conta'}>
            <div className="login-card-icon" aria-hidden="true">✦</div>
            <span className="login-card-eyebrow">{isRegistering ? 'FAÇA PARTE DA TURMA' : 'BEM-VINDO DE VOLTA'}</span>
            <h2>{isRegistering ? 'Crie sua conta' : 'Entre na sua conta'}</h2>
            <p className="login-card-description">{isRegistering ? 'É rápido. Depois é só escolher um jogo.' : 'Que bom ter você por aqui. Vamos jogar?'}</p>

            <form className="login-form" onSubmit={isRegistering ? handleRegistration : handleLogin}>
              <label htmlFor="username">{isRegistering ? 'Nome de usuário' : 'Usuário ou e-mail'}</label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                placeholder={isRegistering ? 'Escolha um nome para jogar' : 'Como podemos te chamar?'}
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
              />

              {isRegistering && (
                <>
                  <label className="form-field-spaced" htmlFor="email">E-mail</label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    placeholder="seuemail@exemplo.com"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    required
                  />
                </>
              )}

              <div className={isRegistering ? 'password-label-row registration-password-label' : 'password-label-row'}>
                <label htmlFor="password">Senha</label>
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
                  {showPassword ? 'Ocultar' : 'Mostrar'}
                </button>
              </div>

              {(loginError || registrationError) && <p className="login-error" role="alert">{loginError || registrationError}</p>}

              <button className="login-submit" type="submit" disabled={isRegistering ? isCreatingAccount : isLoggingIn}>
                {isRegistering ? (isCreatingAccount ? 'Criando...' : 'Criar conta') : (isLoggingIn ? 'Entrando...' : 'Entrar')}
                {!(isRegistering ? isCreatingAccount : isLoggingIn) && <span aria-hidden="true">→</span>}
              </button>
            </form>

            <button className="login-switch" type="button" onClick={isRegistering ? showLogin : showRegistration}>
              {isRegistering ? 'Já tenho uma conta · Entrar' : 'Ainda não tenho uma conta · Criar cadastro'}
            </button>
            <p className="login-security-note"><span aria-hidden="true">⌑</span> Seus dados são protegidos com segurança.</p>
          </section>
        </div>

        <footer className="login-footer">
          <span>FEITO PARA UMA PAUSA FELIZ <span className="footer-heart">♥</span></span>
          <span>ESCOLHA · JOGUE · REPITA</span>
        </footer>
      </main>
    )
  }

  return (
    <main className="arcade">
      <header className="topbar">
        <a className="brand" href="#" aria-label="Playground início"><span className="brand-icon">P</span> playground<span className="brand-dot">.</span></a>
        <div className="topbar-actions">
          <span className="topbar-note"><span className="online-dot" /> diversão sem complicação</span>
          <button className="logout-button" type="button" onClick={handleLogout}>Sair</button>
        </div>
      </header>

      <section className="welcome">
        <span className="welcome-label"><span>✦</span> SEU CANTINHO DE DIVERSÃO</span>
        <h1>Uma pausa para<br /><span>brincar um pouco.</span></h1>
        <p>Jogos simples, boas disputas e diversão garantida.<br className="desktop-break" /> Escolha um jogo e vamos nessa!</p>
        <div className="welcome-doodle doodle-one">✳</div>
        <div className="welcome-doodle doodle-two">✦</div>
      </section>

      <section className="games-section">
        <div className="section-heading">
          <div><span className="eyebrow">ESCOLHA SEU JOGO</span><h2>O que vamos jogar?</h2></div>
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
              <span className="game-card-footer"><span>{game.players}</span><span className="card-arrow">↗</span></span>
            </button>
          ))}
        </div>
        {renderGame()}
      </section>

      <footer className="footer"><span>FEITO PARA UMA PAUSA FELIZ <span className="footer-heart">♥</span></span><span>ESCOLHA · JOGUE · REPITA</span></footer>
    </main>
  )
}

export default App
