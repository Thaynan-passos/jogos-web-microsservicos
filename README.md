# 🎮 Plataforma de Jogos Web (Microsserviços)

Sistema web para gerenciamento e execução de jogos simples em HTML5 Canvas, desenvolvido como projeto para a disciplina de **Desenvolvimento de Sistemas Web II**.

A aplicação adota uma arquitetura de **microsserviços**, com rotas centralizadas por um API Gateway baseado em Nginx, frontend em React e persistência de dados isolada por domínio.

## Tecnologias

- Frontend: React 19, TypeScript e Vite.
- Banco de dados: PostgreSQL 17.
- Backend:
  - User Service em FastAPI (autenticação JWT e usuários).
  - Game Service em FastAPI (catálogo de jogos e sessões de jogo).
  - Rank Service em FastAPI (classificação, pontuações e leaderboard).
  - Recovery Service em FastAPI (recuperação e redefinição de senhas).
  - API Gateway em Nginx (roteamento das APIs para o frontend).
- Orquestração local: Docker Compose.

## Arquitetura e estado atual

O objetivo é ter microsserviços autônomos, cada um responsável pelo seu domínio. O PostgreSQL é compartilhado como servidor físico, mas cada serviço tem um banco e um usuário próprios. Não há chaves estrangeiras entre bancos de serviços distintos: referências a usuários e partidas em outros serviços são identificadores UUID validados pelas APIs.

```text
Frontend → API Gateway → User Service     → banco user_service
                       → Game Service     → banco game_service
                       → Rank Service     → banco rank_service
                       → Recovery Service → integra com User Service
```

O Docker Compose inicia o frontend, o API Gateway, o PostgreSQL e os quatro microsserviços. O Node.js é usado dentro da imagem Docker para compilar o frontend; não é necessário instalá-lo para executar a aplicação com Compose.

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
- API Gateway: `8080`
- PostgreSQL: `5432`

Os serviços internos não são publicados diretamente no host; suas APIs são
acessadas pelo API Gateway em `http://localhost:8080`.

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
- **Acesso de gerente para demonstrar o CRUD**:
  - Usuário: `Gerente`
  - E-mail: `Gerente@playground.com`
  - Senha: `Gerente@123`

  - Aba **Gerência**. Ela permite criar, consultar, editar e remover usuários, jogos, sessões e rankings.
  - Esse usuário é criado pela migração do User Service na primeira inicialização.

- **API Gateway**: [http://localhost:8080/health](http://localhost:8080/health)
- **User Service**:
  - Documentação interativa: [http://localhost:8080/api/user/docs](http://localhost:8080/api/user/docs)
- **Rank Service**:
  - Documentação interativa: [http://localhost:8080/api/rank/docs](http://localhost:8080/api/rank/docs)
- **Game Service**:
  - Documentação interativa: [http://localhost:8080/api/game/docs](http://localhost:8080/api/game/docs)
- **Recovery Service**:
  - Documentação interativa: [http://localhost:8080/api/recovery/docs](http://localhost:8080/api/recovery/docs)

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
