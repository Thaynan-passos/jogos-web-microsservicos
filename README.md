# 🎮 Plataforma de Jogos Web (Microsserviços)

Sistema web completo para gerenciamento e execução de jogos simples em HTML5 Canvas, desenvolvido como projeto para a disciplina de **Desenvolvimento de Sistemas Web II**.

A aplicação adota a arquitetura de **Microsserviços**, com rotas centralizadas por um **API Gateway**, frontend reativo em **React** e persistência de dados isolada para cada domínio.

---

## 🛠️ Tecnologias Utilizadas

### **Frontend**

- **React.js** (TypeScript)
- **HTML5 Canvas API / CSS3** (para renderização dos jogos 2D)
- **Axios** (comunicação HTTP com o Gateway)

### **Backend & Arquitetura**

- **Node.js** com **Express** (TypeScript)
- **API Gateway** (Express / Roteamento de microsserviços)
- **Docker & Docker Compose** (orquestração de containers e bancos de dados)

### **Bancos de Dados & Persistência**

- **PostgreSQL** (Persistência relacional para usuários e suporte)
- **MongoDB** (Persistência NoSQL para metadados e configurações dos jogos)
- **Redis** (Armazenamento em memória para dados de acesso rápido e ranking)

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
