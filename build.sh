#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

# Opprett mapper (lokalt fallback)
mkdir -p instance uploads

# NB: seed.py kjøres i startCommand (runtime), IKKE her.
# Persistent disk (/var/data) er read-only under build-fasen på Render.
