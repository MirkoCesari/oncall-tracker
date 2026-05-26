#!/bin/bash
set -e

mkdir -p data/postgres data/app
chmod 777 data/postgres data/app

echo "Done: docker compose up -d --build"
