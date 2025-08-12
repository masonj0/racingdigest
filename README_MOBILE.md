# 🎯 Racing Scanner Mobile Edition

## 📱 Mobile-Optimized Racing Value Scanner

A mobile-first version of the Racing Value Scanner, optimized for Android devices running Termux. Features reduced concurrency for better battery life, touch-friendly UI, and PWA support for an app-like experience.

## ✨ Mobile Features

### 🚀 Performance Optimizations
- **Reduced Concurrency**: 6 concurrent requests (vs 12 on desktop)
- **Extended Timeouts**: 45 seconds for mobile networks
- **Intelligent Caching**: 1-hour TTL to reduce network usage
- **Battery-Friendly**: Reduced retries and gentler backoff

### 📱 Mobile UI
- **Touch-Friendly**: 44px minimum touch targets
- **Responsive Design**: Works on all screen sizes
- **Dark Mode**: Automatic based on system preference
- **PWA Support**: Add to home screen functionality
- **Pull-to-Refresh**: Swipe down to refresh data
- **Auto-Refresh**: Updates every 5 minutes

### 🔄 Background Execution
- **Termux:Boot Integration**: Automatic startup
- **Smart Scheduling**: Only runs during racing hours (6 AM - 10 PM)
- **File-Based Communication**: Reports saved to shared storage
- **Service Management**: Start/stop/status commands

## 🚀 Quick Start

### 1. Install Termux
```bash
# Download from F-Droid (recommended)
# https://f-droid.org/en/packages/com.termux/
```

### 2. Setup Racing Scanner
```bash
# Update and install dependencies
pkg update -y
pkg install -y git python python-pip

# Clone repository
git clone https://github.com/yourusername/racing-scanner.git
cd racing-scanner

# Run initial setup
chmod +x launcher.sh
./launcher.sh setup
```

### 3. Run Your First Scan
```bash
# Run the scanner
./launcher.sh run
```

## 📋 File Structure

```
racing-scanner/
├── racing_scanner_mobile.py    # Mobile-optimized scanner
├── launcher.sh                 # Easy setup and execution
├── background_service.sh       # Background service management
├── mobile_template.html        # Mobile HTML template
├── race_card.html             # Individual race card template
├── manifest.json              # PWA manifest
├── sw.js                      # Service worker
├── requirements.txt           # Python dependencies
├── setup_instructions.md      # Detailed setup guide
└── README_MOBILE.md          # This file
```

## 🎮 Usage

### Basic Commands

```bash
# Initial setup (first time only)
./launcher.sh setup

# Run a scan
./launcher.sh run

# Update dependencies
./launcher.sh install

# Clean cache and output
./launcher.sh clean
```

### Advanced Usage

```bash
# Run with custom parameters
python3 racing_scanner_mobile.py \
    --days-forward 2 \
    --min-field-size 3 \
    --max-field-size 8 \
    --verbose

# Background service
./background_service.sh start    # Start background scanning
./background_service.sh status   # Check service status
./background_service.sh stop     # Stop background scanning
```

## 🔧 Configuration

### Mobile Settings

The mobile version includes these optimizations in `racing_scanner_mobile.py`:

```python
MOBILE_CONFIG = {
    "HTTP": {
        "MAX_CONCURRENT_REQUESTS": 6,  # Reduced for mobile
        "REQUEST_TIMEOUT": 45.0,       # Longer for mobile networks
        "MAX_RETRIES": 2,              # Reduced to save battery
    },
    "CACHE": {
        "DEFAULT_TTL": 3600,           # 1 hour cache
        "MANUAL_FETCH_TTL": 43200,     # 12 hours for manual fetches
    },
    "OUTPUT": {
        "MOBILE_OUTPUT_DIR": "/sdcard/Download/RacingScanner"
    }
}
```

### Customization

Adjust settings based on your device:

**For Slow Devices:**
```python
"MAX_CONCURRENT_REQUESTS": 3,
```

**For Limited Data:**
```python
"DEFAULT_TTL": 7200,  # 2 hours
```

**For Battery Optimization:**
```python
"MAX_RETRIES": 1,
```

## 📱 Mobile UI Features

### PWA (Progressive Web App)
- **Add to Home Screen**: Install as a native app
- **Offline Support**: Basic offline functionality
- **App-like Experience**: Full-screen, no browser UI

