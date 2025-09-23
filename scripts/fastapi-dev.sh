#!/usr/bin/env bash
set -e  # Exit on any error
# Immediately exit if REPO_ROOT is not set
if [ -z "$REPO_ROOT" ]; then
    echo "Error: REPO_ROOT is not set. Run this script from the Nix devShell."
    exit 1
fi
cd $REPO_ROOT

SESSION_NAME="nixfastapi-dev"

# Function to handle user choice when session exists
handle_existing_session() {
    echo "Tmux session 🚩'$SESSION_NAME'🚩 already exists!"
    echo ""
    echo "What would you like to do?"
    echo "1) Kill existing session and create new one"
    echo "2) Attach to existing session"
    echo "3) Cancel operation"
    echo ""

    while true; do
        read -p "Enter choice (1/2/3): " choice
        case $choice in
            1)
                echo "Killing existing session..."
                if tmux kill-session -t $SESSION_NAME 2>/dev/null; then
                    echo "Session '$SESSION_NAME' killed successfully."
                    # Continue with script to create new session
                    return 0
                else
                    echo "Failed to kill session '$SESSION_NAME'."
                    exit 1
                fi
                ;;
            2)
                echo "Attaching to existing session..."
                tmux attach-session -t $SESSION_NAME
                exit 0
                ;;
            3)
                echo "Operation cancelled."
                exit 0
                ;;
            *)
                echo "Invalid choice. Please enter 1, 2, or 3."
                ;;
        esac
    done
}

# If a session with this name already exists, ask user what to do
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    handle_existing_session
fi

docker pull valkey/valkey:9.0
docker pull mongo:8.0.13

tmux new-session -d -s $SESSION_NAME -n "💨_Tailwind" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:0 "tailwindcss -i ./app/style/input.css -o ./app/style/output.css --watch" C-m

tmux new-window -t $SESSION_NAME -n "🪵_Lazydocker" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:1 "lazydocker" C-m

tmux new-window -t $SESSION_NAME -n "🔑_Valkey" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:2 "docker run --rm -p 6379:6379 -v ./data/valkey:/data --env VALKEY_EXTRA_FLAGS='--save 60 1 --loglevel debug' --name valkey valkey/valkey:9.0" C-m

tmux new-window -t $SESSION_NAME -n "🥭_MongoDB" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:3 "docker run --rm -p 27017:27017 -v ./data/mongo:/data/db --name mongo mongo:8.0.13 | jq" C-m

tmux new-window -t $SESSION_NAME -n "🧭_Compass" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:4 "mongodb-compass --trustedConnectionString mongodb://localhost:27017 --autoUpdates false" C-m

tmux new-window -t $SESSION_NAME -n "🦁_Brave" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:5 "brave --user-data-dir=/tmp/brave-dev-uvicorn --new-window --incognito --disable-cache --disk-cache-size=0 --media-cache-size=0 http://0.0.0.0:8000" C-m

tmux new-window -t $SESSION_NAME -n "🐍_FastAPI" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:6 "uvicorn app.app:app --port 8000 --host 0.0.0.0 --reload --timeout-keep-alive 1 --timeout-graceful-shutdown 1 --reload-delay 0.5 --reload-dir ./app" C-m

echo "Tmux created session ✨'$SESSION_NAME'✨"
tmux attach-session -t $SESSION_NAME
