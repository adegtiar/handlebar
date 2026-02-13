mkdir -p /workspaces/handlebar/logs
touch /workspaces/handlebar/logs/app.log
tail -f /workspaces/handlebar/logs/app.log &
ttyd -W -p 8080 /workspaces/handlebar/src/main.py
