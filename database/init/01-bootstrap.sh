#!/bin/bash
set -e

psql \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=user_service_db_password="$USER_SERVICE_DB_PASSWORD" \
  --set=game_service_db_password="$GAME_SERVICE_DB_PASSWORD" \
  --set=rank_service_db_password="$RANK_SERVICE_DB_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE user_service LOGIN PASSWORD %L', :'user_service_db_password') \gexec
SELECT format('CREATE DATABASE user_service OWNER user_service') \gexec
REVOKE ALL ON DATABASE user_service FROM PUBLIC;

SELECT format('CREATE ROLE game_service LOGIN PASSWORD %L', :'game_service_db_password') \gexec
SELECT format('CREATE DATABASE game_service OWNER game_service') \gexec
REVOKE ALL ON DATABASE game_service FROM PUBLIC;

SELECT format('CREATE ROLE rank_service LOGIN PASSWORD %L', :'rank_service_db_password') \gexec
SELECT format('CREATE DATABASE rank_service OWNER rank_service') \gexec
REVOKE ALL ON DATABASE rank_service FROM PUBLIC;
SQL

psql --username "$POSTGRES_USER" --dbname user_service --file /database/schemas/user-service.sql
psql --username "$POSTGRES_USER" --dbname game_service --file /database/schemas/game-service.sql
psql --username "$POSTGRES_USER" --dbname rank_service --file /database/schemas/rank-service.sql
