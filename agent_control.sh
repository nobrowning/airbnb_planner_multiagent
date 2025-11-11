#!/usr/bin/env bash

# ============================================
# A2A Multi-Agent System - Control Script
# ============================================
# Usage: ./agent_control.sh [command]
# Commands: start (default), stop, status, logs, clean, migrate

# ============================================
# Configuration
# ============================================

# Agent definitions: "name:port"
AGENT_CONFIGS=(
    "weather_agent:10001"
    "airbnb_agent:10002"
    "tripadvisor_agent:10003"
    "event_agent:10004"
    "finance_agent:10005"
    "flight_agent:10006"
    "hotel_agent:10007"
)

# Host agent settings
HOST_AGENT="host_agent"
HOST_PORT=8083

# Timing settings (seconds)
AGENT_STARTUP_DELAY=1
AGENT_INIT_WAIT=5
HOST_STARTUP_WAIT=3

# Log directory
LOG_DIR="./logs"

# ============================================
# Utility Functions
# ============================================

show_help() {
    echo "A2A Multi-Agent System - Control Script"
    echo ""
    echo "Usage: ./agent_control.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start      - Start all agents (default)"
    echo "  stop       - Stop all agents"
    echo "  status     - Check agent status"
    echo "  logs       - List all logs"
    echo "  logs NAME  - View specific log (e.g., logs weather_agent)"
    echo "  clean      - Clean all log files"
    echo "  migrate    - Migrate configuration"
    echo "  help       - Show this help"
    echo ""
    echo "Examples:"
    echo "  ./agent_control.sh"
    echo "  ./agent_control.sh status"
    echo "  ./agent_control.sh logs weather_agent"
    echo ""
}

check_port() {
    local name=$1
    local port=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        printf "✓ %-20s (port %5d) - Running\n" "$name" "$port"
    else
        printf "✗ %-20s (port %5d) - Not running\n" "$name" "$port"
    fi
}

# ============================================
# Command Functions
# ============================================

cmd_start() {
    set -e
    
    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "Error: .env file not found!"
        echo "Please copy .env.example to .env and configure it:"
        echo "  cp .env.example .env"
        exit 1
    fi

    # Export all variables from .env file
    set -a
    source "$SCRIPT_DIR/.env"
    set +a

    # Create log directory
    mkdir -p "$LOG_DIR"

    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        echo "Error: uv not found."
        echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    # Cleanup function - stop all agents on exit
    cleanup() {
        echo ""
        echo "Stopping all agents..."
        jobs -p | xargs kill 2>/dev/null || true
        wait
        echo "All agents stopped."
        exit 0
    }
    trap cleanup SIGINT SIGTERM

    echo "============================================"
    echo "Starting A2A Multi-Agent System"
    echo "============================================"
    echo ""
    
    # Start all sub-agents
    echo "Starting sub-agents..."
    for config in "${AGENT_CONFIGS[@]}"; do
        agent="${config%:*}"
        port="${config#*:}"
        echo "  - Starting $agent on port $port..."
        (cd "$agent" && uv run __main__.py --port "$port") > "$LOG_DIR/${agent}.log" 2>&1 &
        sleep "$AGENT_STARTUP_DELAY"
    done
    
    # Wait for sub-agents to initialize
    echo ""
    echo "Waiting for sub-agents to initialize ($AGENT_INIT_WAIT seconds)..."
    sleep "$AGENT_INIT_WAIT"
    
    # Start host agent
    echo ""
    echo "Starting host agent on port $HOST_PORT..."
    uv run "$HOST_AGENT/__main__.py" > "$LOG_DIR/host_agent.log" 2>&1 &
    sleep "$HOST_STARTUP_WAIT"
    
    # Display status
    echo ""
    echo "============================================"
    echo "All agents started successfully!"
    echo "============================================"
    echo ""
    echo "Host UI: http://127.0.0.1:$HOST_PORT"
    echo "Logs: $LOG_DIR/"
    echo ""
    echo "Press Ctrl+C to stop all agents"
    echo ""
    
    # Keep script running
    wait
}

cmd_stop() {
    echo "Stopping all agents..."
    pkill -f "uv run.*agent.*__main__.py" 2>/dev/null || true
    echo "All agents stopped."
}

cmd_status() {
    echo "Checking agent status..."
    echo ""
    
    # Check sub-agents
    for agent in "${AGENTS[@]}"; do
        port=$(get_agent_port "$agent")
        agent_name=$(get_agent_name "$agent")
        check_port "$agent_name" "$port"
    done
    
    # Check host agent
    check_port "Host Agent" "$HOST_PORT"
}

cmd_logs() {
    if [ -z "$1" ]; then
        echo "Available logs:"
        ls -1 "$LOG_DIR/" 2>/dev/null || echo "No logs directory found"
    else
        if [ -f "$LOG_DIR/$1.log" ]; then
            tail -f "$LOG_DIR/$1.log"
        else
            echo "Log file not found: $LOG_DIR/$1.log"
            exit 1
        fi
    fi
}

cmd_clean() {
    echo "Cleaning logs..."
    rm -rf "$LOG_DIR"/*.log 2>/dev/null || true
    echo "Logs cleaned."
}

cmd_migrate() {
    if [ -f "./migrate_config.sh" ]; then
        ./migrate_config.sh
    else
        echo "Error: migrate_config.sh not found"
        exit 1
    fi
}

# ============================================
# Main Execution
# ============================================

# Parse command
COMMAND=${1:-start}
shift 2>/dev/null || true

case "$COMMAND" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    status)
        cmd_status
        ;;
    logs)
        cmd_logs "$@"
        ;;
    clean)
        cmd_clean
        ;;
    migrate)
        cmd_migrate
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Error: Unknown command '$COMMAND'"
        echo ""
        show_help
        exit 1
        ;;
esac