### Touch Interactions
- **Pull-to-Refresh**: Swipe down to refresh data
- **Long Press**: Long press status bar to refresh
- **Touch Feedback**: Visual feedback on touch
- **Large Buttons**: Easy to tap on mobile

### Auto-Refresh
- **Smart Timing**: Updates every 5 minutes
- **Visual Indicator**: Pulsing dot shows refresh status
- **Manual Override**: Tap to refresh immediately

## 🔄 Background Execution

### Termux:Boot Setup

1. Install Termux:Boot from F-Droid
2. Create boot script:

```bash
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/racing-scanner.sh << 'EOF'
#!/bin/bash
cd /data/data/com.termux/files/home/racing-scanner
./background_service.sh start
EOF
chmod +x ~/.termux/boot/racing-scanner.sh
```

### Service Management

```bash
# Start background service
./background_service.sh start

# Check status
./background_service.sh status

# Stop service
./background_service.sh stop

# Run single scan
./background_service.sh run
```

## 📊 Understanding Results

### Value Scores
- **90+ (Red)**: Extreme value opportunities
- **80-89 (Orange)**: High value opportunities
- **70-79 (Green)**: Good value opportunities
- **60-69 (Blue)**: Decent value opportunities

### Race Categories
- **🎯 Superfecta Fields**: 4-6 runners (optimal for superfecta)
- **🔥 High Value**: Score 70+ (best opportunities)
- **📋 All Races**: Complete list by score

### Data Sources
Aggregates from multiple sources:
- RacingAndSports (Australia)
- SportingLife (UK)
- RacingPost (UK)
- SkySports (UK)
- AtTheRaces (Multiple regions)

## 🛠️ Troubleshooting

### Common Issues

**Permission Denied**
```bash
chmod +x launcher.sh
chmod +x background_service.sh
```

**Python Dependencies**
```bash
./launcher.sh install
```

**Storage Permission**
```bash
termux-setup-storage
```

**Network Timeout**
```bash
# Increase timeout in racing_scanner_mobile.py
"REQUEST_TIMEOUT": 60.0,
```

### Performance Tips

1. **Close other apps** when running scans
2. **Use WiFi** instead of mobile data when possible
3. **Adjust concurrency** based on your device speed
4. **Enable battery optimization** for Termux

## 📱 Mobile-Specific Features

### File Locations
- **Reports**: `/sdcard/Download/RacingScanner/`
- **Logs**: `./racing_scanner_mobile.log`
- **Cache**: `./.cache_v7_final/`

### Browser Integration
- **Auto-open**: Reports open in default browser
- **PWA**: Add to home screen for app-like experience
- **Shared Storage**: Easy access from file manager

### Notifications
- **Scan Complete**: Visual feedback in terminal
- **Background Service**: Status updates in logs
- **Error Alerts**: Clear error messages

## 🔒 Privacy & Security

- **Local Processing**: All data processed on device
- **No Tracking**: No analytics or user tracking
- **Open Source**: Full code transparency
- **Local Storage**: All data stored locally

## 📞 Support

### Getting Help

1. **Check Logs**: `cat racing_scanner_mobile.log`
2. **Verbose Mode**: Add `--verbose` flag
3. **Service Status**: `./background_service.sh status`
4. **Clean Start**: `./launcher.sh clean`

### Debug Commands

```bash
# Check Python version
python3 --version

# Check available packages
pkg list-installed | grep python

# Check disk space
df -h

# Check network
ping -c 3 google.com
```

## 🎯 Success Indicators

You'll know everything is working when:

- ✅ Launcher script runs without errors
- ✅ HTML report opens in browser
- ✅ PWA features work (add to home screen)
- ✅ Auto-refresh indicator pulses
- ✅ Background service starts successfully

## 🚀 Next Steps

1. **Customize Settings**: Adjust for your device and preferences
2. **Set Up Background Scanning**: Configure automatic updates
3. **Optimize Performance**: Fine-tune concurrency and timeouts
4. **Explore Advanced Features**: JSON/CSV export, custom filters

---

**Good luck with your mobile racing analysis! 🍀**

*Remember: This tool is for educational purposes. Always bet responsibly and within your means.*