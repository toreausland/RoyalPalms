#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

# Opprett mapper (lokalt fallback)
mkdir -p instance uploads

# Persistent disk (Render produksjon)
if [ -d "/var/data" ]; then
    mkdir -p /var/data/uploads
    echo "Persistent disk klar: /var/data"
fi

# Seed databasen (kun første gang / hvis tom)
python seed.py
