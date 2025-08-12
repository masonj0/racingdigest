# 🎯 Utopian Value Scanner V7.2 (The Rediscovery Edition)

A comprehensive Python script for scraping horse and dog racing sites to identify upcoming races with small fields and great returns for favorites and second favorites.

## ✨ Features

### 🏁 Multi-Discipline Racing Coverage
- **Thoroughbred Racing**: Horse racing from major tracks
- **Greyhound Racing**: Dog racing from UK tracks  
- **Harness Racing**: Standardbred and trotting races
- **International Coverage**: UK, Ireland, USA, France, Australia, South Africa

### 🎯 Smart Value Detection
- **Advanced Scoring Algorithm**: Identifies races with the best betting value
- **Field Size Analysis**: Focuses on small fields (4-8 runners) for better odds
- **Favorite Analysis**: Tracks odds for favorites and second favorites
- **Odds Spread Evaluation**: Identifies races with clear favorites

### 🌐 Multiple Data Sources
- **Racing & Sports API**: Primary global multi-discipline racing feed (NEW!)
- **Sporting Life Horse API**: High-quality JSON API for international horse racing
- **Racing Post**: Gold standard UK & Irish racing with enhanced scraping
- **Sky Sports Racing**: Comprehensive UK racing coverage
- **At The Races**: Multi-region racing with live odds
- **GB Greyhounds**: UK greyhound racing specialist
- **Automatic Fallbacks**: Robust error handling with multiple source attempts

### 📊 Rich Output
- **Interactive HTML Reports**: Beautiful, responsive web interface
- **JSON Export**: Machine-readable data for further analysis
- **Real-time Scoring**: Live value calculations and rankings
- **Mobile Friendly**: Works on all devices

## 🚀 Quick Start

### Installation

1. **Clone or download the script**
```bash
# Download the files to your local machine
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Scan today and tomorrow for races
python racing_scanner.py

# Include yesterday in the scan
python racing_scanner.py --days-back -1

# Scan next 3 days
python racing_scanner.py --days-forward 3

# Focus on very small fields (3-6 runners)
python racing_scanner.py --min-field-size 3 --max-field-size 6

# Enable interactive fallback for blocked sites
python racing_scanner.py --interactive

# Generate both HTML and JSON output
python racing_scanner.py --json-output

# Enable verbose logging
python racing_scanner.py --verbose
```

