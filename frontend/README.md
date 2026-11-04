# Frontend

Interface do Playground em React, TypeScript e Vite. A tela inicial solicita
login ao User Service; após a autenticação, o usuário pode acessar os jogos
locais: Jogo da Velha, Jogo da Memória e Pedra, Papel e Tesoura. As partidas
são registradas no Game Service e as pontuações no Rank Service.

## Executar em desenvolvimento

Para executar somente o frontend em desenvolvimento, instale as dependências e
execute o Vite:

```sh
npm ci
npm run dev
```

Ao executar com Docker Compose, o frontend usa o API Gateway através das rotas
`/api/user`, `/api/game`, `/api/rank` e `/api/recovery`. Em desenvolvimento
fora do Compose, configure as URLs com `VITE_API_BASE_URL`,
`VITE_GAME_API_URL`, `VITE_RANK_API_URL` e `VITE_RECOVERY_API_URL`, apontando
para as respectivas APIs.

O token de acesso é mantido em `sessionStorage` durante a sessão da aba. As
partidas são persistidas como sessões no Game Service e as pontuações são
persistidas no Rank Service.

## Verificações

```sh
npm run build
npm run lint
```
