#!/bin/bash

PORT="${1:-8080}"
DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$DIR/logs"
touch "$DIR/logs/app.log"
tail -f "$DIR/logs/app.log" &
ttyd -W -p "$PORT" -t fontSize=26 "$DIR/src/main.py"