## 📖 Detailed Usage

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--days-back` | Days back to scan (negative number) | 0 |
| `--days-forward` | Days forward to scan | 1 |
| `--min-field-size` | Minimum runners in filtered results | 4 |
| `--max-field-size` | Maximum runners in filtered results | 8 |
| `--interactive` | Enable manual HTML input fallback | False |
| `--json-output` | Also generate JSON output | False |
| `--verbose` | Enable debug logging | False |

### Understanding Value Scores

The scanner uses a sophisticated algorithm to score races based on:

- **Field Size (35% weight)**: Smaller fields score higher
  - 3-5 runners: 100 points
  - 6-8 runners: 85 points  
  - 9-12 runners: 60 points

- **Favorite Odds (45% weight)**: Even money favorites score best
  - Evens to 3/2: 100 points
  - 3/2 to 5/2: 90 points
  - 5/2 to 4/1: 75 points

- **Odds Spread (15% weight)**: Clear favorites score higher
  - 2+ point spread: 100 points
  - 1.5+ point spread: 90 points
  - 1+ point spread: 80 points

- **Data Quality (5% weight)**: Complete data scores higher

### Bonus Multipliers
- **Live Odds**: +20% if live odds available
- **Greyhound Racing**: +10% (more predictable)
- **Small Field + Good Spread**: +15% additional bonus

### 🚀 API vs Web Scraping

**V7.2 "The Rediscovery Edition"** introduces premium API sources:

#### 🏆 **Racing & Sports API** (Primary Source)
- **🌍 Global Multi-Discipline**: Thoroughbred, harness, and greyhound racing worldwide
- **📅 Today's Racing Focus**: Optimized for current day race discovery
- **🔗 Direct Links**: PDF form guides and race URLs included
- **⚡ High Performance**: Single API call covers all disciplines and countries

#### 🐎 **Sporting Life Horse API** (Secondary)
- **🔒 Reliability**: JSON API is much more stable than web scraping
- **🌍 International Coverage**: Horse racing from multiple countries
- **📊 Rich Data**: Complete runner information with live odds
- **🛡️ Block-Resistant**: APIs are less likely to be blocked

#### 📰 **Enhanced Racing Post** (Premium UK/Irish)
- **🎯 Precision Scraping**: Uses data-test-selectors for stability
- **🏴󠁧󠁢󠁥󠁮󠁧󠁿 Gold Standard**: The definitive source for UK & Irish racing
- **🔄 Concurrent Processing**: Parallel meeting parsing for speed

These API sources provide superior data quality, reliability, and coverage compared to traditional web scraping methods.

## 🔧 Configuration

### Data Sources
You can enable/disable sources in the script configuration:

```python
"SOURCES": {
    "RacingAndSports": {"enabled": True},        # Primary global API
    "SportingLifeHorseApi": {"enabled": True},   # Horse racing API
    "RacingPost": {"enabled": True},             # UK/Irish premium
    "SkySports": {"enabled": True}, 
    "AtTheRaces": {"enabled": True},
    "GBGreyhounds": {"enabled": True}            # Greyhound racing
}
```

### Cache Settings
```python
"CACHE": {
    "DEFAULT_TTL": 1800,      # 30 minutes
    "MANUAL_FETCH_TTL": 21600, # 6 hours  
    "ENABLED": True
}
```

### HTTP Settings
```python
"HTTP": {
    "REQUEST_TIMEOUT": 30.0,
    "MAX_CONCURRENT_REQUESTS": 8,
    "MAX_RETRIES": 3
}
```

## 📊 Output Explanation

### HTML Report Sections

1. **🎯 Superfecta Fields**: Races matching your field size filter
2. **🔥 High Value**: Races with value scores 70+
3. **📋 All Races**: Complete results sorted by score

### Value Score Color Coding
- **🔴 90+ (Extreme Value)**: Red highlight - exceptional opportunities
- **🟠 80+ (High Value)**: Orange highlight - very good bets
- **🟢 70+ (Good Value)**: Green highlight - solid opportunities  
- **🔵 60+ (Decent Value)**: Blue highlight - reasonable bets

### Race Information
- **Course & Time**: Track name and local race time
- **Field Size**: Number of runners
- **Favorites**: Top 2 favorites with odds
- **Data Sources**: Which sites provided the data
- **Direct Links**: Click through to racecards and form guides

## 🛠️ Troubleshooting

### Common Issues

**"Required package not installed"**
```bash
pip install -r requirements.txt
```

**"zoneinfo not available"**
```bash
pip install backports.zoneinfo
```

**Sites blocking requests**
```bash
# Use interactive mode
python racing_scanner.py --interactive
```

**No races found**
- Try expanding date range: `--days-forward 2`
- Check if it's a racing day (avoid Sundays in some regions)
- Enable verbose logging: `--verbose`

### Cache Issues
```bash
# Clear cache if getting stale data
rm -rf .cache_v7_final/
```

### Log Files
Check `racing_scanner.log` for detailed error information.

## 🎲 Betting Strategy Tips

### High-Value Indicators
- **Score 85+**: Exceptional value, consider larger stakes
- **Score 70-84**: Good value, standard stakes  
- **Score 60-69**: Moderate value, smaller stakes

### Field Size Sweet Spots
- **4-5 runners**: Best for win bets and exactas
- **6-8 runners**: Good for trifectas and superfectas
- **3 runners**: Limited options but very predictable

### Discipline Preferences
- **Greyhounds**: More predictable, faster races
- **Thoroughbreds**: Higher stakes, more variables
- **Harness**: Consistent pacing, good for multiples

### Risk Management
- Never bet more than you can afford to lose
- Use the value scores as guidance, not guarantees
- Consider track conditions and weather
- Check for late scratchings before betting

## 🔒 Privacy & Ethics

- The script respects robots.txt and rate limits
- No personal data is collected or stored
- Caching reduces server load
- Educational and research purposes only

## 📝 License

This script is provided for educational and research purposes. Please gamble responsibly and within your means.

## 🤝 Contributing

Feel free to suggest improvements or report issues. The script is designed to be easily extensible with new data sources.

---

**⚠️ Disclaimer**: This tool is for informational purposes only. Past performance does not guarantee future results. Please gamble responsibly.
