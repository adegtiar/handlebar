DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$DIR/logs"
touch "$DIR/logs/app.log"
tail -f "$DIR/logs/app.log" &
ttyd -W -p 8080 "$DIR/src/main.py"
