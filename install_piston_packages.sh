#!/bin/bash
# Script to install basic Piston runtimes
# Usage: ./install_piston_packages.sh [lang1] [lang2] ...
# HOST: set PISTON_HOST to override default http://localhost:2000

HOST=${PISTON_HOST:-"http://localhost:2000"}

if [ -z "$1" ]; then
    LANGS="python node javascript java go clike"
else
    LANGS="$@"
fi

echo "Connecting to Piston at: $HOST"

for LANG in $LANGS; do
    echo "Attempting to install latest $LANG..."
    curl -s -X POST "$HOST/api/v2/packages" \
         -H "Content-Type: application/json" \
         -d "{\"language\": \"$LANG\", \"version\": \"*\"}"
    echo ""
done

echo "Current runtimes:"
curl -s "$HOST/api/v2/runtimes" | jq -r '.[].language' | sort | uniq
