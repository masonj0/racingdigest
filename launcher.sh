#!/bin/bash

# Racing Scanner Mobile Launcher for Termux
# This script sets up the Python environment and runs the racing scanner

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
OUTPUT_DIR="$SCRIPT_DIR/output"
CACHE_DIR="$SCRIPT_DIR/.cache_v7_final"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
MAIN_SCRIPT="$SCRIPT_DIR/racing_scanner.py"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Termux environment
check_termux() {
    if [ -d "/data/data/com.termux" ]; then
        print_success "Running in Termux environment"
        return 0
    else
        print_warning "Not running in Termux - some features may not work"
        return 1
    fi
}

# Function to install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if command_exists pkg; then
        # Termux package manager
        pkg update -y
        pkg install -y python python-pip git curl
    elif command_exists apt; then
        # Debian/Ubuntu
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv git curl
    elif command_exists yum; then
        # CentOS/RHEL
        sudo yum install -y python3 python3-pip git curl
    else
        print_error "No supported package manager found"
        exit 1
    fi
    
    print_success "System dependencies installed"
}

# Function to create Python virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment ready"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install dependencies
    pip install -r "$REQUIREMENTS_FILE"
    
    print_success "Python dependencies installed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$CACHE_DIR"
    
    print_success "Directories created"
}

# Function to run the scanner
run_scanner() {
    print_status "Starting Racing Scanner..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Check if main script exists
    if [ ! -f "$MAIN_SCRIPT" ]; then
        print_error "Main script not found: $MAIN_SCRIPT"
        exit 1
    fi
    
    # Run the scanner with mobile-optimized settings
    print_status "Running scanner with mobile-optimized settings..."
    
    python3 "$MAIN_SCRIPT" \
        --days-forward 1 \
        --min-field-size 4 \
        --max-field-size 6 \
        --formats html \
        --verbose
    
    print_success "Scanner completed!"
}

# Function to open the report
open_report() {
    print_status "Looking for generated report..."
    
    # Find the most recent HTML report
    LATEST_REPORT=$(find "$OUTPUT_DIR" -name "racing_report_*.html" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")
    
    if [ -n "$LATEST_REPORT" ]; then
        print_success "Found report: $LATEST_REPORT"
        
        # Copy to shared storage for easy access
        if check_termux; then
            SHARED_DIR="/sdcard/Download/RacingScanner"
            mkdir -p "$SHARED_DIR"
            cp "$LATEST_REPORT" "$SHARED_DIR/"
            print_success "Report copied to: $SHARED_DIR/"
            print_status "You can now open the report in your mobile browser"
        fi
        
        # Try to open in browser if possible
        if command_exists termux-open; then
            termux-open "$LATEST_REPORT"
        elif command_exists xdg-open; then
            xdg-open "$LATEST_REPORT"
        else
            print_status "Report saved to: $LATEST_REPORT"
        fi
    else
        print_warning "No HTML report found"
    fi
}

# Function to show usage
show_usage() {
    echo "Racing Scanner Mobile Launcher"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup     - Initial setup (install dependencies)"
    echo "  run       - Run the scanner"
    echo "  install   - Install/update dependencies"
    echo "  clean     - Clean cache and output directories"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # First time setup"
    echo "  $0 run      # Run the scanner"
    echo "  $0 install  # Update dependencies"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    
    rm -rf "$CACHE_DIR"/*
    rm -rf "$OUTPUT_DIR"/*
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo "🎯 Racing Scanner Mobile Launcher"
    echo "=================================="
    
    # Check if we're in Termux
    check_termux
    
    # Parse command line arguments
    case "${1:-run}" in
        "setup")
            print_status "Running initial setup..."
            install_system_deps
            setup_venv
            install_python_deps
            create_directories
            print_success "Setup completed! You can now run: $0 run"
            ;;
        "run")
            # Check if virtual environment exists
            if [ ! -d "$VENV_DIR" ]; then
                print_warning "Virtual environment not found. Running setup first..."
                setup_venv
                install_python_deps
                create_directories
            fi
            
            run_scanner
            open_report
            ;;
        "install")
            setup_venv
            install_python_deps
            print_success "Dependencies updated!"
            ;;
        "clean")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"