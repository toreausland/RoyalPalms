#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

# Opprett mapper
mkdir -p instance uploads

# Seed databasen (kun første gang / hvis tom)
python seed.py
