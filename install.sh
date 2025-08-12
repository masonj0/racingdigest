#!/bin/bash

echo "🎯 Utopian Value Scanner - Installation Script"
echo "=============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Try to install dependencies
echo "📦 Installing dependencies..."

if python3 -m pip install -r requirements.txt; then
    echo "✅ Dependencies installed successfully"
elif python3 -m pip install --user -r requirements.txt; then
    echo "✅ Dependencies installed in user directory"
elif pip install --break-system-packages -r requirements.txt; then
    echo "✅ Dependencies installed (system packages)"
else
    echo "❌ Failed to install dependencies. Please install manually:"
    echo "   pip install httpx aiofiles beautifulsoup4 jinja2 curl-cffi lxml"
    exit 1
fi

# Test the script
echo "🧪 Testing the script..."
if python3 racing_scanner.py --help > /dev/null; then
    echo "✅ Script is working correctly!"
    echo ""
    echo "🚀 Ready to use! Try these commands:"
    echo "   python3 racing_scanner.py                    # Basic scan"
    echo "   python3 racing_scanner.py --days-forward 2   # Scan next 2 days"
    echo "   python3 racing_scanner.py --interactive      # Interactive mode"
    echo "   python3 racing_scanner.py --verbose          # Verbose output"
else
    echo "❌ Script test failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "📖 For full documentation, see README.md"
echo "🍀 Good luck with your racing analysis!"