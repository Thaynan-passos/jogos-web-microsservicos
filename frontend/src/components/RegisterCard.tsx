import { useState, type FormEvent } from 'react'

interface RegisterCardProps {
  apiBaseUrl: string
  onSwitchToLogin: (registeredUsername?: string) => void
}

export function RegisterCard({ apiBaseUrl, onSwitchToLogin }: RegisterCardProps) {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  async function handleRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')
    setSuccessMessage('')

    const trimmedUsername = username.trim()
    const trimmedEmail = email.trim()

    if (trimmedUsername.length < 3) {
      setErrorMessage('O nome de usuário deve ter pelo menos 3 caracteres.')
      return
    }

    if (password.length < 8) {
      setErrorMessage('A senha precisa ter no mínimo 8 caracteres.')
      return
    }

    if (password !== confirmPassword) {
      setErrorMessage('As senhas não coincidem. Confira e tente novamente.')
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch(`${apiBaseUrl}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: trimmedUsername,
          email: trimmedEmail,
          password,
        }),
      })

      if (!response.ok) {
        if (response.status === 409) {
          setErrorMessage('Este nome de usuário ou e-mail já está em uso.')
        } else if (response.status === 422) {
          setErrorMessage('Dados inválidos. Verifique o e-mail e os campos informados.')
        } else {
          setErrorMessage('Não foi possível realizar o cadastro no momento. Tente novamente.')
        }
        return
      }

      setSuccessMessage('Conta criada com sucesso! Redirecionando para o login...')
      setTimeout(() => {
        onSwitchToLogin(trimmedUsername)
      }, 1500)
    } catch {
      setErrorMessage('Não foi possível conectar ao servidor. Verifique se os serviços estão ativos.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="login-card" aria-label="Criar nova conta">
      <div className="login-card-icon" aria-hidden="true">✦</div>
      <span className="login-card-eyebrow">NOVA CONTA</span>
      <h2>Cadastre-se</h2>
      <p className="login-card-description">Crie sua conta para salvar suas partidas e competir no ranking.</p>

      {errorMessage && (
        <div className="auth-alert auth-alert-error" role="alert">
          <span>⚠️</span> {errorMessage}
        </div>
      )}

      {successMessage && (
        <div className="auth-alert auth-alert-success" role="status">
          <span>🎉</span> {successMessage}
        </div>
      )}

      <form className="login-form" onSubmit={handleRegister}>
        <label htmlFor="reg-username">Nome de usuário</label>
        <input
          id="reg-username"
          name="username"
          type="text"
          autoComplete="username"
          placeholder="Ex: JogadorAlpha"
          minLength={3}
          maxLength={50}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <label htmlFor="reg-email">E-mail</label>
        <input
          id="reg-email"
          name="email"
          type="email"
          autoComplete="email"
          placeholder="seuemail@exemplo.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <div className="password-label-row">
          <label htmlFor="reg-password">Senha (mín. 8 caracteres)</label>
        </div>
        <div className="password-input-wrap">
          <input
            id="reg-password"
            name="password"
            type={showPassword ? 'text' : 'password'}
            autoComplete="new-password"
            placeholder="Crie uma senha segura"
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button
            className="password-toggle"
            type="button"
            onClick={() => setShowPassword((prev) => !prev)}
            aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
          >
            {showPassword ? 'ocultar' : 'mostrar'}
          </button>
        </div>

        <label htmlFor="reg-confirm-password">Confirmar senha</label>
        <input
          id="reg-confirm-password"
          name="confirmPassword"
          type={showPassword ? 'text' : 'password'}
          autoComplete="new-password"
          placeholder="Repita sua senha"
          minLength={8}
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />

        <button className="login-button" type="submit" disabled={isLoading}>
          <span>{isLoading ? 'Cadastrando...' : 'Finalizar Cadastro'}</span>
          {!isLoading && <span aria-hidden="true">→</span>}
        </button>
      </form>

      <div className="auth-footer-links">
        <span>Já possui uma conta?</span>
        <button
          className="link-button"
          type="button"
          onClick={() => onSwitchToLogin()}
        >
          Fazer login
        </button>
      </div>
    </section>
  )
}

