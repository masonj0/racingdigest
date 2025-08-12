#!/usr/bin/env python3
"""
Utopian Value Scanner V7.2 Mobile Edition

Mobile-optimized version with reduced concurrency for better battery life
and performance on mobile devices.
"""

# Import the original scanner
import sys
import os
from pathlib import Path

# Add the current directory to Python path to import the original scanner
sys.path.insert(0, str(Path(__file__).parent))

# Import the original scanner's main components
from racing_scanner import (
    CONFIG, HTML_TEMPLATE, CacheManager, AsyncHttpClient, 
    RacingDataAggregator, OutputManager, main_async
)

# Mobile-specific configuration overrides
MOBILE_CONFIG = {
    # Reduced concurrency for mobile devices
    "HTTP": {
        "REQUEST_TIMEOUT": 45.0,  # Increased timeout for mobile networks
        "MAX_CONCURRENT_REQUESTS": 6,  # Reduced from 12 to 6 for mobile
        "MAX_RETRIES": 2,  # Reduced retries to save battery
        "RETRY_BACKOFF_BASE": 1.5,  # Gentler backoff
        "USER_AGENTS": [
            "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        ]
    },
    
    # Mobile-optimized cache settings
    "CACHE": {
        "DEFAULT_TTL": 3600,      # 1 hour for mobile (longer to reduce network usage)
        "MANUAL_FETCH_TTL": 43200, # 12 hours for manual fetches
        "ENABLED": True
    },
    
    # Mobile-friendly output settings
    "OUTPUT": {
        "AUTO_OPEN_BROWSER": False,  # Don't auto-open on mobile
        "MOBILE_OUTPUT_DIR": "/sdcard/Download/RacingScanner"  # Android shared storage
    },
    
    # Mobile-optimized filters
    "FILTERS": {
        "MIN_FIELD_SIZE": 4,
        "MAX_FIELD_SIZE": 6,
    }
}

# Override the original CONFIG with mobile settings
CONFIG.update(MOBILE_CONFIG)

# Mobile-optimized HTML template
MOBILE_HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
    <meta name="theme-color" content="#007bff">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Racing Scanner">
    <title>{{ config.APP_NAME }} - Racing Value Scanner</title>
    
    <!-- PWA Manifest -->
    <link rel="manifest" href="manifest.json">
    
    <!-- Apple Touch Icons -->
    <link rel="apple-touch-icon" href="icon-192.png">
    <link rel="apple-touch-icon" sizes="152x152" href="icon-152.png">
    <link rel="apple-touch-icon" sizes="180x180" href="icon-180.png">
    
    <style>
        :root {
            --primary-color: #007bff;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --dark-bg: #121212;
            --dark-surface: #1e1e1e;
            --dark-border: #333;
            --touch-target: 44px;
        }
        
        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        .container {
            max-width: 100%;
            margin: 0;
            padding: 16px;
            background-color: #fff;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary-color), #0056b3);
            color: white;
            padding: 20px 16px;
            margin: -16px -16px 20px -16px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,123,255,0.3);
        }
        
        .header h1 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .status-bar {
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            font-size: 0.9rem;
        }
        
        .status-bar.auto-refresh {
            background: #fff3cd;
            border-color: #ffeaa7;
        }
        
        .refresh-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--success-color);
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .tabs {
            display: flex;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 4px;
            margin-bottom: 20px;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        .tab {
            flex: 1;
            min-width: 120px;
            padding: 12px 16px;
            text-align: center;
            background: transparent;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            color: #6c757d;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        
        .tab.active {
            background: var(--primary-color);
            color: white;
            box-shadow: 0 2px 4px rgba(0,123,255,0.3);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .race {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }
        
        .race:active {
            transform: scale(0.98);
        }
        
        .race.value-extreme {
            border-left: 6px solid var(--danger-color);
            background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
        }
        
        .race.value-high {
            border-left: 5px solid #ff8800;
            background: linear-gradient(135deg, #fff8f0 0%, #ffeecc 100%);
        }
        
        .race.value-good {
            border-left: 4px solid var(--success-color);
            background: linear-gradient(135deg, #f0fff0 0%, #e6ffe6 100%);
        }
        
        .race.value-decent {
            border-left: 3px solid var(--primary-color);
            background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        }
        
        .race-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .course-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1a1a1a;
            flex: 1;
        }
        
        .discipline-icon {
            font-size: 1.5rem;
            margin-left: 8px;
        }
        
        .race-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }
        
        .meta-pill {
            background: #f8f9fa;
            color: #495057;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            border: 1px solid #e9ecef;
        }
        
        .value-score {
            background: var(--primary-color);
            color: white;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .value-score-90plus { background: var(--danger-color); }
        .value-score-80plus { background: #ff8800; }
        .value-score-70plus { background: var(--success-color); }
        .value-score-60plus { background: var(--primary-color); }
        
        .favorites-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .favorite-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            border: 1px solid #e9ecef;
        }
        
        .favorite-name {
            font-weight: 600;
            margin-bottom: 4px;
            font-size: 0.9rem;
        }
        
        .favorite-odds {
            font-size: 1rem;
            color: var(--primary-color);
            font-weight: 500;
        }
        
        .race-details {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-size: 0.85rem;
            color: #6c757d;
        }
        
        .field-size {
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 500;
        }
        
        .sources {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }
        
        .source-tag {
            background: #6c757d;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
        }
        
        .action-buttons {
            display: flex;
            gap: 8px;
        }
        
        .btn {
            flex: 1;
            padding: 12px 16px;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            text-decoration: none;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            min-height: var(--touch-target);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn-primary {
            background: var(--primary-color);
            color: white;
        }
        
        .btn-secondary {
            background: var(--success-color);
            color: white;
        }
        
        .btn:active {
            transform: scale(0.95);
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #6c757d;
        }
        
        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 0.8rem;
            border-top: 1px solid #e9ecef;
            margin-top: 40px;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: var(--dark-bg);
                color: #e0e0e0;
            }
            
            .container {
                background-color: var(--dark-bg);
            }
            
            .race {
                background-color: var(--dark-surface);
                border-color: var(--dark-border);
            }
            
            .course-name {
                color: #e0e0e0;
            }
            
            .meta-pill {
                background: #333;
                color: #ccc;
                border-color: #444;
            }
            
            .favorite-card {
                background: #333;
                border-color: #444;
            }
            
            .field-size {
                background: #444;
                color: #ccc;
            }
            
            .status-bar {
                background: #2c3e50;
                border-color: #4dabf7;
            }
            
            .status-bar.auto-refresh {
                background: #4d331a;
                border-color: #ff8800;
            }
            
            .tabs {
                background: #333;
            }
            
            .tab {
                color: #ccc;
            }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🎯 {{ config.APP_NAME }}</h1>
    </div>
    
    <div class="status-bar" id="statusBar">
        <div class="refresh-indicator" id="refreshIndicator"></div>
        <span id="statusText">
            📊 Found <b>{{ stats.total_races_found }}</b> races from <b>{{ stats.per_source_counts | length }}</b> sources. 
            <b>{{ stats.races_after_dedup }}</b> unique after merging. 
            <b>{{ value_races | length }}</b> high-value opportunities.
            ⏱️ <b>{{ "%.1f"|format(stats.duration_seconds) }}s</b>
        </span>
    </div>
    
    <div class="tabs">
        <button class="tab active" onclick="showTab('filtered-races', this)">
            🎯 Superfecta ({{ filtered_races | length }})
        </button>
        <button class="tab" onclick="showTab('value-races', this)">
            🔥 High Value ({{ value_races | length }})
        </button>
        <button class="tab" onclick="showTab('all-races', this)">
            📋 All ({{ all_races | length }})
        </button>
    </div>
    
    <div id="filtered-races" class="tab-content active">
        <h2>🎯 Superfecta Fields ({{ min_runners }}-{{ max_runners }} Runners)</h2>
        {% if filtered_races %}
            {% for race in filtered_races %}
                <div class="race {{ race.discipline }} value-{% if race.value_score >= 90 %}extreme{% elif race.value_score >= 80 %}high{% elif race.value_score >= 70 %}good{% else %}decent{% endif %}" data-score="{{ race.value_score }}">
                    <div class="race-header">
                        <div class="course-name">{{ race.course }}</div>
                        <div class="discipline-icon">
                            {% if race.discipline == 'thoroughbred' %}🐎{% elif race.discipline == 'harness' %}🏇{% elif race.discipline == 'greyhound' %}🐕{% endif %}
                        </div>
                    </div>
                    
                    <div class="race-meta">
                        <span class="meta-pill">{{ race.country }}</span>
                        <span class="meta-pill">{{ race.local_time }} {{ race.timezone_name }}</span>
                        <span class="meta-pill value-score value-score-{% if race.value_score >= 90 %}90plus{% elif race.value_score >= 80 %}80plus{% elif race.value_score >= 70 %}70plus{% elif race.value_score >= 60 %}60plus{% endif %}">
                            {{ "%.0f"|format(race.value_score) }}★
                        </span>
                    </div>
                    
                    <div class="favorites-grid">
                        <div class="favorite-card">
                            <div class="favorite-name">🥇 {{ (race.favorite.name or 'Unknown') if race.favorite else 'N/A' }}</div>
                            <div class="favorite-odds">{{ (race.favorite.odds_str or 'SP') if race.favorite else '' }}</div>
                        </div>
                        <div class="favorite-card">
                            <div class="favorite-name">🥈 {{ (race.second_favorite.name or 'Unknown') if race.second_favorite else 'N/A' }}</div>
                            <div class="favorite-odds">{{ (race.second_favorite.odds_str or 'SP') if race.second_favorite else '' }}</div>
                        </div>
                    </div>
                    
                    <div class="race-details">
                        <div class="field-size">
                            <strong>Field:</strong> {{ race.field_size }} runners
                        </div>
                        <div class="sources">
                            {% for source in race.data_sources.values() | unique | sort %}
                                <span class="source-tag">{{ source.upper() }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="action-buttons">
                        <a href="{{ race.race_url }}" target="_blank" rel="noopener" class="btn btn-primary">
                            📋 Racecard
                        </a>
                        {% if race.form_guide_url %}
                            <a href="{{ race.form_guide_url }}" target="_blank" rel="noopener" class="btn btn-secondary">
                                📊 Form
                            </a>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="empty-state">
                <div class="empty-state-icon">🎯</div>
                <p>No races found matching your criteria</p>
            </div>
        {% endif %}
    </div>
    
    <div id="value-races" class="tab-content">
        <h2>🔥 Premium Value Opportunities (Score 70+)</h2>
        {% if value_races %}
            {% for race in value_races %}
                <div class="race {{ race.discipline }} value-{% if race.value_score >= 90 %}extreme{% elif race.value_score >= 80 %}high{% elif race.value_score >= 70 %}good{% else %}decent{% endif %}" data-score="{{ race.value_score }}">
                    <div class="race-header">
                        <div class="course-name">{{ race.course }}</div>
                        <div class="discipline-icon">
                            {% if race.discipline == 'thoroughbred' %}🐎{% elif race.discipline == 'harness' %}🏇{% elif race.discipline == 'greyhound' %}🐕{% endif %}
                        </div>
                    </div>
                    
                    <div class="race-meta">
                        <span class="meta-pill">{{ race.country }}</span>
                        <span class="meta-pill">{{ race.local_time }} {{ race.timezone_name }}</span>
                        <span class="meta-pill value-score value-score-{% if race.value_score >= 90 %}90plus{% elif race.value_score >= 80 %}80plus{% elif race.value_score >= 70 %}70plus{% elif race.value_score >= 60 %}60plus{% endif %}">
                            {{ "%.0f"|format(race.value_score) }}★
                        </span>
                    </div>
                    
                    <div class="favorites-grid">
                        <div class="favorite-card">
                            <div class="favorite-name">🥇 {{ (race.favorite.name or 'Unknown') if race.favorite else 'N/A' }}</div>
                            <div class="favorite-odds">{{ (race.favorite.odds_str or 'SP') if race.favorite else '' }}</div>
                        </div>
                        <div class="favorite-card">
                            <div class="favorite-name">🥈 {{ (race.second_favorite.name or 'Unknown') if race.second_favorite else 'N/A' }}</div>
                            <div class="favorite-odds">{{ (race.second_favorite.odds_str or 'SP') if race.second_favorite else '' }}</div>
                        </div>
                    </div>
                    
                    <div class="race-details">
                        <div class="field-size">
                            <strong>Field:</strong> {{ race.field_size }} runners
                        </div>
                        <div class="sources">
                            {% for source in race.data_sources.values() | unique | sort %}
                                <span class="source-tag">{{ source.upper() }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="action-buttons">
                        <a href="{{ race.race_url }}" target="_blank" rel="noopener" class="btn btn-primary">
                            📋 Racecard
                        </a>
                        {% if race.form_guide_url %}
                            <a href="{{ race.form_guide_url }}" target="_blank" rel="noopener" class="btn btn-secondary">
                                📊 Form
                            </a>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="empty-state">
                <div class="empty-state-icon">🔥</div>
                <p>No high-value races found</p>
            </div>
        {% endif %}
    </div>
    
    <div id="all-races" class="tab-content">
        <h2>📋 Complete Race List (by Score)</h2>
        {% if all_races %}
            {% for race in all_races %}
                <div class="race {{ race.discipline }} value-{% if race.value_score >= 90 %}extreme{% elif race.value_score >= 80 %}high{% elif race.value_score >= 70 %}good{% else %}decent{% endif %}" data-score="{{ race.value_score }}">
                    <div class="race-header">
                        <div class="course-name">{{ race.course }}</div>
                        <div class="discipline-icon">
                            {% if race.discipline == 'thoroughbred' %}🐎{% elif race.discipline == 'harness' %}🏇{% elif race.discipline == 'greyhound' %}🐕{% endif %}
                        </div>
                    </div>
                    
                    <div class="race-meta">
                        <span class="meta-pill">{{ race.country }}</span>
                        <span class="meta-pill">{{ race.local_time }} {{ race.timezone_name }}</span>
                        <span class="meta-pill value-score value-score-{% if race.value_score >= 90 %}90plus{% elif race.value_score >= 80 %}80plus{% elif race.value_score >= 70 %}70plus{% elif race.value_score >= 60 %}60plus{% endif %}">
                            {{ "%.0f"|format(race.value_score) }}★
                        </span>
                    </div>
                    
                    <div class="favorites-grid">
                        <div class="favorite-card">
                            <div class="favorite-name">🥇 {{ (race.favorite.name or 'Unknown') if race.favorite else 'N/A' }}</div>
                            <div class="favorite-odds">{{ (race.favorite.odds_str or 'SP') if race.favorite else '' }}</div>
                        </div>
                        <div class="favorite-card">
                            <div class="favorite-name">🥈 {{ (race.second_favorite.name or 'Unknown') if race.second_favorite else 'N/A' }}</div>
                            <div class="favorite-odds">{{ (race.second_favorite.odds_str or 'SP') if race.second_favorite else '' }}</div>
                        </div>
                    </div>
                    
                    <div class="race-details">
                        <div class="field-size">
                            <strong>Field:</strong> {{ race.field_size }} runners
                        </div>
                        <div class="sources">
                            {% for source in race.data_sources.values() | unique | sort %}
                                <span class="source-tag">{{ source.upper() }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="action-buttons">
                        <a href="{{ race.race_url }}" target="_blank" rel="noopener" class="btn btn-primary">
                            📋 Racecard
                        </a>
                        {% if race.form_guide_url %}
                            <a href="{{ race.form_guide_url }}" target="_blank" rel="noopener" class="btn btn-secondary">
                                📊 Form
                            </a>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <p>No races found</p>
            </div>
        {% endif %}
    </div>
    
    <div class="footer">
        Generated {{ generated_at }} | Best of luck! 🍀
    </div>
</div>

<script>
    // Auto-refresh functionality
    let refreshInterval;
    let lastRefresh = Date.now();
    const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes
    
    function startAutoRefresh() {
        refreshInterval = setInterval(() => {
            refreshData();
        }, REFRESH_INTERVAL);
        
        document.getElementById('statusBar').classList.add('auto-refresh');
        updateStatusText('Auto-refresh enabled (every 5 minutes)');
    }
    
    function stopAutoRefresh() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
        document.getElementById('statusBar').classList.remove('auto-refresh');
        updateStatusText('Manual refresh only');
    }
    
    function refreshData() {
        const indicator = document.getElementById('refreshIndicator');
        indicator.style.animation = 'none';
        
        // Simulate refresh (in real implementation, this would fetch new data)
        setTimeout(() => {
            indicator.style.animation = 'pulse 2s infinite';
            lastRefresh = Date.now();
            updateStatusText('Data refreshed at ' + new Date().toLocaleTimeString());
        }, 1000);
    }
    
    function updateStatusText(text) {
        document.getElementById('statusText').innerHTML = text;
    }
    
    // Tab switching
    function showTab(tabName, element) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected tab content
        document.getElementById(tabName).classList.add('active');
        
        // Add active class to clicked tab
        element.classList.add('active');
    }
    
    // Touch gestures for pull-to-refresh
    let startY = 0;
    let currentY = 0;
    let pullDistance = 0;
    
    document.addEventListener('touchstart', (e) => {
        startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchmove', (e) => {
        currentY = e.touches[0].clientY;
        pullDistance = currentY - startY;
        
        if (pullDistance > 50 && window.scrollY === 0) {
            e.preventDefault();
            // Show pull indicator
        }
    });
    
    document.addEventListener('touchend', (e) => {
        if (pullDistance > 100 && window.scrollY === 0) {
            refreshData();
        }
        pullDistance = 0;
    });
    
    // Service Worker registration for PWA
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('sw.js')
                .then(registration => {
                    console.log('SW registered: ', registration);
                })
                .catch(registrationError => {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
    
    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        // Start auto-refresh after 30 seconds
        setTimeout(startAutoRefresh, 30000);
        
        // Add long press to refresh
        let pressTimer;
        const statusBar = document.getElementById('statusBar');
        
        statusBar.addEventListener('touchstart', () => {
            pressTimer = setTimeout(() => {
                refreshData();
            }, 1000);
        });
        
        statusBar.addEventListener('touchend', () => {
            clearTimeout(pressTimer);
        });
        
        statusBar.addEventListener('touchmove', () => {
            clearTimeout(pressTimer);
        });
    });
</script>
</body>
</html>
"""

# Override the HTML template
HTML_TEMPLATE = MOBILE_HTML_TEMPLATE

# Mobile-optimized output manager
class MobileOutputManager(OutputManager):
    def __init__(self, output_dir: Path):
        # Try to use mobile output directory if available
        mobile_dir = Path(CONFIG["OUTPUT"]["MOBILE_OUTPUT_DIR"])
        if mobile_dir.exists() and os.access(mobile_dir, os.W_OK):
            super().__init__(mobile_dir)
        else:
            super().__init__(output_dir)
    
    def write_html_report(self, races, stats, min_r, max_r):
        filename = self.out_dir / f"racing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        template = self.jinja_env.from_string(HTML_TEMPLATE)
        html = template.render(
            config=CONFIG, stats=stats, all_races=races,
            filtered_races=[r for r in races if min_r <= r.field_size <= max_r],
            value_races=[r for r in races if r.value_score >= 70],
            generated_at=datetime.now().isoformat(timespec="seconds"),
            min_runners=min_r, max_runners=max_r
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        logging.info(f"Mobile report saved to {filename}")
        return filename

# Import datetime for the mobile output manager
from datetime import datetime

# Main function for mobile
async def main_mobile_async(args):
    import logging
    import time
    from datetime import timedelta
    import asyncio
    
    logging.basicConfig(
        level=logging.INFO if not args.verbose else logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler('racing_scanner_mobile.log')]
    )
    
    start_time = time.time()
    cache = CacheManager(Path(CONFIG["DEFAULT_CACHE_DIR"]))
    http_client = AsyncHttpClient(cache, interactive_fallback=args.interactive)
    
    try:
        print(f"🚀 Starting {CONFIG['APP_NAME']} Mobile Edition v{CONFIG['SCHEMA_VERSION']}")
        print(f"📱 Mobile-optimized settings: {CONFIG['HTTP']['MAX_CONCURRENT_REQUESTS']} concurrent requests")
        print(f"📅 Scanning from {args.days_back} days back to {args.days_forward} days forward")
        
        aggregator = RacingDataAggregator(http_client)
        start_dt = datetime.now() + timedelta(days=args.days_back)
        end_dt = datetime.now() + timedelta(days=args.days_forward)
        
        races, stats = await aggregator.fetch_all_races(start_dt, end_dt)
        stats.duration_seconds = time.time() - start_time
        
        print(f"✅ Mobile scan completed in {stats.duration_seconds:.1f} seconds")
        print(f"📊 Found {stats.total_races_found} total races, {stats.races_after_dedup} unique")
        
        output_manager = MobileOutputManager(Path(CONFIG["DEFAULT_OUTPUT_DIR"]))
        
        if 'html' in args.formats:
            report_file = output_manager.write_html_report(races, stats, args.min_field_size, args.max_field_size)
            print(f"📱 Mobile report saved to: {report_file}")
        
        if 'json' in args.formats:
            output_manager.write_json_report(races, stats)
        
        if 'csv' in args.formats:
            output_manager.write_csv_report(races)
        
        high_value_races = [r for r in races if r.value_score >= 70]
        if high_value_races:
            print(f"\n🔥 {len(high_value_races)} high-value opportunities found (Top 5):")
            for race in high_value_races[:5]:
                fav_name = race.favorite.get('name', 'Unknown') if race.favorite else 'N/A'
                print(f"   {race.course} {race.local_time} - {race.field_size} runners - Score: {race.value_score:.0f} - Fav: {fav_name}")
        
        return report_file if 'html' in args.formats else None
        
    except KeyboardInterrupt:
        print("\n⏹️ Mobile scan interrupted by user")
    except Exception as e:
        logging.error(f"Critical error: {e}", exc_info=True)
        print(f"❌ Critical error occurred: {e}")
    finally:
        await http_client.close()

# Command line interface for mobile
def main_mobile():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description=f"{CONFIG['APP_NAME']} Mobile Edition v{CONFIG['SCHEMA_VERSION']}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Mobile Examples:
  python racing_scanner_mobile.py --days-forward 0       # Scan today only
  python racing_scanner_mobile.py --min-field-size 3 --max-field-size 6
  python racing_scanner_mobile.py --formats html json csv # Specify output formats
        """
    )
    
    parser.add_argument("--days-back", type=int, default=0, help="Days back to scan (e.g., -1 for yesterday)")
    parser.add_argument("--days-forward", type=int, default=1, help="Days forward to scan")
    parser.add_argument("--min-field-size", type=int, default=CONFIG["FILTERS"]["MIN_FIELD_SIZE"])
    parser.add_argument("--max-field-size", type=int, default=CONFIG["FILTERS"]["MAX_FIELD_SIZE"])
    parser.add_argument("--interactive", action="store_true", help="Enable interactive fallback for manual HTML input")
    parser.add_argument("--formats", nargs='+', default=['html'], help="Output formats (html, json, csv)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")
    
    args = parser.parse_args()
    
    try:
        report_file = asyncio.run(main_mobile_async(args))
        print("🎯 Mobile scan complete! Good luck with your bets! 🍀")
        if report_file:
            print(f"📱 Open the report in your mobile browser: {report_file}")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_mobile()