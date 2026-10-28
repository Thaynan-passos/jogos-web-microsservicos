# 🎮 Plataforma de Jogos Web (Microsserviços)

Sistema web para gerenciamento e execução de jogos simples em HTML5 Canvas, desenvolvido como projeto para a disciplina de **Desenvolvimento de Sistemas Web II**.

A aplicação adota uma arquitetura de **microsserviços**, com rotas centralizadas por um API Gateway (ainda em desenvolvimento), frontend em React e persistência de dados isolada por domínio.

## Tecnologias

- Frontend: React, TypeScript e Vite.
- Banco de dados: PostgreSQL 17.
- Backend: User Service em FastAPI; Rank Service com esqueleto FastAPI.
- Orquestração local: Docker Compose.

## Arquitetura e estado atual

O objetivo é ter três microsserviços, cada um responsável pelo seu banco de dados. O PostgreSQL é compartilhado como servidor, mas cada serviço tem um banco e um usuário próprios. Não há chaves estrangeiras entre bancos: referências a usuários e partidas em outros serviços são identificadores UUID validados pelas APIs.

```text
Frontend → API Gateway → User Service → banco user_service
                       → Game Service → banco game_service
                       → Rank Service → banco rank_service
```

O Docker Compose inicia o frontend, o PostgreSQL, o User Service e o esqueleto do Rank Service. O Node.js é usado dentro da imagem Docker para compilar o frontend; não é necessário instalá-lo para executar a aplicação com Compose.

O frontend autentica usuários pelo User Service e executa os jogos localmente; partidas e pontuações ainda não são salvas nos serviços. O Rank Service expõe `/health` e `GET /api/v1/rankings`, que responde HTTP 501 até sua implementação. O Game Service e o API Gateway ainda estão em desenvolvimento.

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

As portas padrão são frontend `5173`, User Service `8001`, Rank Service `8003` e PostgreSQL `5432`. Se alguma já estiver ocupada, altere a variável correspondente no `.env`.

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

- Frontend: [http://localhost:5173](http://localhost:5173)
- Login do frontend: usa `POST /api/v1/auth/login` no User Service, disponível em `http://localhost:8001` por padrão. Em desenvolvimento, configure `VITE_API_BASE_URL` se a API estiver em outro endereço.
- User Service — documentação interativa: [http://localhost:8001/docs](http://localhost:8001/docs)
- User Service — verificação de saúde: [http://localhost:8001/health](http://localhost:8001/health)
- Rank Service — documentação interativa: [http://localhost:8003/docs](http://localhost:8003/docs)
- Rank Service — verificação de saúde: [http://localhost:8003/health](http://localhost:8003/health)

As portas podem ser diferentes se você as alterou no `.env`. O PostgreSQL, por padrão, fica disponível apenas localmente em `127.0.0.1:5432`.

### 6. Consultar logs

Para acompanhar os logs de todos os serviços:

```sh
docker compose logs -f
```

Para consultar apenas um serviço, informe seu nome, por exemplo:

```sh
docker compose logs -f user-service
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

Os bancos `user_service`, `game_service` e `rank_service` são criados com usuários e senhas individuais. O User Service usa `user_service` e aplica suas migrações Alembic ao iniciar. Os esquemas iniciais do catálogo de jogos e do ranking estão em `database/schemas/`; o catálogo começa com os três jogos do frontend. O esqueleto atual do Rank Service ainda não se conecta ao banco.

## Desenvolvimento do frontend sem contêiner

Esse modo requer Node.js e npm instalados. Mantenha os serviços de backend e o banco iniciados com Docker Compose e pare o frontend em contêiner para liberar a porta:

```sh
docker compose up -d postgres user-service rank-service
docker compose stop frontend
cd frontend
npm ci
npm run dev
```

O Vite informa no terminal o endereço local do frontend. Para voltar a usar o frontend em contêiner, encerre o Vite com `Ctrl+C` e execute, na raiz do projeto:

```sh
docker compose start frontend
```
