#!/bin/bash

# Строгий режим Bash
set -euo pipefail

# Путь к пользовательскому паролю
SECRET_FILE="/run/secrets/psql_app_user_pass"

if [[ ! -f "$SECRET_FILE" ]]; then
  echo "ERROR: Secret file not found at $SECRET_FILE" >&2
  exit 1
fi

# Считываем пароль
APP_USER_PASSWORD=$(cat "$SECRET_FILE" | tr -d '\r\n')

# Проводим инициализацию БД
psql -v ON_ERROR_STOP=1 --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" <<EOF
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'wms_app_user') THEN
    CREATE USER wms_app_user WITH PASSWORD '$APP_USER_PASSWORD';
  END IF;
END \$\$;

CREATE DATABASE management_system ENCODING UTF8;

\c management_system admin_db

CREATE SCHEMA IF NOT EXISTS app_schema AUTHORIZATION admin_db;
GRANT USAGE ON SCHEMA app_schema TO wms_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA app_schema
GRANT USAGE, SELECT ON SEQUENCES TO wms_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA app_schema
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO wms_app_user;

CREATE EXTENSION pgcrypto;
CREATE EXTENSION "uuid-ossp";

CREATE TYPE status_inbound_invoices AS ENUM('draft', 'posted', 'cancelled');
CREATE TYPE action_type_log AS ENUM('create', 'update', 'annull');
CREATE TYPE user_role AS ENUM('manager', 'storekeeper', 'picker');
EOF

echo "Database initialization complete for user wms_app_user."