import { useCallback, useEffect, useState } from 'react'
import type { ReactNode } from 'react'

type ManagerTab = 'users' | 'games' | 'sessions' | 'rankings'
type User = { id: string; username: string; email: string; is_active: boolean; is_admin: boolean }
type Game = { slug: string; name: string; description: string; enabled: boolean }
type Session = { id: string; game_slug: string; user_id: string | null; status: string; result: Record<string, unknown> }
type Ranking = { id: string; username: string; game_slug: string; score: number; duration_ms: number; matches_played: number; win_rate: string }

type Props = {
  token: string
  userApiUrl: string
  gameApiUrl: string
  rankApiUrl: string
  onGamesChanged: () => Promise<void>
}

async function request<T>(url: string, token: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, ...options?.headers },
  })
  if (!response.ok) throw new Error((await response.text()) || 'Não foi possível concluir a operação')
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export function ManagerView({ token, userApiUrl, gameApiUrl, rankApiUrl, onGamesChanged }: Props) {
  const [tab, setTab] = useState<ManagerTab>('users')
  const [users, setUsers] = useState<User[]>([])
  const [games, setGames] = useState<Game[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [rankings, setRankings] = useState<Ranking[]>([])
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [userForm, setUserForm] = useState({ username: '', email: '', password: '', is_admin: false })
  const [gameForm, setGameForm] = useState({ slug: '', name: '', description: '' })
  const [rankingForm, setRankingForm] = useState({ username: '', game_slug: 'memory', score: '0', duration_ms: '30000' })
  const [sessionForm, setSessionForm] = useState({ game_slug: 'memory', user_id: '' })

  const loadAll = useCallback(async () => {
    try {
      const [usersData, gamesData, sessionsData, rankingsData] = await Promise.all([
        request<User[]>(`${userApiUrl}/users`, token),
        request<Game[]>(`${gameApiUrl}/games?include_disabled=true`, token),
        request<Session[]>(`${gameApiUrl}/sessions?limit=100`, token),
        request<Ranking[]>(`${rankApiUrl}/rankings/?limit=100`, token),
      ])
      setUsers(usersData)
      setGames(gamesData)
      setSessions(sessionsData)
      setRankings(rankingsData)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Erro ao carregar dados')
    }
  }, [gameApiUrl, rankApiUrl, token, userApiUrl])

  useEffect(() => {
    const timerId = window.setTimeout(() => { void loadAll() }, 0)
    return () => window.clearTimeout(timerId)
  }, [loadAll])

  async function run(action: () => Promise<void>, message: string) {
    try {
      setError('')
      await action()
      setNotice(message)
      await loadAll()
      await onGamesChanged()
    }
    catch (operationError) { setError(operationError instanceof Error ? operationError.message : 'Erro na operação') }
  }

  return (
    <section className="manager-view">
      <div className="manager-heading">
        <div><span className="eyebrow">ÁREA RESTRITA</span><h1>Painel do gerente</h1><p>Gerencie usuários, jogos, sessões e pontuações persistidas.</p></div>
        <button className="secondary-button" type="button" onClick={() => void loadAll()}>Atualizar dados</button>
      </div>
      {notice && <p className="manager-notice">{notice}</p>}
      {error && <p className="manager-error">{error}</p>}
      <div className="manager-tabs">
        {(['users', 'games', 'sessions', 'rankings'] as ManagerTab[]).map((item) => <button key={item} type="button" className={tab === item ? 'active' : ''} onClick={() => setTab(item)}>{item === 'users' ? 'Usuários' : item === 'games' ? 'Jogos' : item === 'sessions' ? 'Sessões' : 'Rankings'}</button>)}
      </div>

      {tab === 'users' && <ManagerPanel title="Usuários" count={users.length} form={<form className="manager-form" onSubmit={(event) => { event.preventDefault(); void run(() => request(`${userApiUrl}/auth/register`, token, { method: 'POST', body: JSON.stringify(userForm) }).then(() => undefined), 'Usuário criado') }}><input placeholder="Usuário" value={userForm.username} onChange={(e) => setUserForm({ ...userForm, username: e.target.value })} required /><input type="email" placeholder="E-mail" value={userForm.email} onChange={(e) => setUserForm({ ...userForm, email: e.target.value })} required /><input type="password" placeholder="Senha" value={userForm.password} onChange={(e) => setUserForm({ ...userForm, password: e.target.value })} required /><label><input type="checkbox" checked={userForm.is_admin} onChange={(e) => setUserForm({ ...userForm, is_admin: e.target.checked })} /> Gerente</label><button type="submit">Criar usuário</button></form>}><table><thead><tr><th>Usuário</th><th>E-mail</th><th>Perfil</th><th>Status</th><th></th></tr></thead><tbody>{users.map((user) => <tr key={user.id}><td>{user.username}</td><td>{user.email}</td><td>{user.is_admin ? 'Gerente' : 'Jogador'}</td><td>{user.is_active ? 'Ativo' : 'Inativo'}</td><td><button type="button" onClick={() => void run(() => request(`${userApiUrl}/users/${user.id}`, token, { method: 'PUT', body: JSON.stringify({ is_active: !user.is_active }) }).then(() => undefined), 'Usuário atualizado')}>{user.is_active ? 'Desativar' : 'Ativar'}</button><button type="button" onClick={() => void run(() => request(`${userApiUrl}/users/${user.id}`, token, { method: 'DELETE' }).then(() => undefined), 'Usuário removido')}>Remover</button></td></tr>)}</tbody></table></ManagerPanel>}
      {tab === 'games' && <ManagerPanel title="Jogos" count={games.length} form={<form className="manager-form" onSubmit={(event) => { event.preventDefault(); void run(() => request(`${gameApiUrl}/games`, token, { method: 'POST', body: JSON.stringify(gameForm) }).then(() => undefined), 'Jogo criado') }}><input placeholder="Slug" value={gameForm.slug} onChange={(e) => setGameForm({ ...gameForm, slug: e.target.value })} required /><input placeholder="Nome" value={gameForm.name} onChange={(e) => setGameForm({ ...gameForm, name: e.target.value })} required /><input placeholder="Descrição" value={gameForm.description} onChange={(e) => setGameForm({ ...gameForm, description: e.target.value })} /><button type="submit">Criar jogo</button></form>}><table><thead><tr><th>Slug</th><th>Nome</th><th>Descrição</th><th>Status</th><th></th></tr></thead><tbody>{games.map((game) => <tr key={game.slug}><td>{game.slug}</td><td>{game.name}</td><td>{game.description}</td><td>{game.enabled ? 'Ativo' : 'Desativado'}</td><td><button type="button" onClick={() => void run(() => request(`${gameApiUrl}/games/${game.slug}`, token, { method: 'PUT', body: JSON.stringify({ enabled: !game.enabled }) }).then(() => undefined), 'Jogo atualizado')}>Alternar</button><button type="button" onClick={() => void run(() => request(`${gameApiUrl}/games/${game.slug}`, token, { method: 'DELETE' }).then(() => undefined), 'Jogo desativado')}>Desativar</button></td></tr>)}</tbody></table></ManagerPanel>}
      {tab === 'sessions' && <ManagerPanel title="Sessões" count={sessions.length} form={<form className="manager-form" onSubmit={(event) => { event.preventDefault(); void run(() => request(`${gameApiUrl}/sessions`, token, { method: 'POST', body: JSON.stringify({ game_slug: sessionForm.game_slug, user_id: sessionForm.user_id || null }) }).then(() => undefined), 'Sessão criada') }}><select value={sessionForm.game_slug} onChange={(e) => setSessionForm({ ...sessionForm, game_slug: e.target.value })}>{games.map((game) => <option key={game.slug} value={game.slug}>{game.name}</option>)}</select><input placeholder="ID do usuário (opcional)" value={sessionForm.user_id} onChange={(e) => setSessionForm({ ...sessionForm, user_id: e.target.value })} /><button type="submit">Criar sessão</button></form>}><table><thead><tr><th>Jogo</th><th>Usuário</th><th>Status</th><th></th></tr></thead><tbody>{sessions.map((session) => <tr key={session.id}><td>{session.game_slug}</td><td>{session.user_id || 'Anônimo'}</td><td>{session.status}</td><td><button type="button" onClick={() => void run(() => request(`${gameApiUrl}/sessions/${session.id}`, token, { method: 'PUT', body: JSON.stringify({ status: session.status === 'completed' ? 'in_progress' : 'completed' }) }).then(() => undefined), 'Sessão atualizada')}>Editar status</button><button type="button" onClick={() => void run(() => request(`${gameApiUrl}/sessions/${session.id}`, token, { method: 'DELETE' }).then(() => undefined), 'Sessão removida')}>Remover</button></td></tr>)}</tbody></table></ManagerPanel>}
      {tab === 'rankings' && <ManagerPanel title="Rankings" count={rankings.length} form={<form className="manager-form" onSubmit={(event) => { event.preventDefault(); void run(() => request(`${rankApiUrl}/rankings/`, token, { method: 'POST', body: JSON.stringify({ username: rankingForm.username, game_slug: rankingForm.game_slug, score: Number(rankingForm.score), duration_ms: Number(rankingForm.duration_ms) }) }).then(() => undefined), 'Pontuação criada') }}><input placeholder="Usuário" value={rankingForm.username} onChange={(e) => setRankingForm({ ...rankingForm, username: e.target.value })} required /><input placeholder="Slug do jogo" value={rankingForm.game_slug} onChange={(e) => setRankingForm({ ...rankingForm, game_slug: e.target.value })} required /><input type="number" placeholder="Pontuação" value={rankingForm.score} onChange={(e) => setRankingForm({ ...rankingForm, score: e.target.value })} /><input type="number" placeholder="Duração (ms)" value={rankingForm.duration_ms} onChange={(e) => setRankingForm({ ...rankingForm, duration_ms: e.target.value })} /><button type="submit">Criar pontuação</button></form>}><table><thead><tr><th>Usuário</th><th>Jogo</th><th>Pontos</th><th>Partidas</th><th></th></tr></thead><tbody>{rankings.map((ranking) => <tr key={ranking.id}><td>{ranking.username}</td><td>{ranking.game_slug}</td><td>{ranking.score}</td><td>{ranking.matches_played}</td><td><button type="button" onClick={() => void run(() => request(`${rankApiUrl}/rankings/${ranking.id}`, token, { method: 'PUT', body: JSON.stringify({ score: ranking.score + 1 }) }).then(() => undefined), 'Pontuação atualizada')}>+1 ponto</button><button type="button" onClick={() => void run(() => request(`${rankApiUrl}/rankings/${ranking.id}`, token, { method: 'DELETE' }).then(() => undefined), 'Pontuação removida')}>Remover</button></td></tr>)}</tbody></table></ManagerPanel>}
    </section>
  )
}

function ManagerPanel({ title, count, form, children }: { title: string; count: number; form: ReactNode; children: ReactNode }) {
  return <section className="manager-panel"><div className="manager-panel-heading"><div><span className="eyebrow">REGISTROS</span><h2>{title}</h2></div><strong>{String(count).padStart(2, '0')}</strong></div>{form}<div className="manager-table-wrap">{children}</div></section>
}
