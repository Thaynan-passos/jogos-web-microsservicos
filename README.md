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

### Dependências entre os microsserviços

Cada serviço mantém seu próprio banco (`user_service`, `game_service` e `rank_service`) e credenciais próprias no servidor PostgreSQL compartilhado. Não há chaves estrangeiras entre esses bancos. Os identificadores de usuários e jogos usados fora do serviço de origem são valores UUID ou slugs; a existência do registro referenciado não é garantida por uma restrição de banco entre serviços.

```text
Frontend → User Service       (cadastro, login e identidade)
Frontend → Game Service       (catálogo e sessões; armazena user_id e game_slug)
Frontend → Rank Service       (pontuações e leaderboard; armazena user_id e game_slug)
Frontend → Recovery Service  (solicita e valida token de recuperação)
Recovery Service → User Service (redefine a senha pelo endpoint interno)

User Service  → PostgreSQL / user_service
Game Service  → PostgreSQL / game_service
Rank Service  → PostgreSQL / rank_service
```

- **User Service** é a fonte dos usuários e emite os tokens JWT. Game e Rank recebem identificadores de usuário nos dados das requisições; não consultam diretamente o banco de usuários para validá-los.
- **Game Service** é dono do catálogo e das sessões. Uma sessão guarda o slug do jogo e, opcionalmente, o UUID do usuário. A referência do jogo é validada dentro do próprio banco do Game Service; a de usuário não tem validação cruzada.
- **Rank Service** é dono das pontuações. Guarda UUID do usuário, nome de usuário e slug do jogo como dados locais, sem chave estrangeira para User ou Game. Assim, alterações ou remoções nesses serviços não se propagam automaticamente para o ranking.
- **Recovery Service** não tem banco próprio. Gera e verifica tokens de recuperação; para redefinir a senha, chama `POST /api/v1/auth/reset-password-internal` no User Service. Se o User Service estiver indisponível, a redefinição não pode ser concluída.
- **Dependência operacional no Compose:** Recovery Service aguarda o User Service ficar saudável. O API Gateway aguarda os quatro serviços, e o frontend aguarda o Gateway. Portanto, no Compose atual, a indisponibilidade do Recovery também impede que o Gateway e o frontend sejam considerados prontos, embora Game e Rank não dependam funcionalmente dele.

Game e Rank não têm chamadas diretas entre si nem para User no fluxo implementado: o frontend coordena as chamadas às APIs. Isso mantém os bancos isolados, mas significa que a consistência de nomes e identificadores enviados entre serviços depende dos contratos usados pelo cliente.

## Executar localmente com Docker Compose

Para preparar o uso do AWS Secrets Manager em tarefas Amazon ECS/Fargate, consulte [Implantação AWS](docs/implantacao-aws.md). A execução local continua usando o arquivo `.env`.

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

Preencha no `.env` as senhas e as chaves que estão em branco. Gere valores aleatórios e diferentes para cada senha, `JWT_SECRET_KEY`, `RECOVERY_TOKEN_SECRET_KEY` e `RECOVERY_SERVICE_SECRET`; por exemplo, execute `python -c "import secrets; print(secrets.token_urlsafe(32))"` várias vezes e copie cada resultado para uma variável distinta. As chaves JWT, de recuperação e de comunicação entre serviços são separadas. Não compartilhe nem versione o arquivo `.env`.

As portas padrão são:
- Frontend: `5173`
- API Gateway: `8080`
- PostgreSQL: `5432`

Os microsserviços e o banco ficam em uma rede Docker interna, sem portas
publicadas. Frontend e API Gateway são vinculados somente ao loopback do host;
as APIs são acessadas pelo Gateway em `http://localhost:8080`.

### 4. Construir e iniciar os serviços

Na raiz do repositório, execute:

```sh
docker compose up --build -d
```

Na primeira execução, o Docker baixa as imagens e constrói os serviços. Aguarde até que os contêineres estejam iniciados e verifique o estado:

```sh
docker compose ps
```

O serviço não cria um gerente automaticamente. Para cadastrar o primeiro, execute o comando interativo abaixo; informe o usuário, e-mail e uma senha exclusiva quando solicitado:

```sh
docker compose exec -it user-service python -m app.cli create-admin
```

O comando só funciona enquanto não existir nenhuma conta gerente e exige um terminal interativo. Novos gerentes podem ser cadastrados por uma conta gerente no painel.

As pontuações de demonstração são opcionais e ficam marcadas como demonstração, sem aparecer no ranking real. Para carregá-las em desenvolvimento local, defina `SEED_DEMO_DATA=true` no `.env`; em ambientes diferentes de `development`, elas não são carregadas.

### 5. Acessar e verificar

- **Frontend**: [http://localhost:5173](http://localhost:5173)
  - Tela de Login, Cadastro de novos usuários e Recuperação de senha.
  - Tela principal com Jogos e **Rank Básico**.
  - Aba **Leaderboard**: Ranking complexo com filtros, estatísticas e busca.
- **Aba Gerência**: permite criar, consultar, editar e remover usuários, jogos, sessões e rankings. Gerentes também podem conceder ou remover o papel de gerente, mantendo pelo menos um gerente ativo. A migração remove a antiga conta de demonstração; contas reais são criadas sem privilégios, exceto quando um gerente explicitamente lhes concede o papel.

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
