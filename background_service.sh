#!/bin/bash

# Racing Scanner Background Service
# This script runs the scanner in the background and can be used with Termux:Boot

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/background_service.log"
LOCK_FILE="$SCRIPT_DIR/background_service.lock"
VENV_DIR="$SCRIPT_DIR/venv"

# Colors for logging
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to log messages
log_message() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if service is already running
check_lock() {
    if [ -f "$LOCK_FILE" ]; then
        PID=$(cat "$LOCK_FILE" 2>/dev/null)
        if ps -p "$PID" > /dev/null 2>&1; then
            log_warning "Service already running with PID $PID"
            return 1
        else
            log_warning "Removing stale lock file"
            rm -f "$LOCK_FILE"
        fi
    fi
    return 0
}

# Function to create lock file
create_lock() {
    echo $$ > "$LOCK_FILE"
}

# Function to remove lock file
remove_lock() {
    rm -f "$LOCK_FILE"
}

# Function to check if it's racing hours
is_racing_hours() {
    local hour=$(date +%H)
    # Racing hours: 6 AM to 10 PM (06-22)
    if [ "$hour" -ge 6 ] && [ "$hour" -le 22 ]; then
        return 0
    else
        return 1
    fi
}

# Function to run the scanner
run_scanner() {
    log_message "Starting background scan..."
    
    # Activate virtual environment
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    else
        log_error "Virtual environment not found. Please run setup first."
        return 1
    fi
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Run the mobile scanner
    python3 racing_scanner_mobile.py \
        --days-forward 1 \
        --min-field-size 4 \
        --max-field-size 6 \
        --formats html \
        --verbose >> "$LOG_FILE" 2>&1
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_message "Background scan completed successfully"
    else
        log_error "Background scan failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Function to clean up old logs
cleanup_logs() {
    # Keep only last 7 days of logs
    if [ -f "$LOG_FILE" ]; then
        # Remove log entries older than 7 days
        awk -v cutoff="$(date -d '7 days ago' '+%Y-%m-%d')" '
            $1 >= cutoff { print }
        ' "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
}

# Function to show status
show_status() {
    echo "=== Racing Scanner Background Service Status ==="
    echo "Script Directory: $SCRIPT_DIR"
    echo "Log File: $LOG_FILE"
    echo "Lock File: $LOCK_FILE"
    echo ""
    
    if [ -f "$LOCK_FILE" ]; then
        PID=$(cat "$LOCK_FILE" 2>/dev/null)
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Service is RUNNING (PID: $PID)"
        else
            echo "❌ Service has stale lock file"
        fi
    else
        echo "❌ Service is NOT RUNNING"
    fi
    
    echo ""
    echo "=== Recent Log Entries ==="
    if [ -f "$LOG_FILE" ]; then
        tail -20 "$LOG_FILE"
    else
        echo "No log file found"
    fi
}

# Function to show usage
show_usage() {
    echo "Racing Scanner Background Service"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the background service"
    echo "  stop      - Stop the background service"
    echo "  status    - Show service status"
    echo "  run       - Run a single scan"
    echo "  clean     - Clean up old logs"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start   # Start background service"
    echo "  $0 status  # Check service status"
    echo "  $0 run     # Run a single scan"
}

# Main execution
main() {
    case "${1:-help}" in
        "start")
            if ! check_lock; then
                exit 1
            fi
            
            create_lock
            log_message "Background service started"
            
            # Set up signal handlers
            trap 'log_message "Received stop signal"; remove_lock; exit 0' TERM INT
            
            # Main loop
            while true; do
                if is_racing_hours; then
                    run_scanner
                    # Wait 30 minutes before next scan
                    sleep 1800
                else
                    log_message "Outside racing hours, sleeping for 1 hour"
                    sleep 3600
                fi
            done
            ;;
        
        "stop")
            if [ -f "$LOCK_FILE" ]; then
                PID=$(cat "$LOCK_FILE" 2>/dev/null)
                if ps -p "$PID" > /dev/null 2>&1; then
                    log_message "Stopping background service (PID: $PID)"
                    kill "$PID"
                    remove_lock
                    echo "Service stopped"
                else
                    log_warning "Service not running"
                    remove_lock
                fi
            else
                log_warning "No lock file found"
            fi
            ;;
        
        "status")
            show_status
            ;;
        
        "run")
            if ! check_lock; then
                exit 1
            fi
            
            create_lock
            run_scanner
            remove_lock
            ;;
        
        "clean")
            cleanup_logs
            log_message "Log cleanup completed"
            ;;
        
        "help"|"-h"|"--help")
            show_usage
            ;;
        
        *)
            log_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"