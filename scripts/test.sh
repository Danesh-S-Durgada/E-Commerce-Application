#!/usr/bin/env bash
set -e
docker compose up -d mysql
python -m pytest backend/tests -q
