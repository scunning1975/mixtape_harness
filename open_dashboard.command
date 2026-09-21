#!/bin/bash
# Double-click to open the project dashboard.
# Starts the server if it isn't already running, then opens the browser.
cd "$(dirname "$0")"

if ! lsof -ti :8080 >/dev/null 2>&1; then
    nohup python3 dashboard_server.py > /tmp/gtd_dashboard.log 2>&1 &
    sleep 2
fi

open "http://localhost:8080"
