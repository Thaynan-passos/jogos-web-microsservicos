# Integração com AWS Secrets Manager

O código dos serviços já lê credenciais e chaves de variáveis de ambiente. Em AWS, a integração recomendada para este projeto é o ECS injetar os valores do Secrets Manager nos contêineres na inicialização da task. Isso evita adicionar credenciais AWS ao código ou às imagens e dispensa um cliente AWS dentro das aplicações.

Esta configuração é um modelo para **Amazon ECS com AWS Fargate**. O Docker Compose continua sendo o fluxo local; ele usa o `.env` e não consulta a AWS.

## Criar conjuntos separados por ambiente

O template [secrets-manager.yaml](../deploy/aws/secrets-manager.yaml) cria seis segredos independentes para um ambiente: senha de administrador do PostgreSQL, senhas de banco dos serviços User, Game e Rank, chave de assinatura JWT e chave de assinatura dos tokens de recuperação. Cada valor é gerado aleatoriamente pelo Secrets Manager; o template não contém valores secretos. Recursos usam `DeletionPolicy: Retain` para evitar apagar os segredos junto com a stack.

Crie uma stack para cada ambiente, na conta e região AWS desejadas:

```sh
aws cloudformation deploy \
  --template-file deploy/aws/secrets-manager.yaml \
  --stack-name jogos-dev-secrets \
  --parameter-overrides Environment=dev

aws cloudformation deploy \
  --template-file deploy/aws/secrets-manager.yaml \
  --stack-name jogos-homologacao-secrets \
  --parameter-overrides Environment=homologacao

aws cloudformation deploy \
  --template-file deploy/aws/secrets-manager.yaml \
  --stack-name jogos-prod-secrets \
  --parameter-overrides Environment=prod
```

Configure a região padrão da AWS CLI ou acrescente `--region <regiao>` em cada comando. Cada execução cria nomes distintos sob `jogos/dev/`, `jogos/homologacao/` ou `jogos/prod/`; todos os valores também são gerados separadamente. Consulte os ARNs retornados pelas saídas das stacks para configurar as tasks. A stack apenas cria os segredos: ela não implanta serviços nem altera bancos.

| Nome sugerido | Variável ECS | Consumidor |
|---|---|---|
| `jogos/<ambiente>/postgres/admin-password` | `POSTGRES_PASSWORD` | PostgreSQL de desenvolvimento; em produção, prefira RDS. |
| `jogos/<ambiente>/user-service/database-password` | `POSTGRES_PASSWORD` | User Service |
| `jogos/<ambiente>/user-service/jwt-signing-key` | `JWT_SECRET_KEY` | User Service |
| `jogos/<ambiente>/game-service/database-password` | `POSTGRES_PASSWORD` | Game Service |
| `jogos/<ambiente>/rank-service/database-password` | `POSTGRES_PASSWORD` | Rank Service |
| `jogos/<ambiente>/recovery-service/token-signing-key` | `RECOVERY_TOKEN_SECRET_KEY` | Recovery Service |

Os segredos separados por serviço permitem restringir a task execution role aos ARNs necessários para cada serviço. A chave `ALGORITHM` e os tempos de expiração não são segredos e podem continuar como variáveis comuns da definição da task.

## Definição da task

Na definição ECS de cada contêiner, mantenha configurações não sensíveis em `environment` e referencie cada valor sensível em `secrets`. Exemplo do contêiner User Service:

```json
{
  "name": "user-service",
  "environment": [
    { "name": "POSTGRES_USER", "value": "user_service" },
    { "name": "POSTGRES_DB", "value": "user_service" },
    { "name": "POSTGRES_SERVER", "value": "<hostname-do-banco>" },
    { "name": "POSTGRES_PORT", "value": "5432" },
    { "name": "ALGORITHM", "value": "HS256" },
    { "name": "ACCESS_TOKEN_EXPIRE_MINUTES", "value": "30" }
  ],
  "secrets": [
    {
      "name": "POSTGRES_PASSWORD",
      "valueFrom": "<ARN da saída UserDatabasePasswordArn>"
    },
    {
      "name": "JWT_SECRET_KEY",
      "valueFrom": "<ARN da saída UserJwtSigningKeyArn>"
    }
  ]
}
```

Use o mesmo padrão para os outros contêineres:

- Game Service: injete `POSTGRES_PASSWORD` usando a saída `GameDatabasePasswordArn`.
- Rank Service: injete `POSTGRES_PASSWORD` usando a saída `RankDatabasePasswordArn`.
- Recovery Service: injete `RECOVERY_TOKEN_SECRET_KEY` usando `RecoveryTokenSigningKeyArn` e configure `USER_SERVICE_URL` com o endereço interno do User Service.
- PostgreSQL local em ECS: injete `POSTGRES_PASSWORD` usando `PostgresAdminPasswordArn`. Para produção, prefira um PostgreSQL gerenciado (por exemplo, Amazon RDS) e não rode o contêiner de banco do Compose como banco de produção.

Como cada segredo contém um único valor string, use diretamente o ARN retornado pelo CloudFormation, sem sufixo de chave JSON. O Fargate precisa de plataforma `1.3.0` ou posterior para injetar o valor completo do segredo.

## Permissões IAM

Atribua à task uma **task execution role** com `secretsmanager:GetSecretValue` apenas nos ARNs dos segredos referenciados pela definição. A role também precisa das permissões usuais de execução, como pull de imagens do ECR e envio de logs ao CloudWatch, conforme o ambiente.

Exemplo de política adicional para a task execution role do User Service, restrita aos dois segredos usados por essa task:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": [
        "<ARN do segredo user-service database-password>",
        "<ARN do segredo user-service jwt-signing-key>"
      ]
    }
  ]
}
```

Crie uma política por task/service, removendo os ARNs que não forem necessários; a task do Recovery, por exemplo, recebe apenas `RecoveryTokenSigningKeyArn`. Se os segredos usarem uma chave KMS gerenciada pelo cliente, conceda também `kms:Decrypt` para essa chave à execution role. Não coloque access keys da AWS nas variáveis do contêiner; use as roles do ECS.

## Atualização e rotação

O ECS injeta o valor quando inicia a task. Alterar ou rotacionar um segredo não atualiza contêineres em execução; publique uma nova revisão ou force uma nova implantação do serviço para as tasks lerem `AWSCURRENT`. Planeje a rotação junto com a atualização dos serviços e do banco, pois trocar chaves JWT invalida tokens de acesso existentes e trocar a chave de recuperação invalida tokens de recuperação emitidos anteriormente.

Evite imprimir variáveis de ambiente em logs ou incluí-las em saídas de diagnóstico. Para tasks em sub-redes privadas sem saída pública, configure conectividade privada com Secrets Manager por meio de um interface VPC endpoint.

## Referências AWS

- [Injetar segredos do Secrets Manager como variáveis de ambiente em ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-secrets-manager.html)
- [IAM task execution role do ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html)
