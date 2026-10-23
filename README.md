# 🎮 Plataforma de Jogos Web (Microsserviços)

Sistema web completo para gerenciamento e execução de jogos simples em HTML5 Canvas, desenvolvido como projeto para a disciplina de **Desenvolvimento de Sistemas Web II**.

A aplicação adota a arquitetura de **Microsserviços**, com rotas centralizadas por um **API Gateway**, frontend reativo em **React** e persistência de dados isolada para cada domínio.

---

## 🛠️ Tecnologias Utilizadas

### **Frontend**

- **React 19** com **TypeScript**
- **Vite** (servidor de desenvolvimento e build)
- **React Router** (roteamento da aplicacao)
- **HTML5 Canvas API / CSS3** (para renderização dos jogos 2D)
- **Axios** (comunicação HTTP com o Gateway)
- **oxlint** (linting)

### **Backend & Arquitetura**

- **Python** com **FastAPI**
- **Uvicorn**
- **API Gateway** (ponto de entrada para o roteamento dos microsserviços)
- **Arquitetura de microsserviços** (serviços de usuários, jogos, ranking e suporte)

### **Bancos de Dados & Persistência**

- **PostgreSQL 16** (persistência relacional dos usuários)
- **SQLAlchemy** com suporte assíncrono via **asyncpg** (acesso ao banco)
- **Alembic** (migrações do banco de dados)

### **Autenticação e Configuração**

- **JWT** com `python-jose` (autenticação baseada em tokens)
- **bcrypt (>= 4.0.0)** (hash e verificação nativa de senhas)
- **Pydantic v2** e **pydantic-settings** (validação estrita de dados e carregamento de configurações a partir do `.env`)

### **Infraestrutura e Ferramentas**

- **Docker** e **Docker Compose** (containerização e execução local)
- **npm** (gerenciamento das dependências do frontend)
- **pip** (gerenciamento das dependências do backend)
---

## 🏛️ Arquitetura do Sistema

O sistema é dividido em **4 microsserviços distintos**, um **API Gateway** e uma aplicação **Frontend**:

```text
                 +-----------------------+
                 |    Frontend (React)   |
                 +-----------+-----------+
                             |
                             v
                 +-----------------------+
                 |      API Gateway      |
                 +-----------+-----------+
                             |
     +-----------------------+--------------------+--------------------+
     |                       |                    |                    |
     v                       v                    v                    v
+--------+               +---------+         +---------+       +--------+
| User   |               | Game    |         | Rank    |       |Support |
|Service |               | Service |         | Service |       |Service |
+----+---+               +----+----+         +-----+---+       +---+----+
```

## 🚀 Execução Local

### 📋 Pré-requisitos

* **Linux:** [Docker Engine](https://docs.docker.com/engine/install/) e plugin [Docker Compose](https://docs.docker.com/compose/install/) instalados e ativos.
* **Windows:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e iniciado (com o backend WSL 2 recomendado).
* **Git** instalado.

---

### Executando com Docker Compose

O banco PostgreSQL e o `user-service` são iniciados em conjunto através do [compose.yaml](./compose.yaml).

#### 🐧 No Linux (Bash / Terminal)

1. **Clone o repositório e acesse a pasta:**
   ```bash
   git clone https://github.com/Thaynan-passos/jogos-web-microsservicos.git
   cd jogos-web-microsservicos
   ```

2. **Configure o arquivo de variáveis de ambiente:**
   ```bash
   cp .env.example .env
   ```

3. **Suba os containers com build:**
   ```bash
   docker compose up --build
   ```

4. **Para acompanhar os logs ou parar os serviços:**
   ```bash
   # Ver logs em tempo real do user-service:
   docker compose logs -f user-service

   # Parar todos os serviços:
   docker compose down
   ```

#### 🪟 No Windows (PowerShell / Windows Terminal)

1. **Abra o PowerShell na pasta raiz do repositório:**
   ```powershell
   cd caminho\ate\jogos-web-microsservicos
   ```

2. **Copie o arquivo de variáveis de ambiente:**
   ```powershell
   Copy-Item .env.example .env
   ```
   *(No Prompt de Comando / CMD clássico utilize `copy .env.example .env`)*

3. **Inicie os containers:**
   *(Certifique-se de que o Docker Desktop está aberto e em execução)*
   ```powershell
   docker compose up --build
   ```

4. **Para acompanhar os logs ou parar os serviços:**
   ```powershell
   # Ver logs em tempo real do user-service:
   docker compose logs -f user-service

   # Parar os serviços:
   docker compose down
   ```

### 🌐 Endpoints e Acessos Disponíveis

| Serviço / Recurso | URL Local | Descrição |
| :--- | :--- | :--- |
| **Frontend (Página Web)** | [http://localhost:8000](http://localhost:8000) | Aplicação web principal (React/Vite ou Gateway) |
| **User Service (Swagger UI)** | [http://localhost:8001/docs](http://localhost:8001/docs) | Teste interativo de todos os endpoints JSON |
| **User Service (Healthcheck)** | [http://localhost:8001/health](http://localhost:8001/health) | Verificação de status (`{"status":"ok"}`) |
| **PostgreSQL** | `localhost:5432` | Banco de dados relacional (`user_db`) |
