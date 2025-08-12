#!/usr/bin/env python3
"""
Utopian Value Scanner V7.1 (The Perfected Edition)

Enhanced version with comprehensive racing data sources, improved error handling,
and robust HTTP client implementation for scraping horse and dog racing sites.
"""

# =============================================================================
# CONFIGURATION SECTION - YOUR CONTROL PANEL
# =============================================================================

CONFIG = {
    # Application Settings
    "SCHEMA_VERSION": "7.1",
    "APP_NAME": "Utopian Value Scanner (Perfected Edition)",

    # Directory Settings
    "DEFAULT_CACHE_DIR": ".cache_v7_final",
    "DEFAULT_OUTPUT_DIR": "output",

    # HTTP Client Configuration
    "HTTP": {
        "REQUEST_TIMEOUT": 30.0,
        "MAX_CONCURRENT_REQUESTS": 8,
        "MAX_RETRIES": 3,
        "RETRY_BACKOFF_BASE": 2,
        "USER_AGENTS": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        ]
    },

    # Cache Configuration
    "CACHE": {
        "DEFAULT_TTL": 1800,      # 30 minutes for normal fetches
        "MANUAL_FETCH_TTL": 21600, # 6 hours for hard-to-get manual fetches
        "ENABLED": True
    },

    # Data Sources (All available sources enabled for maximum coverage)
    "SOURCES": {
        "AtTheRaces": {
            "enabled": True, 
            "base_url": "https://www.attheraces.com", 
            "regions": ["uk", "ireland", "usa", "france", "saf", "aus"]
        },
        "SkySports": {
            "enabled": True, 
            "base_url": "https://www.skysports.com/racing/racecards"
        },
        "SportingLife": {
            "enabled": True, 
            "base_url": "https://www.sportinglife.com",
            "greyhound_url": "https://www.sportinglife.com/greyhound"
        },
        "RacingPost": {
            "enabled": True,
            "base_url": "https://www.racingpost.com"
        },
        "HarnessAustralia": {
            "enabled": True, 
            "base_url": "https://www.harness.org.au"
        },
        "StandardbredCanada": {
            "enabled": True, 
            "base_url": "https://standardbredcanada.ca"
        },
    },

    # Command-line Argument Defaults
    "FILTERS": {
        "MIN_FIELD_SIZE": 4,
        "MAX_FIELD_SIZE": 8,
    },

    # Output Configuration
    "OUTPUT": {
        "AUTO_OPEN_BROWSER": True
    },

    # Timezone Mappings
    "TIMEZONES": {
        "TRACKS": {
            # UK & Ireland
            "ayr": "Europe/London", "kempton-park": "Europe/London", "windsor": "Europe/London", 
            "ascot": "Europe/London", "cheltenham": "Europe/London", "newmarket": "Europe/London",
            "leopardstown": "Europe/Dublin", "curragh": "Europe/Dublin", "ballinrobe": "Europe/Dublin",
            "romford": "Europe/London", "crayford": "Europe/London", "belle-vue": "Europe/London",
            
            # USA
            "finger-lakes": "America/New_York", "fort-erie": "America/Toronto", 
            "presque-isle-downs": "America/New_York", "ellis-park": "America/Chicago", 
            "thistledown": "America/New_York", "mountaineer-park": "America/New_York", 
            "mountaineer": "America/New_York", "churchill": "America/New_York", 
            "belmont": "America/New_York", "saratoga": "America/New_York", 
            "santa-anita": "America/Los_Angeles", "del-mar": "America/Los_Angeles",
            
            # France
            "la-teste-de-buch": "Europe/Paris", "clairefontaine": "Europe/Paris", 
            "cagnes-sur-mer-midi": "Europe/Paris", "divonne-les-bains": "Europe/Paris", 
            "longchamp": "Europe/Paris", "saint-malo": "Europe/Paris",
            
            # Australia
            "flemington": "Australia/Melbourne", "randwick": "Australia/Sydney", 
            "eagle-farm": "Australia/Brisbane", "albion-park": "Australia/Brisbane", 
            "redcliffe": "Australia/Brisbane", "menangle": "Australia/Sydney", 
            "gloucester-park": "Australia/Perth", "wentworth-park": "Australia/Sydney",
            
            # Other
            "fairview": "Africa/Johannesburg", "gavea": "America/Sao_Paulo", 
            "sha-tin": "Asia/Hong_Kong", "tokyo": "Asia/Tokyo"
        },
        "COUNTRIES": {
            "GB": "Europe/London", "IE": "Europe/Dublin", "US": "America/New_York", 
            "FR": "Europe/Paris", "AU": "Australia/Sydney", "NZ": "Pacific/Auckland", 
            "HK": "Asia/Hong_Kong", "JP": "Asia/Tokyo", "ZA": "Africa/Johannesburg", 
            "CA": "America/Toronto", "BR": "America/Sao_Paulo"
        }
    }
}

