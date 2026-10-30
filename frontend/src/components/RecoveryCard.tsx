import { useState, type FormEvent } from 'react'

interface RecoveryCardProps {
  recoveryApiUrl: string
  onSwitchToLogin: () => void
}

type RecoveryStep = 'request' | 'reset'

export function RecoveryCard({ recoveryApiUrl, onSwitchToLogin }: RecoveryCardProps) {
  const [step, setStep] = useState<RecoveryStep>('request')
  const [email, setEmail] = useState('')
  const [token, setToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  async function handleRequestToken(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')
    setSuccessMessage('')

    const trimmedEmail = email.trim()
    if (!trimmedEmail) {
      setErrorMessage('Por favor, informe seu e-mail.')
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch(`${recoveryApiUrl}/recovery/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: trimmedEmail }),
      })

      const data = await response.json()

      if (!response.ok) {
        setErrorMessage(data.detail || 'Não foi possível solicitar a recuperação. Verifique os dados.')
        return
      }

      setSuccessMessage('Solicitação enviada! Copie o token de validação abaixo para redefinir a senha.')
      if (data.reset_token) {
        setToken(data.reset_token)
      }
      setStep('reset')
    } catch {
      setErrorMessage('Não foi possível conectar ao Recovery Service. Verifique se o serviço está ativo.')
    } finally {
      setIsLoading(false)
    }
  }

  async function handleResetPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')
    setSuccessMessage('')

    const trimmedToken = token.trim()
    if (!trimmedToken) {
      setErrorMessage('Por favor, informe o token de recuperação.')
      return
    }

    if (newPassword.length < 8) {
      setErrorMessage('A nova senha deve ter no mínimo 8 caracteres.')
      return
    }

    if (newPassword !== confirmPassword) {
      setErrorMessage('As senhas digitadas não conferem.')
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch(`${recoveryApiUrl}/recovery/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: trimmedToken,
          new_password: newPassword,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        setErrorMessage(data.detail || 'Falha ao redefinir a senha. O token pode estar expirado ou incorreto.')
        return
      }

      setSuccessMessage('Sua senha foi redefinida com sucesso! Redirecionando para o login...')
      setTimeout(() => {
        onSwitchToLogin()
      }, 1800)
    } catch {
      setErrorMessage('Não foi possível conectar ao Recovery Service. Verifique se o serviço está ativo.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="login-card" aria-label="Recuperação de senha">
      <div className="login-card-icon" aria-hidden="true">🔑</div>
      <span className="login-card-eyebrow">RECUPERAÇÃO DE CONTA</span>
      <h2>Recuperar Senha</h2>
      <p className="login-card-description">
        {step === 'request'
          ? 'Informe o e-mail cadastrado para gerar seu código de redefinição.'
          : 'Insira o token recebido e escolha sua nova senha de acesso.'}
      </p>

      {errorMessage && (
        <div className="auth-alert auth-alert-error" role="alert">
          <span>⚠️</span> {errorMessage}
        </div>
      )}

      {successMessage && (
        <div className="auth-alert auth-alert-success" role="status">
          <span>✅</span> {successMessage}
        </div>
      )}

      {step === 'request' ? (
        <form className="login-form" onSubmit={handleRequestToken}>
          <label htmlFor="rec-email">E-mail da sua conta</label>
          <input
            id="rec-email"
            name="email"
            type="email"
            autoComplete="email"
            placeholder="seuemail@exemplo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <button className="login-button" type="submit" disabled={isLoading}>
            <span>{isLoading ? 'Solicitando...' : 'Enviar Código de Recuperação'}</span>
            {!isLoading && <span aria-hidden="true">→</span>}
          </button>
        </form>
      ) : (
        <form className="login-form" onSubmit={handleResetPassword}>
          <label htmlFor="rec-token">Token de Recuperação</label>
          <input
            id="rec-token"
            name="token"
            type="text"
            placeholder="Cole o token de recuperação"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            required
          />

          <div className="password-label-row">
            <label htmlFor="rec-new-password">Nova Senha (mín. 8 caracteres)</label>
          </div>
          <div className="password-input-wrap">
            <input
              id="rec-new-password"
              name="newPassword"
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              placeholder="Digite a nova senha"
              minLength={8}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
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

          <label htmlFor="rec-confirm-password">Confirmar Nova Senha</label>
          <input
            id="rec-confirm-password"
            name="confirmPassword"
            type={showPassword ? 'text' : 'password'}
            autoComplete="new-password"
            placeholder="Repita a nova senha"
            minLength={8}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          <button className="login-button" type="submit" disabled={isLoading}>
            <span>{isLoading ? 'Redefinindo...' : 'Atualizar Minha Senha'}</span>
            {!isLoading && <span aria-hidden="true">✓</span>}
          </button>
        </form>
      )}

      <div className="auth-footer-links">
        {step === 'reset' && (
          <button
            className="link-button"
            type="button"
            onClick={() => {
              setStep('request')
              setErrorMessage('')
              setSuccessMessage('')
            }}
          >
            ← Pedir outro código
          </button>
        )}
        <button
          className="link-button"
          type="button"
          onClick={onSwitchToLogin}
        >
          Lembrou a senha? Voltar ao login
        </button>
      </div>
    </section>
  )
}

