# 🎮 Plataforma de Jogos Web (Microsserviços)

Sistema web para gerenciamento e execução de jogos simples em HTML5 Canvas, desenvolvido como projeto para a disciplina de **Desenvolvimento de Sistemas Web II**.

A aplicação adota uma arquitetura de **microsserviços**, com rotas centralizadas por um API Gateway (em planejamento), frontend em React e persistência de dados isolada por domínio.

## Tecnologias

- Frontend: React 19, TypeScript e Vite.
- Banco de dados: PostgreSQL 17.
- Backend:
  - User Service em FastAPI (autenticação JWT e usuários).
  - Rank Service em FastAPI (classificação, pontuações e leaderboard).
  - Recovery Service em FastAPI (recuperação e redefinição de senhas).
- Orquestração local: Docker Compose.

## Arquitetura e estado atual

O objetivo é ter microsserviços autônomos, cada um responsável pelo seu domínio. O PostgreSQL é compartilhado como servidor físico, mas cada serviço tem um banco e um usuário próprios. Não há chaves estrangeiras entre bancos de serviços distintos: referências a usuários e partidas em outros serviços são identificadores UUID validados pelas APIs.

```text
Frontend → API Gateway → User Service     → banco user_service
                       → Game Service     → banco game_service
                       → Rank Service     → banco rank_service
                       → Recovery Service → integra com User Service
```

O Docker Compose inicia o frontend, o PostgreSQL, o User Service, o Rank Service e o Recovery Service. O Node.js é usado dentro da imagem Docker para compilar o frontend; não é necessário instalá-lo para executar a aplicação com Compose.

O frontend autentica usuários pelo User Service, permite cadastro de novos usuários, recuperação de senha com tokens de segurança, exibe um **Rank Básico** na tela inicial de jogos e uma tela completa de **Leaderboard Detalhado** (com métricas, filtros por jogo, busca e tempos de conclusão).

## Executar localmente com Docker Compose

### 1. Pré-requisitos

- Git, caso ainda não tenha uma cópia do repositório.
- Docker Desktop instalado e em execução, com Docker Compose v2.

### 2. Obter o projeto

Se ainda não tiver o repositório, clone-o e entre na pasta:

```sh
git clone https://github.com/Thaynan-passos/jogos-web-microsservicos.git
cd jogos-web-microsservicos
```

### 3. Criar e configurar o arquivo de ambiente

Na raiz do projeto, crie o arquivo `.env` a partir do exemplo.

No PowerShell:

```powershell
Copy-Item .env.example .env
```

No macOS/Linux:

```sh
cp .env.example .env
```

Abra `.env` e substitua `SECRET_KEY=replace-with-a-random-32-byte-secret` por uma chave aleatória. Os valores de senha do exemplo servem apenas para desenvolvimento local; use senhas fortes e exclusivas fora desse ambiente. Não compartilhe nem versione o arquivo `.env`.

As portas padrão são:
- Frontend: `5173`
- User Service: `8001`
- Rank Service: `8003`
- Recovery Service: `8004`
- PostgreSQL: `5432`

### 4. Construir e iniciar os serviços

Na raiz do repositório, execute:

```sh
docker compose up --build -d
```

Na primeira execução, o Docker baixa as imagens e constrói os serviços. Aguarde até que os contêineres estejam iniciados e verifique o estado:

```sh
docker compose ps
```

### 5. Acessar e verificar

- **Frontend**: [http://localhost:5173](http://localhost:5173)
  - Tela de Login, Cadastro de novos usuários e Recuperação de senha.
  - Tela principal com Jogos e **Rank Básico**.
  - Aba **Leaderboard**: Ranking complexo com filtros, estatísticas e busca.
- **User Service**:
  - Documentação interativa: [http://localhost:8001/docs](http://localhost:8001/docs)
  - Verificação de saúde: [http://localhost:8001/health](http://localhost:8001/health)
- **Rank Service**:
  - Documentação interativa: [http://localhost:8003/docs](http://localhost:8003/docs)
  - Verificação de saúde: [http://localhost:8003/health](http://localhost:8003/health)
- **Recovery Service**:
  - Documentação interativa: [http://localhost:8004/docs](http://localhost:8004/docs)
  - Verificação de saúde: [http://localhost:8004/health](http://localhost:8004/health)

O PostgreSQL, por padrão, fica disponível apenas localmente em `127.0.0.1:5432`.

### 6. Consultar logs

Para acompanhar os logs de todos os serviços:

```sh
docker compose logs -f
```

Para consultar apenas um serviço, informe seu nome, por exemplo:

```sh
docker compose logs -f recovery-service
```

Pressione `Ctrl+C` para encerrar a visualização dos logs; isso não encerra os contêineres.

### 7. Parar os serviços

Para parar e remover os contêineres e a rede, preservando os dados do banco:

```sh
docker compose down
```

Para iniciar novamente depois, use `docker compose up -d`.

> **Atenção:** `docker compose down -v` também remove o volume do PostgreSQL e apaga todos os dados locais. Os scripts de `database/init/` são executados somente quando esse volume é criado pela primeira vez; editar esses scripts não altera um banco já existente.

## Banco de dados

Os bancos `user_service`, `game_service` e `rank_service` são criados com usuários e senhas individuais. O User Service usa `user_service` e aplica suas migrações Alembic ao iniciar. Os esquemas iniciais do catálogo de jogos e do ranking estão em `database/schemas/`.
