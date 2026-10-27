# 🎮 Plataforma de Jogos Web (Microsserviços)

Sistema web completo para gerenciamento e execução de jogos simples em HTML5 Canvas, desenvolvido como projeto para a disciplina de **Desenvolvimento de Sistemas Web II**.

A aplicação adota a arquitetura de **Microsserviços**, com rotas centralizadas por um **API Gateway**, frontend reativo em **React** e persistência de dados isolada para cada domínio.

---

## Tecnologias

- Frontend: React, TypeScript e Vite.
- Persistência: PostgreSQL 17 e Docker Compose.
- Backend: User Service em FastAPI; Game Service, Rank Service e API Gateway ainda em desenvolvimento.

## 🏛️ Arquitetura do Sistema

O objetivo é ter três microsserviços, cada um responsável pelo seu banco de dados. O PostgreSQL é compartilhado como servidor, mas cada serviço tem um banco e um usuário próprios. Não há chaves estrangeiras entre bancos: referências a usuários e partidas em outros serviços são identificadores UUID validados pelas APIs.

```text
Frontend → API Gateway → User Service → banco user_service
                       → Game Service → banco game_service
                       → Rank Service → banco rank_service
```

O Docker Compose inicia o frontend, o PostgreSQL e o User Service. Node.js é usado dentro da imagem Docker para compilar o frontend; não é necessário instalá-lo na máquina. Game Service, Rank Service e API Gateway ainda não têm APIs implementadas; o frontend atual executa os jogos localmente e não salva partidas ou pontuações nos serviços.

## Banco de dados local

1. Instale o Docker Desktop e inicie o Docker.
2. Copie `.env.example` para `.env`. Os valores do exemplo são apenas para desenvolvimento local; use senhas fortes em outros ambientes.
3. Na raiz do repositório, execute:

   ```sh
   docker compose up --build -d
   ```

O frontend fica disponível em `http://localhost:5173` (ou na porta definida por `FRONTEND_PORT`), e a API do User Service em `http://localhost:8001`, com documentação interativa em `http://localhost:8001/docs`. O PostgreSQL escuta apenas em `127.0.0.1:5432` por padrão. Os bancos `user_service`, `game_service` e `rank_service` são criados com usuários e senhas individuais. O User Service usa o banco `user_service`; ferramentas executadas na máquina podem usar `localhost` e a porta definida em `POSTGRES_PORT`.

Os esquemas iniciais do catálogo de jogos e do ranking estão em `database/schemas/`. O banco de usuários é atualizado pelas migrações Alembic do User Service. O catálogo começa com os três jogos do frontend. `user_id` e `session_id` no banco de ranking não têm chaves estrangeiras, pois os dados pertencem a bancos de outros serviços.

Os scripts em `database/init/` são executados somente quando o volume do PostgreSQL é criado pela primeira vez. Alterações futuras devem ser aplicadas como migrações versionadas; editar os scripts de inicialização não atualiza um volume existente. O User Service aplica suas migrações Alembic ao iniciar. `docker compose down` preserva os dados. **`docker compose down -v` apaga os bancos e todos os dados locais.**
