#!/usr/bin/env sh
set -e

# Initialize DB (idempotent)
flask --app wsgi.py init-db || true

exec "$@"