# =============================================================================
# ENHANCED HTML TEMPLATE
# =============================================================================

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ config.APP_NAME }} - Racing Value Scanner</title>
    <style>
        :root{color-scheme:light dark}
        body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background-color:#f4f4f9;color:#333;margin:0;padding:20px;line-height:1.6}
        .container{max-width:1400px;margin:auto;background-color:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.05)}
        .race.value-extreme { border-left: 8px solid #ff4444; background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%); }
        .race.value-high { border-left: 6px solid #ff8800; background: linear-gradient(135deg, #fff8f0 0%, #ffeecc 100%); }
        .race.value-good { border-left: 4px solid #00aa00; background: linear-gradient(135deg, #f0fff0 0%, #e6ffe6 100%); }
        .race.value-decent { border-left: 3px solid #0088cc; background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%); }
        .odds-evens-plus { background: linear-gradient(45deg, #ff6b6b, #feca57); color: white; font-weight: bold; padding: 4px 8px; border-radius: 6px; box-shadow: 0 2px 4px rgba(255,107,107,0.3); animation: pulse 2s infinite; }
        .odds-short-good { background: #48cae4; color: white; padding: 3px 6px; border-radius: 4px; font-weight: 600; }
        .odds-longshot { background: #6c757d; color: white; padding: 2px 5px; border-radius: 3px; }
        @keyframes pulse { 0% { box-shadow: 0 2px 4px rgba(255,107,107,0.3); } 50% { box-shadow: 0 4px 8px rgba(255,107,107,0.6); } 100% { box-shadow: 0 2px 4px rgba(255,107,107,0.3); } }
        h1{color:#1a1a1a;border-bottom:3px solid #007bff;padding-bottom:10px}
        .summary{background:#e7f3ff;padding:15px;border-radius:8px;margin-bottom:20px;border-left:4px solid #007bff}
        .tabs{display:flex;border-bottom:2px solid #dee2e6;margin-bottom:20px;flex-wrap:wrap}
        .tab{padding:10px 20px;cursor:pointer;background:#f8f9fa;border:1px solid #dee2e6;border-bottom:none;margin-right:2px;border-radius:4px 4px 0 0;white-space:nowrap}
        .tab.active{background:#007bff;color:white;border-color:#007bff}
        .tab-content{display:none}.tab-content.active{display:block}
        .race{border:1px solid #ddd;padding:15px;margin:10px 0;border-radius:8px;position:relative}
        .race.thoroughbred::before{content:"🐎";position:absolute;top:10px;right:15px;font-size:1.5em}
        .race.harness::before{content:"🏇";position:absolute;top:10px;right:15px;font-size:1.5em}
        .race.greyhound::before{content:"🐕";position:absolute;top:10px;right:15px;font-size:1.5em}
        .head{display:flex;flex-wrap:wrap;align-items:center;gap:15px;font-weight:600;font-size:1.2em;margin-bottom:10px}
        .pill{display:inline-block;padding:4px 12px;border-radius:12px;background:#e9ecef;color:#495057;font-size:.9rem;font-weight:500}
        .value-score-pill{font-weight:bold;font-size:1rem}
        .value-score-90plus{background:#ff4444;color:white}
        .value-score-80plus{background:#ff8800;color:white}
        .value-score-70plus{background:#00aa00;color:white}
        .value-score-60plus{background:#0088cc;color:white}
        .favorites-row{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin:12px 0;padding:12px;background:#f8f9fa;border-radius:6px}
        .favorite-info{text-align:center}
        .favorite-name{font-weight:bold;margin-bottom:5px}
        .favorite-odds{font-size:1.1em}
        .links a{display:inline-block;text-decoration:none;background-color:#007bff;color:white;padding:8px 15px;border-radius:4px;margin-right:10px;font-size:.9em;margin-top:8px}
        .links a.alt{background:#28a745}
        .links a:hover{transform:translateY(-1px);box-shadow:0 2px 4px rgba(0,0,0,0.2)}
        .runner-count{font-size:0.9em;color:#666;margin-top:8px}
        .data-sources{margin-top:8px}
        .source-pill{background:#6c757d;color:white;padding:2px 6px;border-radius:3px;font-size:0.8em;margin-right:5px}
        @media (max-width: 768px) { .favorites-row{grid-template-columns:1fr;gap:10px} .head{font-size:1.1em} }
        @media (prefers-color-scheme:dark){
            body{background-color:#121212;color:#e0e0e0} .container{background-color:#1e1e1e} h1{color:#e0e0e0;border-color:#4dabf7}
            .summary{background-color:#2c3e50;border-left-color:#4dabf7} .tabs{border-color:#444}
            .tab{background:#333;color:#ccc;border-color:#444} .tab.active{background:#4dabf7;color:#000;border-color:#4dabf7}
            .race{background-color:#2a2a2a;border-color:#444} .favorites-row{background:#333} .pill{background:#333;color:#ccc}
            .links a{background-color:#4dabf7;color:#000} .links a.alt{background:#2ecc71}
            .race.value-extreme { background: linear-gradient(135deg, #4d1a1a 0%, #3d1111 100%); }
            .race.value-high { background: linear-gradient(135deg, #4d331a 0%, #3d2211 100%); }
            .race.value-good { background: linear-gradient(135deg, #1a4d1a 0%, #113d11 100%); }
            .race.value-decent { background: linear-gradient(135deg, #1a334d 0%, #11223d 100%); }
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🎯 {{ config.APP_NAME }}</h1>
    <div class="summary">
        <strong>📊 SCAN RESULTS:</strong> 
        Found <b>{{ stats.total_races_found }}</b> raw races from <b>{{ stats.per_source_counts | length }}</b> sources. 
        <b>{{ stats.races_after_dedup }}</b> unique after merging. 
        <b>{{ value_races | length }}</b> high-value races identified.
        ⏱️ Runtime: <b>{{ "%.1f"|format(stats.duration_seconds) }}s</b>
    </div>
    <div class="tabs">
        <div class="tab active" onclick="showTab('filtered-races', this)">🎯 Superfecta Fields ({{ filtered_races | length }})</div>
        <div class="tab" onclick="showTab('value-races', this)">🔥 High Value ({{ value_races | length }})</div>
        <div class="tab" onclick="showTab('all-races', this)">📋 All Races ({{ all_races | length }})</div>
    </div>
    {% macro render_race(race) %}
    <div class="race {{ race.discipline }}" data-score="{{ race.value_score }}">
        <div class="head">
            <span style="font-size:1.3em">{{ race.course }}</span>
            <span class="pill">{{ race.country }}</span>
            <span class="pill">{{ race.local_time }} {{ race.timezone_name }}</span>
            <span class="pill value-score-pill {% if race.value_score >= 90 %}value-score-90plus{% elif race.value_score >= 80 %}value-score-80plus{% elif race.value_score >= 70 %}value-score-70plus{% elif race.value_score >= 60 %}value-score-60plus{% endif %}">
                {{ "%.0f"|format(race.value_score) }}★
            </span>
        </div>
        <div class="favorites-row">
            <div class="favorite-info"><div class="favorite-name">🥇 {{ (race.favorite.name or 'Unknown') if race.favorite else 'N/A' }}</div><div class="favorite-odds">{{ (race.favorite.odds_str or 'SP') if race.favorite else '' }}</div></div>
            <div class="favorite-info"><div class="favorite-name">🥈 {{ (race.second_favorite.name or 'Unknown') if race.second_favorite else 'N/A' }}</div><div class="favorite-odds">{{ (race.second_favorite.odds_str or 'SP') if race.second_favorite else '' }}</div></div>
        </div>
        <div class="runner-count"><strong>Field:</strong> {{ race.field_size }} runners</div>
        <div class="data-sources"><strong>Sources:</strong>{% for source in race.data_sources.values() | unique | sort %}<span class="source-pill">{{ source.upper() }}</span>{% endfor %}</div>
        <div class="links"><a href="{{ race.race_url }}" target="_blank" rel="noopener">📋 Racecard</a>{% if race.form_guide_url %}<a class="alt" href="{{ race.form_guide_url }}" target="_blank" rel="noopener">📊 Form</a>{% endif %}</div>
    </div>
    {% endmacro %}
    <div id="filtered-races" class="tab-content active"><h2>🎯 Superfecta Fields ({{ min_runners }}-{{ max_runners }} Runners)</h2>{% for race in filtered_races %}{{ render_race(race) }}{% endfor %}</div>
    <div id="value-races" class="tab-content"><h2>🔥 Premium Value Opportunities (Score 70+)</h2>{% for race in value_races %}{{ render_race(race) }}{% endfor %}</div>
    <div id="all-races" class="tab-content"><h2>📋 Complete Race List (by Score)</h2>{% for race in all_races %}{{ render_race(race) }}{% endfor %}</div>
    <div style="text-align:center;margin-top:30px;font-size:.9em;color:#777">Generated {{ generated_at }} | Best of luck! 🍀</div>
</div>
<script>
    function showTab(tabName, element){
        document.querySelectorAll(".tab-content").forEach(c=>c.classList.remove("active"));
        document.querySelectorAll(".tab").forEach(c=>c.classList.remove("active"));
        document.getElementById(tabName).classList.add("active");
        element.classList.add("active");
    }
    function convertOddsToFractional(oddsStr) {
        if (!oddsStr || typeof oddsStr !== 'string') return 999;
        const s = oddsStr.trim().toUpperCase();
        if (s === 'SP' || s === 'NR') return 999;
        if (s === 'EVS' || s === 'EVENS') return 1.0;
        if (s.includes('/')) { const parts = s.split('/'); const num = parseFloat(parts[0]); const den = parseFloat(parts[1]); return den > 0 ? num / den : 999; }
        const decimal = parseFloat(s);
        return !isNaN(decimal) && decimal > 1 ? decimal - 1 : 999;
    }
    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll('.race').forEach(race => {
            const score = parseFloat(race.dataset.score || 0);
            if (score >= 90) race.classList.add('value-extreme');
            else if (score >= 80) race.classList.add('value-high');
            else if (score >= 70) race.classList.add('value-good');
            else if (score >= 60) race.classList.add('value-decent');
        });
        document.querySelectorAll('.favorite-odds').forEach(el => {
            const odds = convertOddsToFractional(el.textContent);
            if (odds >= 1.0 && odds <= 2.5) el.classList.add('odds-evens-plus');
            else if (odds < 1.0) el.classList.add('odds-short-good');
            else el.classList.add('odds-longshot');
        });
    });
</script>
</body>
</html>
"""

# =============================================================================
# IMPORTS AND SETUP
# =============================================================================

import asyncio
import argparse
import json
import logging
import os
import re
import hashlib
import random
import sys
import time
import webbrowser
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from urllib.parse import urlparse, urljoin

# Handle timezone imports
try:
    from zoneinfo import ZoneInfo
except ImportError:
    try:
        from backports.zoneinfo import ZoneInfo
    except ImportError:
        print("Error: zoneinfo is not available. Please run: pip install backports.zoneinfo", file=sys.stderr)
        sys.exit(1)

# Handle Jinja2 import
JINJA2_AVAILABLE = False
try:
    from jinja2 import Environment
    JINJA2_AVAILABLE = True
except ImportError:
    print("Warning: Jinja2 is not installed. HTML reports will be basic. Please run: pip install Jinja2", file=sys.stderr)

# Required imports
try:
    import httpx
    import aiofiles
    from bs4 import BeautifulSoup, Tag
except ImportError as e:
    print(f"Error: Required package not installed: {e}", file=sys.stderr)
    print("Please run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# Optional curl-cffi import with fallback
try:
    from curl_cffi.requests import AsyncSession as CurlCffiSession
    CURL_CFFI_AVAILABLE = True
except ImportError:
    print("Warning: curl-cffi not available. Using httpx only.", file=sys.stderr)
    CURL_CFFI_AVAILABLE = False

# =============================================================================
# DATA CLASSES AND CORE MODELS
# =============================================================================

@dataclass
class SourceError:
    source_name: str
    error_message: str
    error_type: str
    timestamp: datetime
    url: Optional[str] = None

@dataclass
class RaceData:
    id: str
    course: str
    race_time: str
    utc_datetime: datetime
    local_time: str
    timezone_name: str
    field_size: int
    country: str
    discipline: str
    race_url: str = ""
    form_guide_url: Optional[str] = None
    favorite: Optional[Dict[str, Any]] = None
    second_favorite: Optional[Dict[str, Any]] = None
    all_runners: List[Dict[str, Any]] = field(default_factory=list)
    value_score: float = 0.0
    data_sources: Dict[str, str] = field(default_factory=dict)

@dataclass
class ScanStatistics:
    total_races_found: int = 0
    races_after_dedup: int = 0
    duration_seconds: float = 0.0
    per_source_counts: Dict[str, int] = field(default_factory=dict)
    source_errors: List[SourceError] = field(default_factory=list)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def normalize_course_name(name: str) -> str:
    """Normalize course name for consistent comparison"""
    if not name: return ""
    # Remove parenthetical content and normalize
    normalized = re.sub(r'\s*\([^)]*\)', '', name.lower().strip())
    # Replace common variations
    replacements = {
        'park': '', 'raceway': '', 'racecourse': '', 'track': '',
        'stadium': '', 'greyhound': '', 'harness': ''
    }
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized.strip()

def get_track_timezone(course: str, country: str) -> str:
    """Get timezone for a track based on course name and country"""
    norm_course = normalize_course_name(course).replace(" ", "-")
    return CONFIG["TIMEZONES"]["TRACKS"].get(
        norm_course, 
        CONFIG["TIMEZONES"]["COUNTRIES"].get(country.upper(), "UTC")
    )

def generate_race_id(course: str, date: str, time: str) -> str:
    """Generate unique race ID from course, date, and time"""
    key = f"{normalize_course_name(course)}|{date}|{re.sub(r'[^\d]', '', time or '')}"
    return hashlib.sha1(key.encode()).hexdigest()[:12]

def convert_odds_to_fractional(odds_str: str) -> float:
    """Convert odds string to fractional decimal for comparison"""
    if not isinstance(odds_str, str) or not odds_str.strip(): 
        return 999.0
    
    s = odds_str.strip().upper().replace("-", "/")
    
    # Handle special cases
    if s in {"SP", "NR", "VOID", "WD"}: 
        return 999.0
    if s in {"EVS", "EVENS"}: 
        return 1.0
    
    # Handle fractional odds (e.g., "3/1", "9/4")
    if "/" in s:
        try:
            parts = s.split("/", 1)
            num, den = float(parts[0]), float(parts[1])
            return num / den if den > 0 else 999.0
        except (ValueError, ZeroDivisionError): 
            return 999.0
    
    # Handle decimal odds (e.g., "2.5", "4.0")
    try:
        dec = float(s)
        return dec - 1.0 if dec > 1 else 999.0
    except ValueError: 
        return 999.0

def is_probable_block_page(html: str) -> bool:
    """Check if HTML content appears to be a bot blocking page"""
    if not html or len(html) < 200: 
        return False
    
    h = html.lower()
    block_signals = [
        "just a moment...", "attention required! | cloudflare", 
        "check your browser", "access denied", "incapsula", 
        "unusual traffic", "verify you are a human", 
        "cf-chl-bypass", "cf-ray", "turn on javascript",
        "security check", "please wait", "ddos protection"
    ]
    return any(signal in h for signal in block_signals)

def parse_local_hhmm(time_text: str) -> Optional[str]:
    """Extract HH:MM time from text"""
    if not time_text: 
        return None
    
    # Look for time patterns
    match = re.search(r"\b(\d{1,2}):(\d{2})\s*([AaPp][Mm])?\b", time_text)
    if not match: 
        return None
    
    h, mm, ap = match.groups()
    hour = int(h)
    
    # Handle AM/PM
    if ap:
        ap = ap.upper()
        if ap == "PM" and hour != 12: 
            hour += 12
        elif ap == "AM" and hour == 12: 
            hour = 0
    
    return f"{hour:02d}:{mm}"

def extract_meta_refresh_target(html: str) -> Optional[str]:
    """Extract redirect URL from meta refresh tag"""
    match = re.search(
        r'http-equiv=["\']?refresh["\']?[^>]*content=["\']?\s*\d+\s*;\s*url=([^"\'>\s]+)', 
        html, re.I
    )
    return match.group(1).strip() if match else None

# =============================================================================
# CACHE AND HTTP CLIENT
# =============================================================================

class CacheManager:
    """Manages local file cache for HTTP responses"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True, parents=True)

    def _get_cache_path(self, url: str) -> Path:
        """Get cache file path for URL"""
        url_hash = hashlib.sha1(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.html"

    async def get(self, url: str) -> Optional[str]:
        """Get cached content for URL if valid"""
        if not CONFIG["CACHE"]["ENABLED"]: 
            return None
        
        path = self._get_cache_path(url)
        if not path.exists(): 
            return None
        
        try:
            # Check if cache is expired
            cache_age = datetime.now().timestamp() - path.stat().st_mtime
            if cache_age > CONFIG["CACHE"]["DEFAULT_TTL"]:
                path.unlink()
                return None
            
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                return await f.read()
        except Exception as e:
            logging.debug(f"Cache read error for {url}: {e}")
            return None

    async def set(self, url: str, content: str, ttl: Optional[int] = None):
        """Cache content for URL"""
        if not CONFIG["CACHE"]["ENABLED"]: 
            return
        
        try:
            path = self._get_cache_path(url)
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(content)
        except Exception as e:
            logging.debug(f"Cache write error for {url}: {e}")

class EnhancedHttpClient:
    """Enhanced HTTP client with multiple fetching strategies"""
    
    def __init__(self, cache: CacheManager, interactive_fallback: bool = False):
        self.cache = cache
        self.interactive_fallback = interactive_fallback
        self.semaphore = asyncio.Semaphore(CONFIG["HTTP"]["MAX_CONCURRENT_REQUESTS"])
        self.user_agent = random.choice(CONFIG["HTTP"]["USER_AGENTS"])
        self._httpx_client: Optional[httpx.AsyncClient] = None
        self._host_last_request: Dict[str, float] = {}
        self._throttle_lock = asyncio.Lock()

    async def _get_httpx_client(self) -> httpx.AsyncClient:
        """Get or create httpx client"""
        if self._httpx_client is None:
            self._httpx_client = httpx.AsyncClient(
                timeout=CONFIG["HTTP"]["REQUEST_TIMEOUT"],
                follow_redirects=True,
                http2=True,
                headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
        return self._httpx_client

    async def close(self):
        """Close HTTP client"""
        if self._httpx_client:
            await self._httpx_client.aclose()

    async def _throttle_request(self, url: str):
        """Throttle requests to avoid overwhelming servers"""
        try:
            host = urlparse(url).netloc
        except Exception:
            return
        
        async with self._throttle_lock:
            now = time.perf_counter()
            last_request = self._host_last_request.get(host, 0.0)
            wait_time = 0.5 - (now - last_request)  # 500ms between requests to same host
            
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            self._host_last_request[host] = time.perf_counter()

    def _prompt_for_manual_input(self, url: str) -> Optional[str]:
        """Interactive fallback to get content manually"""
        print("\n" + "="*80, file=sys.stderr)
        print("🛑 FETCH FAILED: MANUAL INTERVENTION REQUIRED", file=sys.stderr)
        print(f"🔗 URL: {url}", file=sys.stderr)
        print("\nINSTRUCTIONS:", file=sys.stderr)
        print("1. Open the URL above in a web browser.", file=sys.stderr)
        print("2. View the page source (usually Ctrl+U or right-click -> View Page Source).", file=sys.stderr)
        print("3. Select all (Ctrl+A) and copy (Ctrl+C).", file=sys.stderr)
        print("4. Paste the HTML content here in the terminal.", file=sys.stderr)
        print("5. Press Enter, then signal End-of-File:", file=sys.stderr)
        print("   - On Windows: Ctrl+Z then Enter", file=sys.stderr)
        print("   - On Linux/macOS: Ctrl+D", file=sys.stderr)
        print("   (Or, to skip this URL, just signal End-of-File on an empty line)", file=sys.stderr)
        print("="*80, file=sys.stderr)
        
        try:
            content = sys.stdin.read().strip()
            if content:
                print("✅ HTML received, continuing scan...", file=sys.stderr)
                return content
            else:
                print("⏩ Skipped.", file=sys.stderr)
                return None
        except KeyboardInterrupt:
            print("⏩ Skipped due to interrupt.", file=sys.stderr)
            return None

    async def _fetch_with_httpx(self, url: str) -> Optional[str]:
        """Fetch using httpx"""
        try:
            client = await self._get_httpx_client()
            headers = {"User-Agent": self.user_agent}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.debug(f"httpx fetch failed for {url}: {e}")
            return None

    async def _fetch_with_curl_cffi(self, url: str) -> Optional[str]:
        """Fetch using curl-cffi if available"""
        if not CURL_CFFI_AVAILABLE:
            return None
        
        try:
            async with CurlCffiSession(impersonate="chrome120") as session:
                headers = {
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Referer": "https://www.google.com/"
                }
                response = await session.get(url, timeout=CONFIG["HTTP"]["REQUEST_TIMEOUT"], headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logging.debug(f"curl-cffi fetch failed for {url}: {e}")
            return None

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch URL with multiple strategies and caching"""
        # Try cache first
        cached = await self.cache.get(url)
        if cached and not is_probable_block_page(cached):
            return cached
        
        async with self.semaphore:
            await self._throttle_request(url)
            
            # Try multiple fetch strategies
            for attempt in range(CONFIG["HTTP"]["MAX_RETRIES"]):
                # Try curl-cffi first (better for bypassing blocks)
                content = await self._fetch_with_curl_cffi(url)
                if content and not is_probable_block_page(content):
                    await self.cache.set(url, content)
                    return content
                
                # Try httpx as fallback
                content = await self._fetch_with_httpx(url)
                if content and not is_probable_block_page(content):
                    # Handle meta refresh redirects
                    if redirect_url := extract_meta_refresh_target(content):
                        try:
                            next_url = urljoin(url, redirect_url)
                            client = await self._get_httpx_client()
                            response = await client.get(next_url, headers={"User-Agent": self.user_agent})
                            content = response.text
                        except Exception:
                            pass  # Use original content
                    
                    await self.cache.set(url, content)
                    return content
                
                # Wait before retry
                if attempt < CONFIG["HTTP"]["MAX_RETRIES"] - 1:
                    wait_time = CONFIG["HTTP"]["RETRY_BACKOFF_BASE"] ** attempt
                    await asyncio.sleep(wait_time)
            
            # Interactive fallback if enabled
            if self.interactive_fallback:
                manual_content = await asyncio.to_thread(self._prompt_for_manual_input, url)
                if manual_content:
                    await self.cache.set(url, manual_content, ttl=CONFIG["CACHE"]["MANUAL_FETCH_TTL"])
                    return manual_content

        logging.warning(f"All fetch methods failed for {url}")
        return None

# =============================================================================
# ENHANCED VALUE SCORER
# =============================================================================

class EnhancedValueScorer:
    """Advanced scoring algorithm for race value assessment"""
    
    def __init__(self):
        self.weights = {
            "FIELD_SIZE_WEIGHT": 0.35,
            "FAVORITE_ODDS_WEIGHT": 0.45,
            "ODDS_SPREAD_WEIGHT": 0.15,
            "DATA_QUALITY_WEIGHT": 0.05
        }

    def calculate_score(self, race: RaceData) -> float:
        """Calculate comprehensive value score for a race"""
        # Base score calculation
        field_score = self._calculate_field_score(race.field_size)
        fav_score = self._calculate_favorite_odds_score(race.favorite)
        spread_score = self._calculate_odds_spread_score(race.favorite, race.second_favorite)
        quality_score = self._calculate_data_quality_score(race)
        
        base_score = (
            field_score * self.weights["FIELD_SIZE_WEIGHT"] +
            fav_score * self.weights["FAVORITE_ODDS_WEIGHT"] +
            spread_score * self.weights["ODDS_SPREAD_WEIGHT"] +
            quality_score * self.weights["DATA_QUALITY_WEIGHT"]
        )
        
        # Apply multipliers
        multiplier = 1.0
        
        # Bonus for live odds data
        if self._has_live_odds(race):
            multiplier *= 1.2
        
        # Bonus for greyhound racing (typically more predictable)
        if race.discipline == "greyhound":
            multiplier *= 1.1
        
        # Bonus for small fields with good odds spread
        if race.field_size <= 6 and spread_score > 80:
            multiplier *= 1.15
        
        final_score = base_score * multiplier
        return min(100.0, max(0.0, final_score))

    def _calculate_field_score(self, size: int) -> float:
        """Score based on field size (smaller is better for value)"""
        if 3 <= size <= 5:
            return 100.0
        elif 6 <= size <= 8:
            return 85.0
        elif 9 <= size <= 12:
            return 60.0
        elif size <= 2:
            return 30.0  # Too small, limited betting options
        else:
            return 20.0  # Too large, harder to predict

    def _calculate_favorite_odds_score(self, favorite: Optional[Dict]) -> float:
        """Score based on favorite's odds (evens money is ideal)"""
        if not favorite:
            return 0.0
        
        odds = convert_odds_to_fractional(favorite.get("odds_str", ""))
        
        if odds == 999.0:  # No odds available
            return 30.0
        
        # Sweet spot for favorites
        if 1.0 <= odds <= 1.5:  # Evens to 3/2
            return 100.0
        elif 1.5 < odds <= 2.5:  # 3/2 to 5/2
            return 90.0
        elif 2.5 < odds <= 4.0:  # 5/2 to 4/1
            return 75.0
        elif 0.5 <= odds < 1.0:  # Short odds but still reasonable
            return 85.0
        elif odds < 0.5:  # Very short odds
            return 60.0
        else:  # Long odds favorite (risky)
            return 40.0

    def _calculate_odds_spread_score(self, favorite: Optional[Dict], second_favorite: Optional[Dict]) -> float:
        """Score based on odds difference between top two"""
        if not favorite or not second_favorite:
            return 50.0
        
        fav_odds = convert_odds_to_fractional(favorite.get("odds_str", ""))
        sec_odds = convert_odds_to_fractional(second_favorite.get("odds_str", ""))
        
        if fav_odds == 999.0 or sec_odds == 999.0:
            return 50.0
        
        spread = sec_odds - fav_odds
        
        # Good spread indicates clear favorite
        if spread >= 2.0:
            return 100.0
        elif spread >= 1.5:
            return 90.0
        elif spread >= 1.0:
            return 80.0
        elif spread >= 0.5:
            return 60.0
        else:
            return 40.0  # Too close, harder to predict

    def _calculate_data_quality_score(self, race: RaceData) -> float:
        """Score based on data completeness and quality"""
        score = 0.0
        
        # Has odds data
        if race.all_runners and any(r.get("odds_str") for r in race.all_runners):
            score += 40.0
        
        # Has both favorites identified
        if race.favorite and race.second_favorite:
            score += 30.0
        
        # Has form guide URL
        if race.form_guide_url:
            score += 20.0
        
        # Multiple data sources
        if len(race.data_sources) > 1:
            score += 10.0
        
        return min(100.0, score)

    def _has_live_odds(self, race: RaceData) -> bool:
        """Check if race has live odds (not just SP)"""
        if not race.all_runners:
            return False
        
        return any(
            r.get("odds_str") and r.get("odds_str") not in ["", "SP", "NR", "VOID"]
            for r in race.all_runners
        )

# =============================================================================
# DATA SOURCE CLASSES
# =============================================================================

class DataSourceBase:
    """Base class for all data sources"""
    
    def __init__(self, http_client: EnhancedHttpClient):
        self.http_client = http_client
        self.name = self.__class__.__name__.replace("Source", "")
        self.source_errors: List[SourceError] = []

    def _generate_date_range(self, date_range: Tuple[datetime, datetime]):
        """Generate dates within the specified range"""
        current_date, end_date = date_range[0].date(), date_range[1].date()
        while current_date <= end_date:
            yield datetime.combine(current_date, datetime.min.time())
            current_date += timedelta(days=1)

    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        """Fetch races for the given date range - to be implemented by subclasses"""
        raise NotImplementedError

    def _add_error(self, message: str, url: Optional[str] = None, error_type: str = "ParsingError"):
        """Add error to the source error list"""
        error = SourceError(
            source_name=self.name,
            error_message=message,
            error_type=error_type,
            timestamp=datetime.now(),
            url=url
        )
        self.source_errors.append(error)
        logging.debug(f"{self.name} Error: {message} at URL: {url}")

class SkySportsSource(DataSourceBase):
    """Sky Sports racing data source"""
    
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        races: List[RaceData] = []
        base_url = CONFIG["SOURCES"]["SkySports"]["base_url"]
        
        for dt in self._generate_date_range(date_range):
            # Use today's URL format or date-specific format
            if dt.date() == datetime.now().date():
                url = base_url
            else:
                url = f"{base_url}/{dt.strftime('%d-%m-%Y')}"
            
            html = await self.http_client.fetch(url)
            if not html:
                continue
            
            try:
                races.extend(await self._parse_sky_sports_page(html, url, dt))
            except Exception as e:
                self._add_error(f"Failed to parse Sky Sports page: {e}", url=url)
        
        return races

    async def _parse_sky_sports_page(self, html: str, base_url: str, date: datetime) -> List[RaceData]:
        """Parse Sky Sports racing page"""
        races = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find race meeting containers
        meeting_containers = soup.find_all('div', class_='sdc-site-racing-meetings__event')
        
        for container in meeting_containers:
            try:
                # Get race URL
                link = container.find('a', class_='sdc-site-racing-meetings__event-link')
                if not link or not link.get('href'):
                    continue
                
                race_url = urljoin(base_url, link['href'])
                
                # Get race details
                details = container.find('span', class_='sdc-site-racing-meetings__event-details')
                if not details:
                    continue
                
                details_text = details.get_text(strip=True)
                
                # Extract field size
                runners_match = re.search(r'(\d+)\s+runners?', details_text, re.I)
                if not runners_match:
                    continue
                field_size = int(runners_match.group(1))
                
                # Extract race time
                time_str = parse_local_hhmm(details_text)
                if not time_str:
                    continue
                
                # Extract course name from URL
                try:
                    path_parts = urlparse(race_url).path.strip('/').split('/')
                    racecards_idx = path_parts.index('racecards')
                    course_slug = path_parts[racecards_idx + 1]
                    course_name = course_slug.replace('-', ' ').title()
                except (ValueError, IndexError):
                    course_name = "Unknown Course"
                
                # Extract country
                country_match = re.search(r'\(([^)]+)\)', details_text)
                country = country_match.group(1) if country_match else "GB"
                
                # Set timezone and create datetime
                tz_name = get_track_timezone(course_name, country)
                local_dt = datetime.combine(
                    date.date(), 
                    datetime.strptime(time_str, "%H:%M").time()
                ).replace(tzinfo=ZoneInfo(tz_name))

                race = RaceData(
                    id=generate_race_id(course_name, date.strftime("%Y-%m-%d"), time_str),
                    course=course_name,
                    race_time=time_str,
                    utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                    local_time=local_dt.strftime("%H:%M"),
                    timezone_name=tz_name,
                    field_size=field_size,
                    country=country,
                    discipline="thoroughbred",
                    race_url=race_url,
                    data_sources={"course": "SkySports"}
                )
                
                races.append(race)
                
            except Exception as e:
                self._add_error(f"Error parsing Sky Sports race container: {e}")
                continue
        
        return races

class AtTheRacesSource(DataSourceBase):
    """At The Races data source with odds"""
    
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        races = []
        
        for dt in self._generate_date_range(date_range):
            for region in CONFIG["SOURCES"]["AtTheRaces"]["regions"]:
                url = f"{CONFIG['SOURCES']['AtTheRaces']['base_url']}/ajax/marketmovers/tabs/{region}/{dt.strftime('%Y%m%d')}"
                
                try:
                    region_races = await self._parse_atr_region(url, region, dt.date())
                    races.extend(region_races)
                except Exception as e:
                    self._add_error(f"Failed to parse ATR region {region}: {e}", url=url)
        
        return races

    async def _parse_atr_region(self, url: str, region: str, date: datetime.date) -> List[RaceData]:
        """Parse At The Races region page"""
        html = await self.http_client.fetch(url)
        if not html:
            return []
        
        races = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find time captions (race times)
        time_captions = soup.find_all('caption', string=re.compile(r'^\d{2}:\d{2}'))
        
        for caption in time_captions:
            try:
                race_time = caption.get_text(strip=True).split()[0]
                
                # Find the panel containing this race
                panel = caption.find_parent('div', class_=re.compile(r'\bpanel\b'))
                if not panel:
                    continue
                
                # Find course heading
                course_heading = panel.find('h2')
                if not course_heading:
                    course_heading = caption.find_previous('h2')
                if not course_heading:
                    continue
                
                course_name = course_heading.get_text(strip=True)
                
                # Find runners table
                table = caption.find_next_sibling('table')
                if not table:
                    continue
                
                # Parse runners and odds
                runners = []
                tbody = table.find('tbody') or table
                
                for row in tbody.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2 and cells[0].get_text(strip=True):
                        runner_name = cells[0].get_text(strip=True)
                        odds_str = cells[1].get_text(strip=True)
                        runners.append({
                            'name': runner_name,
                            'odds_str': odds_str
                        })
                
                if not runners:
                    continue
                
                # Sort runners by odds (favorites first)
                sorted_runners = sorted(
                    runners, 
                    key=lambda x: convert_odds_to_fractional(x.get('odds_str', ''))
                )
                
                # Map region to country
                country_map = {
                    'uk': 'GB', 'ireland': 'IE', 'usa': 'US', 
                    'france': 'FR', 'saf': 'ZA', 'aus': 'AU'
                }
                country = country_map.get(region, 'GB')
                
                # Set timezone and create datetime
                tz_name = get_track_timezone(course_name, country)
                local_dt = datetime.combine(
                    date, 
                    datetime.strptime(race_time, "%H:%M").time()
                ).replace(tzinfo=ZoneInfo(tz_name))

                race = RaceData(
                    id=generate_race_id(course_name, date.strftime("%Y-%m-%d"), race_time),
                    course=course_name,
                    race_time=race_time,
                    utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                    local_time=local_dt.strftime("%H:%M"),
                    timezone_name=tz_name,
                    field_size=len(runners),
                    country=country,
                    discipline="thoroughbred",
                    race_url=f"{CONFIG['SOURCES']['AtTheRaces']['base_url']}/racecard/{normalize_course_name(course_name).replace(' ', '-')}/{date.strftime('%Y-%m-%d')}/{race_time.replace(':', '')}",
                    all_runners=runners,
                    favorite=sorted_runners[0] if sorted_runners else None,
                    second_favorite=sorted_runners[1] if len(sorted_runners) > 1 else None,
                    data_sources={"course": "ATR", "runners": "ATR", "odds": "ATR"}
                )
                
                races.append(race)
                
            except Exception as e:
                self._add_error(f"Error parsing ATR caption: {e}")
                continue
        
        return races

class SportingLifeGreyhoundSource(DataSourceBase):
    """Sporting Life greyhound racing source"""
    
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        races = []
        base_url = CONFIG["SOURCES"]["SportingLife"]["greyhound_url"]
        
        for dt in self._generate_date_range(date_range):
            url = f"{base_url}/racecards/{dt.strftime('%Y-%m-%d')}"
            
            try:
                day_races = await self._parse_greyhound_day(url, dt.date())
                races.extend(day_races)
            except Exception as e:
                self._add_error(f"Failed to parse Sporting Life greyhounds: {e}", url=url)
        
        return races

    async def _parse_greyhound_day(self, url: str, date: datetime.date) -> List[RaceData]:
        """Parse Sporting Life greyhound racing page"""
        html = await self.http_client.fetch(url)
        if not html:
            return []
        
        races = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find race cards
        race_cards = soup.find_all('div', class_=re.compile(r'racecard|meeting'))
        
        for card in race_cards:
            try:
                # Extract track name
                track_elem = card.find(['h2', 'h3'], class_=re.compile(r'track|venue|meeting'))
                if not track_elem:
                    continue
                
                track_name = track_elem.get_text(strip=True)
                
                # Find individual races
                race_elements = card.find_all('div', class_=re.compile(r'race-time|race-info'))
                
                for race_elem in race_elements:
                    # Extract race time
                    time_elem = race_elem.find(string=re.compile(r'\d{2}:\d{2}'))
                    if not time_elem:
                        continue
                    
                    race_time = time_elem.strip()
                    
                    # Count runners (look for trap numbers or runner names)
                    runners = race_elem.find_all(['div', 'span'], class_=re.compile(r'runner|trap|dog'))
                    field_size = len(runners) if runners else 6  # Default greyhound field
                    
                    # Create race data
                    tz_name = get_track_timezone(track_name, "GB")
                    local_dt = datetime.combine(
                        date, 
                        datetime.strptime(race_time, "%H:%M").time()
                    ).replace(tzinfo=ZoneInfo(tz_name))

                    race = RaceData(
                        id=generate_race_id(track_name, date.strftime("%Y-%m-%d"), race_time),
                        course=track_name,
                        race_time=race_time,
                        utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                        local_time=local_dt.strftime("%H:%M"),
                        timezone_name=tz_name,
                        field_size=field_size,
                        country="GB",
                        discipline="greyhound",
                        race_url=url,
                        data_sources={"course": "SportingLife"}
                    )
                    
                    races.append(race)
                    
            except Exception as e:
                self._add_error(f"Error parsing greyhound race card: {e}")
                continue
        
        return races

class RacingPostSource(DataSourceBase):
    """Racing Post data source"""
    
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        races = []
        base_url = CONFIG["SOURCES"]["RacingPost"]["base_url"]
        
        for dt in self._generate_date_range(date_range):
            url = f"{base_url}/racecards/{dt.strftime('%Y-%m-%d')}"
            
            try:
                day_races = await self._parse_racing_post_day(url, dt.date())
                races.extend(day_races)
            except Exception as e:
                self._add_error(f"Failed to parse Racing Post: {e}", url=url)
        
        return races

    async def _parse_racing_post_day(self, url: str, date: datetime.date) -> List[RaceData]:
        """Parse Racing Post racing page"""
        html = await self.http_client.fetch(url)
        if not html:
            return []
        
        races = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find meeting containers
        meetings = soup.find_all('div', class_=re.compile(r'meeting|racecard'))
        
        for meeting in meetings:
            try:
                # Extract course name
                course_elem = meeting.find(['h1', 'h2', 'h3'], class_=re.compile(r'course|venue'))
                if not course_elem:
                    continue
                
                course_name = course_elem.get_text(strip=True)
                
                # Find races
                race_elements = meeting.find_all('div', class_=re.compile(r'race-time|race-info'))
                
                for race_elem in race_elements:
                    # Extract time
                    time_text = race_elem.get_text()
                    race_time = parse_local_hhmm(time_text)
                    if not race_time:
                        continue
                    
                    # Extract field size
                    runners_match = re.search(r'(\d+)\s+runners?', time_text, re.I)
                    field_size = int(runners_match.group(1)) if runners_match else 0
                    
                    if field_size == 0:
                        continue
                    
                    # Determine discipline and country
                    discipline = "thoroughbred"
                    country = "GB"
                    
                    if "greyhound" in time_text.lower() or "dog" in time_text.lower():
                        discipline = "greyhound"
                    elif "harness" in time_text.lower() or "trot" in time_text.lower():
                        discipline = "harness"
                    
                    # Set timezone
                    tz_name = get_track_timezone(course_name, country)
                    local_dt = datetime.combine(
                        date, 
                        datetime.strptime(race_time, "%H:%M").time()
                    ).replace(tzinfo=ZoneInfo(tz_name))

                    race = RaceData(
                        id=generate_race_id(course_name, date.strftime("%Y-%m-%d"), race_time),
                        course=course_name,
                        race_time=race_time,
                        utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                        local_time=local_dt.strftime("%H:%M"),
                        timezone_name=tz_name,
                        field_size=field_size,
                        country=country,
                        discipline=discipline,
                        race_url=url,
                        data_sources={"course": "RacingPost"}
                    )
                    
                    races.append(race)
                    
            except Exception as e:
                self._add_error(f"Error parsing Racing Post meeting: {e}")
                continue
        
        return races

# =============================================================================
# CORE LOGIC
# =============================================================================

class RacingDataAggregator:
    """Main class for aggregating racing data from multiple sources"""
    
    def __init__(self, http_client: EnhancedHttpClient):
        self.http_client = http_client
        self.scorer = EnhancedValueScorer()
        self.sources = self._initialize_sources()

    def _initialize_sources(self) -> List[DataSourceBase]:
        """Initialize enabled data sources"""
        sources = []
        
        source_classes = {
            "SkySports": SkySportsSource,
            "AtTheRaces": AtTheRacesSource,
            "SportingLife": SportingLifeGreyhoundSource,
            "RacingPost": RacingPostSource,
        }
        
        for name, config in CONFIG["SOURCES"].items():
            if config.get("enabled") and name in source_classes:
                try:
                    source_instance = source_classes[name](self.http_client)
                    sources.append(source_instance)
                    logging.info(f"Initialized {name} source")
                except Exception as e:
                    logging.error(f"Failed to initialize {name} source: {e}")
        
        return sources

    async def fetch_all_races(self, start_dt: datetime, end_dt: datetime) -> Tuple[List[RaceData], ScanStatistics]:
        """Fetch races from all sources and compile statistics"""
        stats = ScanStatistics()
        
        # Create tasks for all sources
        tasks = [
            self._fetch_from_source(source, start_dt, end_dt)
            for source in self.sources
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_races = []
        for i, result in enumerate(results):
            source = self.sources[i]
            
            if isinstance(result, Exception):
                error = SourceError(
                    source_name=source.name,
                    error_message=str(result),
                    error_type=type(result).__name__,
                    timestamp=datetime.now()
                )
                stats.source_errors.append(error)
                logging.error(f"Source {source.name} failed: {result}")
            else:
                races, source_errors = result
                stats.per_source_counts[source.name] = len(races)
                stats.source_errors.extend(source_errors)
                all_races.extend(races)
                logging.info(f"Source {source.name} returned {len(races)} races")
        
        stats.total_races_found = len(all_races)
        
        # Deduplicate races
        deduped_races = self._deduplicate_races(all_races)
        stats.races_after_dedup = len(deduped_races)
        
        # Calculate value scores
        for race in deduped_races:
            race.value_score = self.scorer.calculate_score(race)
        
        # Sort by value score (highest first)
        sorted_races = sorted(deduped_races, key=lambda r: r.value_score, reverse=True)
        
        return sorted_races, stats

    async def _fetch_from_source(self, source: DataSourceBase, start_dt: datetime, end_dt: datetime) -> Tuple[List[RaceData], List[SourceError]]:
        """Fetch races from a single source"""
        try:
            races = await source.fetch_races((start_dt, end_dt))
            return races, source.source_errors
        except Exception as e:
            logging.error(f"Error fetching from {source.name}: {e}")
            return [], [SourceError(
                source_name=source.name,
                error_message=str(e),
                error_type=type(e).__name__,
                timestamp=datetime.now()
            )]

    def _deduplicate_races(self, races: List[RaceData]) -> List[RaceData]:
        """Remove duplicate races, keeping the one with most complete data"""
        unique_races = {}
        
        for race in races:
            existing = unique_races.get(race.id)
            
            if existing is None:
                unique_races[race.id] = race
            else:
                # Keep the race with more complete data
                if self._is_more_complete(race, existing):
                    # Merge data sources
                    race.data_sources.update(existing.data_sources)
                    unique_races[race.id] = race
                else:
                    # Merge data sources into existing
                    existing.data_sources.update(race.data_sources)
        
        return list(unique_races.values())

    def _is_more_complete(self, race1: RaceData, race2: RaceData) -> bool:
        """Determine which race has more complete data"""
        score1 = self._completeness_score(race1)
        score2 = self._completeness_score(race2)
        return score1 > score2

    def _completeness_score(self, race: RaceData) -> int:
        """Calculate completeness score for a race"""
        score = 0
        
        if race.all_runners:
            score += len(race.all_runners) * 2
        if race.favorite:
            score += 5
        if race.second_favorite:
            score += 3
        if race.form_guide_url:
            score += 2
        if len(race.data_sources) > 1:
            score += 3
        
        return score

class OutputManager:
    """Handles output generation and file management"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize Jinja2 environment if available
        if JINJA2_AVAILABLE:
            self.jinja_env = Environment()
            self.jinja_env.filters['unique'] = lambda x: list(set(x)) if x else []
        else:
            self.jinja_env = None

    def write_html_report(self, races: List[RaceData], stats: ScanStatistics, min_runners: int, max_runners: int):
        """Generate and write HTML report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"racing_report_{timestamp}.html"
        
        try:
            if self.jinja_env:
                template = self.jinja_env.from_string(HTML_TEMPLATE)
                html_content = template.render(
                    config=CONFIG,
                    stats=stats,
                    all_races=races,
                    filtered_races=[r for r in races if min_runners <= r.field_size <= max_runners],
                    value_races=[r for r in races if r.value_score >= 70],
                    generated_at=datetime.now().isoformat(timespec="seconds"),
                    min_runners=min_runners,
                    max_runners=max_runners
                )
            else:
                # Fallback simple HTML
                html_content = self._generate_simple_html(races, stats, min_runners, max_runners)
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logging.info(f"Report saved to {filename}")
            print(f"📊 Report generated: {filename}")
            
            # Auto-open in browser if configured
            if CONFIG["OUTPUT"]["AUTO_OPEN_BROWSER"]:
                try:
                    webbrowser.open(f"file://{os.path.abspath(filename)}")
                except Exception as e:
                    logging.debug(f"Failed to open browser: {e}")
            
        except Exception as e:
            logging.error(f"Failed to write HTML report: {e}")
            print(f"❌ Error generating report: {e}")

    def _generate_simple_html(self, races: List[RaceData], stats: ScanStatistics, min_runners: int, max_runners: int) -> str:
        """Generate simple HTML when Jinja2 is not available"""
        filtered_races = [r for r in races if min_runners <= r.field_size <= max_runners]
        value_races = [r for r in races if r.value_score >= 70]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{CONFIG['APP_NAME']} - Racing Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .race {{ border: 1px solid #ccc; margin: 10px 0; padding: 15px; }}
                .high-value {{ border-left: 5px solid #ff6600; }}
                h1 {{ color: #333; }}
                .stats {{ background: #f0f0f0; padding: 10px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>{CONFIG['APP_NAME']}</h1>
            <div class="stats">
                <strong>Scan Results:</strong> Found {stats.total_races_found} races, 
                {len(value_races)} high-value opportunities identified.
            </div>
            <h2>High Value Races (Score 70+)</h2>
        """
        
        for race in value_races:
            fav_name = race.favorite.get('name', 'Unknown') if race.favorite else 'N/A'
            fav_odds = race.favorite.get('odds_str', 'SP') if race.favorite else ''
            
            html += f"""
            <div class="race high-value">
                <h3>{race.course} - {race.local_time}</h3>
                <p><strong>Field:</strong> {race.field_size} runners</p>
                <p><strong>Favorite:</strong> {fav_name} ({fav_odds})</p>
                <p><strong>Value Score:</strong> {race.value_score:.0f}</p>
                <p><strong>Country:</strong> {race.country}</p>
                <p><a href="{race.race_url}" target="_blank">View Racecard</a></p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html

    def write_json_report(self, races: List[RaceData], stats: ScanStatistics) -> Path:
        """Write JSON report for programmatic access"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"racing_data_{timestamp}.json"
        
        try:
            # Convert to serializable format
            races_data = []
            for race in races:
                race_dict = asdict(race)
                # Convert datetime objects to ISO strings
                race_dict['utc_datetime'] = race.utc_datetime.isoformat()
                races_data.append(race_dict)
            
            stats_data = asdict(stats)
            # Convert datetime objects in errors
            for error in stats_data['source_errors']:
                error['timestamp'] = error['timestamp'].isoformat()
            
            output_data = {
                'generated_at': datetime.now().isoformat(),
                'config_version': CONFIG['SCHEMA_VERSION'],
                'statistics': stats_data,
                'races': races_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"JSON data saved to {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"Failed to write JSON report: {e}")
            raise

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main_async(args: argparse.Namespace):
    """Main async execution function"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('racing_scanner.log')
        ]
    )
    
    start_time = time.time()
    
    # Initialize components
    cache = CacheManager(Path(CONFIG["DEFAULT_CACHE_DIR"]))
    http_client = EnhancedHttpClient(cache, interactive_fallback=args.interactive)
    
    try:
        print(f"🚀 Starting {CONFIG['APP_NAME']} v{CONFIG['SCHEMA_VERSION']}")
        print(f"📅 Scanning from {args.days_back} days back to {args.days_forward} days forward")
        print(f"🏁 Field size filter: {args.min_field_size}-{args.max_field_size} runners")
        
        aggregator = RacingDataAggregator(http_client)
        
        # Calculate date range
        start_dt = datetime.now() + timedelta(days=args.days_back)
        end_dt = datetime.now() + timedelta(days=args.days_forward)
        
        print(f"🔍 Fetching races from {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}")
        
        # Fetch all races
        races, stats = await aggregator.fetch_all_races(start_dt, end_dt)
        stats.duration_seconds = time.time() - start_time
        
        print(f"✅ Scan completed in {stats.duration_seconds:.1f} seconds")
        print(f"📊 Found {stats.total_races_found} total races, {stats.races_after_dedup} unique")
        
        # Generate output
        output_manager = OutputManager(Path(CONFIG["DEFAULT_OUTPUT_DIR"]))
        output_manager.write_html_report(races, stats, args.min_field_size, args.max_field_size)
        
        if args.json_output:
            json_file = output_manager.write_json_report(races, stats)
            print(f"📄 JSON data saved to {json_file}")
        
        # Print summary of high-value races
        high_value_races = [r for r in races if r.value_score >= 70]
        if high_value_races:
            print(f"\n🔥 {len(high_value_races)} high-value opportunities found:")
            for race in high_value_races[:5]:  # Show top 5
                fav_name = race.favorite.get('name', 'Unknown') if race.favorite else 'N/A'
                print(f"   {race.course} {race.local_time} - {race.field_size} runners - Score: {race.value_score:.0f} - Fav: {fav_name}")
        else:
            print("\n📊 No high-value opportunities found in current scan")
        
    except KeyboardInterrupt:
        print("\n⏹️ Scan interrupted by user")
    except Exception as e:
        logging.error(f"Critical error: {e}", exc_info=True)
        print(f"❌ Critical error occurred: {e}")
    finally:
        await http_client.close()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description=f"{CONFIG['APP_NAME']} v{CONFIG['SCHEMA_VERSION']}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python racing_scanner.py                    # Scan today and tomorrow
  python racing_scanner.py --days-back -1    # Include yesterday
  python racing_scanner.py --days-forward 3  # Scan next 3 days
  python racing_scanner.py --min-field-size 3 --max-field-size 6  # Small fields only
  python racing_scanner.py --interactive     # Enable manual HTML input fallback
        """
    )
    
    parser.add_argument(
        "--days-back", 
        type=int, 
        default=0, 
        help="Days back to scan (e.g., -1 for yesterday)"
    )
    parser.add_argument(
        "--days-forward", 
        type=int, 
        default=1, 
        help="Days forward to scan (e.g., 2 for day after tomorrow)"
    )
    parser.add_argument(
        "--min-field-size", 
        type=int, 
        default=CONFIG["FILTERS"]["MIN_FIELD_SIZE"],
        help="Minimum number of runners to include in filtered results"
    )
    parser.add_argument(
        "--max-field-size", 
        type=int, 
        default=CONFIG["FILTERS"]["MAX_FIELD_SIZE"],
        help="Maximum number of runners to include in filtered results"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Enable interactive fallback for manual HTML input"
    )
    parser.add_argument(
        "--json-output", 
        action="store_true",
        help="Also generate JSON output file"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        asyncio.run(main_async(args))
        print("🎯 Scan complete! Good luck with your bets! 🍀")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()