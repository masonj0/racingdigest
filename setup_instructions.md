# 🎯 Racing Scanner Mobile Setup Instructions

## Overview

This guide will help you set up the Racing Value Scanner on your Android device using Termux. The mobile version is optimized for battery life and touch interaction, with reduced concurrency and mobile-friendly output.

## 📱 Prerequisites

1. **Android Device** (Android 7.0 or higher recommended)
2. **Termux** - Download from [F-Droid](https://f-droid.org/en/packages/com.termux/) (recommended) or Google Play Store
3. **Internet Connection** for initial setup and data fetching

## 🚀 Quick Start (5 minutes)

### Step 1: Install Termux

1. Download Termux from [F-Droid](https://f-droid.org/en/packages/com.termux/)
2. Install and open Termux
3. Grant storage permissions when prompted

### Step 2: Download the Racing Scanner

```bash
# Update package list
pkg update -y

# Install git and Python
pkg install -y git python python-pip

# Clone the repository (replace with your actual repository URL)
git clone https://github.com/yourusername/racing-scanner.git
cd racing-scanner

# Make the launcher executable
chmod +x launcher.sh
```

### Step 3: Run Initial Setup

```bash
# Run the initial setup (this will take a few minutes)
./launcher.sh setup
```

### Step 4: Run Your First Scan

```bash
# Run the scanner
./launcher.sh run
```

The scanner will:
- Fetch racing data from multiple sources
- Generate a mobile-optimized HTML report
- Save it to `/sdcard/Download/RacingScanner/`
- Open it in your browser

## 📋 Detailed Setup Instructions

### Option A: Using the Launcher Script (Recommended)

The launcher script automates everything for you:

```bash
# Initial setup (first time only)
./launcher.sh setup

# Run a scan
./launcher.sh run

# Update dependencies
./launcher.sh install

# Clean cache and output
./launcher.sh clean

# Show help
./launcher.sh help
```

### Option B: Manual Setup

If you prefer manual control:

```bash
# 1. Create Python virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create output directories
mkdir -p output
mkdir -p .cache_v7_final

# 5. Run the scanner
python3 racing_scanner_mobile.py --days-forward 1 --formats html
```

## 🔧 Configuration Options

### Mobile-Optimized Settings

The mobile version includes these optimizations:

- **Reduced Concurrency**: 6 concurrent requests (vs 12 on desktop)
- **Longer Timeouts**: 45 seconds for mobile networks
- **Extended Cache**: 1 hour TTL to reduce network usage
- **Touch-Friendly UI**: 44px minimum touch targets
- **PWA Support**: Add to home screen functionality

### Customizing the Scanner

Edit `racing_scanner_mobile.py` to modify settings:

```python
MOBILE_CONFIG = {
    "HTTP": {
        "MAX_CONCURRENT_REQUESTS": 6,  # Adjust based on your device
        "REQUEST_TIMEOUT": 45.0,       # Increase for slow connections
    },
    "FILTERS": {
        "MIN_FIELD_SIZE": 4,           # Minimum runners
        "MAX_FIELD_SIZE": 6,           # Maximum runners
    }
}
```

## 📱 Using the Mobile App

### Running Scans

```bash
# Quick scan (today's races)
./launcher.sh run

# Scan with custom parameters
python3 racing_scanner_mobile.py --days-forward 2 --min-field-size 3 --max-field-size 8

# Verbose output for debugging
python3 racing_scanner_mobile.py --verbose
```

### Viewing Results

1. **HTML Report**: Opens automatically in your browser
2. **Location**: `/sdcard/Download/RacingScanner/`
3. **PWA Features**: 
   - Add to home screen for app-like experience
   - Auto-refresh every 5 minutes
   - Pull-to-refresh gesture
   - Dark mode support

### Mobile UI Features

- **Touch-Friendly**: Large buttons and touch targets
- **Responsive Design**: Works on all screen sizes
- **Dark Mode**: Automatic based on system preference
- **Auto-Refresh**: Updates every 5 minutes
- **Pull-to-Refresh**: Swipe down to refresh
- **Long Press**: Long press status bar to refresh

## 🔄 Background Execution (Advanced)

### Using Termux:Boot

For automatic background scanning:

1. Install Termux:Boot from F-Droid
2. Create a boot script:

```bash
# Create boot directory
mkdir -p ~/.termux/boot

# Create background scanner script
cat > ~/.termux/boot/racing-scanner.sh << 'EOF'
#!/bin/bash
cd /data/data/com.termux/files/home/racing-scanner
./launcher.sh run
EOF

# Make executable
chmod +x ~/.termux/boot/racing-scanner.sh
```

### Using Cron (Alternative)

```bash
# Install cronie
pkg install -y cronie

# Edit crontab
crontab -e

# Add this line to run every 30 minutes during racing hours
*/30 6-22 * * * cd /data/data/com.termux/files/home/racing-scanner && ./launcher.sh run
```

## 🛠️ Troubleshooting

### Common Issues

**1. Permission Denied**
```bash
# Fix file permissions
chmod +x launcher.sh
chmod +x racing_scanner_mobile.py
```

**2. Python Dependencies Not Found**
```bash
# Reinstall dependencies
./launcher.sh install
```

**3. Network Timeout**
```bash
# Increase timeout in racing_scanner_mobile.py
"REQUEST_TIMEOUT": 60.0,  # Increase to 60 seconds
```

**4. Storage Permission**
```bash
# Grant storage permission in Termux
termux-setup-storage
```

**5. Virtual Environment Issues**
```bash
# Remove and recreate virtual environment
rm -rf venv
./launcher.sh setup
```

### Performance Optimization

**For Slow Devices:**
```python
# Reduce concurrency further
"MAX_CONCURRENT_REQUESTS": 3,
```

**For Limited Data:**
```python
# Increase cache duration
"DEFAULT_TTL": 7200,  # 2 hours
```

**For Battery Optimization:**
```python
# Reduce retries
"MAX_RETRIES": 1,
```

## 📊 Understanding the Results

### Value Scores

- **90+ (Red)**: Extreme value opportunities
- **80-89 (Orange)**: High value opportunities  
- **70-79 (Green)**: Good value opportunities
- **60-69 (Blue)**: Decent value opportunities

### Race Categories

- **🎯 Superfecta Fields**: 4-6 runners (optimal for superfecta betting)
- **🔥 High Value**: Score 70+ (best betting opportunities)
- **📋 All Races**: Complete list sorted by value score

### Data Sources

The scanner aggregates data from:
- RacingAndSports (Australia)
- SportingLife (UK)
- RacingPost (UK)
- SkySports (UK)
- AtTheRaces (Multiple regions)
- And more...

## 🔒 Privacy & Security

- **No Data Collection**: All processing happens locally
- **No Tracking**: No analytics or user tracking
- **Open Source**: Full transparency of code
- **Local Storage**: All data stored on your device

## 📞 Support

### Getting Help

1. **Check Logs**: `cat racing_scanner_mobile.log`
2. **Verbose Mode**: Add `--verbose` flag for detailed output
3. **Clean Start**: Run `./launcher.sh clean` to reset

### Common Commands

```bash
# Check system status
pkg list-installed | grep python

# Check Python version
python3 --version

# Check available disk space
df -h

# Check network connectivity
ping -c 3 google.com
```

## 🎯 Next Steps

Once you have the basic setup working:

1. **Customize Filters**: Adjust field size and value thresholds
2. **Set Up Background Scanning**: Configure automatic updates
3. **Optimize for Your Device**: Adjust concurrency and timeouts
4. **Explore Advanced Features**: JSON/CSV export, custom date ranges

## 🏆 Success Indicators

You'll know everything is working when:

- ✅ Launcher script runs without errors
- ✅ HTML report opens in browser
- ✅ Report shows racing data with value scores
- ✅ PWA features work (add to home screen)
- ✅ Auto-refresh indicator pulses

---

**Good luck with your betting! 🍀**

*Remember: This tool is for educational purposes. Always bet responsibly and within your means.*