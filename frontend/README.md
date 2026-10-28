# Frontend

Interface do Playground em React, TypeScript e Vite. A tela inicial solicita
login ao User Service; após a autenticação, o usuário pode acessar os jogos
locais: Jogo da Velha, Jogo da Memória e Pedra, Papel e Tesoura.

## Executar em desenvolvimento

Com o User Service iniciado, instale as dependências e execute o Vite:

```sh
npm ci
npm run dev
```

Por padrão, o frontend chama `http://localhost:8001/api/v1/auth/login`.
Para usar outra URL base da API, defina `VITE_API_BASE_URL` no ambiente do
Vite, por exemplo `http://localhost:8001/api/v1`.

O token de acesso é mantido em `sessionStorage` durante a sessão da aba. O
frontend não persiste partidas ou pontuações nos serviços.

## Verificações

```sh
npm run build
npm run lint
```
