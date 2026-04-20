#!/bin/bash
# Script to install basic Piston runtimes

if [ -z "$1" ]; then
    LANGS="python node javascript java go clike"
else
    LANGS="$@"
fi

echo "Available languages and versions can be checked at: http://localhost:2000/api/v2/packages"

for LANG in $LANGS; do
    echo "Attempting to install latest $LANG..."
    # * for version installs the latest available
    curl -X POST http://localhost:2000/api/v2/packages \
         -H "Content-Type: application/json" \
         -d "{\"language\": \"$LANG\", \"version\": \"*\"}"
    echo ""
done

echo "Check runtimes:"
curl -s http://localhost:2000/api/v2/runtimes | jq .
