import { useState } from 'react'
import './App.css'

type GameId = 'tic-tac-toe' | 'memory' | 'rps'
type Player = 'X' | 'O'

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

  return (
    <main className="arcade">
      <header className="topbar">
        <a className="brand" href="#" aria-label="Playground início"><span className="brand-icon">P</span> playground<span className="brand-dot">.</span></a>
        <span className="topbar-note"><span className="online-dot" /> diversão sem complicação</span>
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
