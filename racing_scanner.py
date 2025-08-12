#!/usr/bin/env python3
"""
Utopian Value Scanner V7.2 (The Polished Diamond Edition)

This definitive version merges the comprehensive, multi-discipline data sources 
with a superior value scoring algorithm, more intelligent data merging, and an
enhanced user experience, representing the best of all previous versions.
"""

# =============================================================================
# CONFIGURATION SECTION - YOUR CONTROL PANEL
# =============================================================================

CONFIG = {
    # Application Settings
    "SCHEMA_VERSION": "7.2",
    "APP_NAME": "Utopian Value Scanner (Polished Diamond)",

    # Directory Settings
    "DEFAULT_CACHE_DIR": ".cache_v7_final",
    "DEFAULT_OUTPUT_DIR": "output",

    # HTTP Client Configuration
    "HTTP": {
        "REQUEST_TIMEOUT": 30.0,
        "MAX_CONCURRENT_REQUESTS": 12,
        "MAX_RETRIES": 3,
        "RETRY_BACKOFF_BASE": 2,
        "USER_AGENTS": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        ]
    },

    # Cache Configuration
    "CACHE": {
        "DEFAULT_TTL": 1800,      # 30 minutes for normal fetches
        "MANUAL_FETCH_TTL": 21600, # 6 hours for hard-to-get manual fetches
        "ENABLED": True
    },

    # Data Sources (All sources enabled for maximum coverage)
    "SOURCES": {
        "RacingAndSports": {"enabled": True, "base_url": "https://www.racingandsports.com.au"},
        "SportingLifeHorseApi": {"enabled": True, "base_url": "https://www.sportinglife.com/api/horse-racing/race"},
        "RacingPost": {"enabled": True, "base_url": "https://www.racingpost.com"},
        "SkySports": {"enabled": True, "base_url": "https://www.skysports.com/racing/racecards"},
        "AtTheRaces": {"enabled": True, "base_url": "https://www.attheraces.com", "regions": ["uk", "ireland", "usa", "france", "saf", "aus"]},
        "GBGreyhounds": {"enabled": True, "base_url": "https://www.sportinglife.com"},
        "HarnessAustralia": {"enabled": True, "base_url": "https://www.harness.org.au"},
        "StandardbredCanada": {"enabled": True, "base_url": "https://standardbredcanada.ca"},
    },

    # Command-line Argument Defaults
    "FILTERS": {
        "MIN_FIELD_SIZE": 4,
        "MAX_FIELD_SIZE": 6,
    },

    # Output Configuration
    "OUTPUT": {
        "AUTO_OPEN_BROWSER": True
    },

    # Timezone Mappings
    "TIMEZONES": {
        "TRACKS": {
            "ayr": "Europe/London", "kempton-park": "Europe/London", "windsor": "Europe/London", "ascot": "Europe/London", "cheltenham": "Europe/London", "newmarket": "Europe/London", "leopardstown": "Europe/Dublin", "curragh": "Europe/Dublin", "ballinrobe": "Europe/Dublin",
            "finger-lakes": "America/New_York", "fort-erie": "America/Toronto", "presque-isle-downs": "America/New_York", "ellis-park": "America/Chicago", "thistledown": "America/New_York", "mountaineer-park": "America/New_York", "mountaineer": "America/New_York", "churchill": "America/New_York", "belmont": "America/New_York", "saratoga": "America/New_York", "santa-anita": "America/Los_Angeles", "del-mar": "America/Los_Angeles",
            "la-teste-de-buch": "Europe/Paris", "clairefontaine": "Europe/Paris", "cagnes-sur-mer-midi": "Europe/Paris", "divonne-les-bains": "Europe/Paris", "longchamp": "Europe/Paris", "saint-malo": "Europe/Paris",
            "flemington": "Australia/Melbourne", "randwick": "Australia/Sydney", "eagle-farm": "Australia/Brisbane", "albion-park": "Australia/Brisbane", "redcliffe": "Australia/Brisbane", "menangle": "Australia/Sydney", "gloucester-park": "Australia/Perth",
            "fairview": "Africa/Johannesburg",
            "gavea": "America/Sao_Paulo", "sha-tin": "Asia/Hong_Kong", "tokyo": "Asia/Tokyo"
        },
        "COUNTRIES": {
            "GB": "Europe/London", "IE": "Europe/Dublin", "US": "America/New_York", "FR": "Europe/Paris", "AU": "Australia/Sydney", "NZ": "Pacific/Auckland", "HK": "Asia/Hong_Kong", "JP": "Asia/Tokyo", "ZA": "Africa/Johannesburg", "CA": "America/Toronto", "BR": "America/Sao_Paulo"
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
import csv
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, urljoin

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

try:
    from jinja2 import Environment
except ImportError:
    print("Error: Jinja2 is not installed. Please run: pip install Jinja2", file=sys.stderr)
    sys.exit(1)

import aiofiles
from bs4 import BeautifulSoup, Tag
from curl_cffi.requests import AsyncSession as CurlCffiSession
import httpx

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
    """Aggressively normalize course name for consistent comparison."""
    if not name: return ""
    normalized = re.sub(r'\s*\([^)]*\)', '', name.lower().strip())
    replacements = {'park': '', 'raceway': '', 'racecourse': '', 'track': '', 'stadium': '', 'greyhound': '', 'harness': ''}
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return " ".join(normalized.split())

def get_track_timezone(course: str, country: str) -> str:
    norm_course = normalize_course_name(course).replace(" ", "-")
    return CONFIG["TIMEZONES"]["TRACKS"].get(norm_course, CONFIG["TIMEZONES"]["COUNTRIES"].get(country.upper(), "UTC"))

def generate_race_id(course: str, date: str, time: str) -> str:
    key = f"{normalize_course_name(course)}|{date}|{re.sub(r'[^\d]', '', time or '')}"
    return hashlib.sha1(key.encode()).hexdigest()[:12]

def convert_odds_to_fractional(odds_str: str) -> float:
    if not isinstance(odds_str, str) or not odds_str.strip(): return 999.0
    s = odds_str.strip().upper().replace("-", "/")
    if s in {"SP", "NR"}: return 999.0
    if s in {"EVS", "EVENS"}: return 1.0
    if "/" in s:
        try:
            num, den = map(float, s.split("/", 1))
            return num / den if den > 0 else 999.0
        except (ValueError, ZeroDivisionError): return 999.0
    try:
        dec = float(s)
        return dec - 1.0 if dec > 1 else 999.0
    except ValueError: return 999.0

def is_probable_block_page(html: str) -> bool:
    if not html or len(html) < 200: return False
    h = html.lower()
    signals = ["just a moment...", "attention required! | cloudflare", "check your browser", "access denied", "incapsula", "unusual traffic", "verify you are a human", "cf-chl-bypass", "cf-ray", "turn on javascript"]
    return any(s in h for s in signals)

def parse_local_hhmm(time_text: str) -> Optional[str]:
    if not time_text: return None
    match = re.search(r"\b(\d{1,2}):(\d{2})\s*([AaPp][Mm])?\b", time_text)
    if not match: return None
    h, mm, ap = match.groups()
    hour = int(h)
    if (ap or "").upper() == "PM" and hour != 12: hour += 12
    if (ap or "").upper() == "AM" and hour == 12: hour = 0
    return f"{hour:02d}:{mm}"

def _extract_meta_refresh_target(html: str) -> Optional[str]:
    m = re.search(r'http-equiv=["\']?refresh["\']?[^>]*content=["\']?\s*\d+\s*;\s*url=([^"\'>\s]+)', html, re.I)
    return m.group(1).strip() if m else None

# =============================================================================
# CACHE AND HTTP CLIENT
# =============================================================================

class CacheManager:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True, parents=True)

    def _path(self, url: str) -> Path:
        return self.cache_dir / f"{hashlib.sha1(url.encode()).hexdigest()}.html"

    async def get(self, url: str) -> Optional[str]:
        if not CONFIG["CACHE"]["ENABLED"]: return None
        path = self._path(url)
        if not path.exists(): return None
        try:
            if (datetime.now().timestamp() - path.stat().st_mtime) > CONFIG["CACHE"]["DEFAULT_TTL"]:
                path.unlink()
                return None
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                return await f.read()
        except Exception: return None

    async def set(self, url: str, content: str, ttl: Optional[int] = None):
        if not CONFIG["CACHE"]["ENABLED"]: return
        path = self._path(url)
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(content)

class AsyncHttpClient:
    def __init__(self, cache: CacheManager, interactive_fallback: bool):
        self.cache = cache
        self.interactive_fallback = interactive_fallback
        self.semaphore = asyncio.Semaphore(CONFIG["HTTP"]["MAX_CONCURRENT_REQUESTS"])
        self.user_agent = random.choice(CONFIG["HTTP"]["USER_AGENTS"])
        self._client: Optional[httpx.AsyncClient] = None
        self._host_last: Dict[str, float] = {}
        self._throttle_lock = asyncio.Lock()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=CONFIG["HTTP"]["REQUEST_TIMEOUT"], follow_redirects=True, http2=True)
        return self._client

    async def aclose(self):
        if self._client: await self._client.aclose()

    def _prompt_for_manual_input(self, url: str) -> Optional[str]:
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
        print("="*80, file=sys.stderr)
        content = sys.stdin.read().strip()
        if content: print("✅ HTML received, continuing scan...", file=sys.stderr); return content
        else: print("⏩ Skipped.", file=sys.stderr); return None

    async def _throttle(self, url: str):
        try: host = urlparse(url).netloc
        except Exception: return
        async with self._throttle_lock:
            now = time.perf_counter()
            last = self._host_last.get(host, 0.0)
            wait = 0.25 - (now - last)
            if wait > 0: await asyncio.sleep(wait)
            self._host_last[host] = time.perf_counter()

    async def fetch(self, url: str) -> Optional[str]:
        cached = await self.cache.get(url)
        if cached and not is_probable_block_page(cached): return cached
        
        async with self.semaphore:
            await self._throttle(url)
            content = None
            for attempt in range(CONFIG["HTTP"]["MAX_RETRIES"]):
                try:
                    async with CurlCffiSession(impersonate="chrome120") as session:
                        headers = {"User-Agent": self.user_agent, "Referer": "https://www.google.com/"}
                        response = await session.get(url, timeout=CONFIG["HTTP"]["REQUEST_TIMEOUT"], headers=headers)
                        response.raise_for_status()
                        content = response.text
                        if not is_probable_block_page(content):
                            if new_target := _extract_meta_refresh_target(content):
                                client = await self._get_client()
                                next_url = urljoin(url, new_target)
                                response = await client.get(next_url, headers={"User-Agent": self.user_agent})
                                content = response.text
                            await self.cache.set(url, content)
                            return content
                        else:
                            logging.debug(f"Block page detected for {url}, retrying...")
                            await asyncio.sleep(CONFIG["HTTP"]["RETRY_BACKOFF_BASE"] ** attempt)
                except Exception as e:
                    logging.debug(f"Fetch failed for {url} (attempt {attempt+1}): {e}")
                    await asyncio.sleep(CONFIG["HTTP"]["RETRY_BACKOFF_BASE"] ** attempt)
            
            if self.interactive_fallback:
                if manual_content := await asyncio.to_thread(self._prompt_for_manual_input, url):
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
        self.weights = {"FIELD_SIZE_WEIGHT": 0.35, "FAVORITE_ODDS_WEIGHT": 0.45, "ODDS_SPREAD_WEIGHT": 0.15, "DATA_QUALITY_WEIGHT": 0.05}

    def calculate_score(self, race: RaceData) -> float:
        base_score = (self._calculate_field_score(race.field_size) * self.weights["FIELD_SIZE_WEIGHT"] +
                      self._calculate_favorite_odds_score(race.favorite) * self.weights["FAVORITE_ODDS_WEIGHT"] +
                      self._calculate_odds_spread_score(race.favorite, race.second_favorite) * self.weights["ODDS_SPREAD_WEIGHT"] +
                      self._calculate_data_quality_score(race) * self.weights["DATA_QUALITY_WEIGHT"])
        
        multiplier = 1.0
        if self._has_live_odds(race): multiplier *= 1.2
        if race.discipline == "greyhound": multiplier *= 1.1
        if race.field_size <= 6 and self._calculate_odds_spread_score(race.favorite, race.second_favorite) > 80: multiplier *= 1.15
        
        final_score = base_score * multiplier
        return min(100.0, max(0.0, final_score))

    def _calculate_field_score(self, size: int) -> float:
        if 3 <= size <= 5: return 100.0
        elif 6 <= size <= 8: return 85.0
        elif 9 <= size <= 12: return 60.0
        else: return 20.0

    def _calculate_favorite_odds_score(self, favorite: Optional[Dict]) -> float:
        if not favorite: return 0.0
        odds = convert_odds_to_fractional(favorite.get("odds_str", ""))
        if odds == 999.0: return 30.0
        if 1.0 <= odds <= 1.5: return 100.0
        elif 1.5 < odds <= 2.5: return 90.0
        elif 2.5 < odds <= 4.0: return 75.0
        elif 0.5 <= odds < 1.0: return 85.0
        elif odds < 0.5: return 60.0
        else: return 40.0

    def _calculate_odds_spread_score(self, favorite: Optional[Dict], second_favorite: Optional[Dict]) -> float:
        if not favorite or not second_favorite: return 50.0
        fav_odds = convert_odds_to_fractional(favorite.get("odds_str", ""))
        sec_odds = convert_odds_to_fractional(second_favorite.get("odds_str", ""))
        if fav_odds == 999.0 or sec_odds == 999.0: return 50.0
        spread = sec_odds - fav_odds
        if spread >= 2.0: return 100.0
        elif spread >= 1.5: return 90.0
        elif spread >= 1.0: return 80.0
        elif spread >= 0.5: return 60.0
        else: return 40.0

    def _calculate_data_quality_score(self, race: RaceData) -> float:
        score = 0.0
        if race.all_runners and any(r.get("odds_str") for r in race.all_runners): score += 40.0
        if race.favorite and race.second_favorite: score += 30.0
        if race.form_guide_url: score += 20.0
        if len(race.data_sources) > 1: score += 10.0
        return min(100.0, score)

    def _has_live_odds(self, race: RaceData) -> bool:
        return any(r.get("odds_str") and r.get("odds_str") not in ["", "SP", "NR", "VOID"] for r in race.all_runners)

# =============================================================================
# DATA SOURCE CLASSES
# =============================================================================

class DataSourceBase:
    """Base class for all data sources"""
    
    def __init__(self, http_client: AsyncHttpClient):
        self.http_client = http_client
        self.name = self.__class__.__name__.replace("Source", "")
        self.source_errors: List[SourceError] = []

    def _days(self, date_range: Tuple[datetime, datetime]):
        """Generate dates within the specified range"""
        cur, end = date_range[0].date(), date_range[1].date()
        while cur <= end: yield datetime.combine(cur, datetime.min.time()); cur += timedelta(days=1)

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

class RacingAndSportsSource(DataSourceBase):
    """
    Primary data source using the R&S JSON feed for a high-coverage, multi-discipline
    backbone of global race data.
    """
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        out: List[RaceData] = []
        today = datetime.now().date()
        # This API is for "today's racing", so we only hit it if today is in the requested range
        if not (date_range[0].date() <= today <= date_range[1].date()):
            return []

        url = f"{CONFIG['SOURCES']['RacingAndSports']['base_url']}/todays-racing-json-v2"
        json_text = await self.http_client.fetch(url)
        if not json_text:
            self._add_error("Failed to fetch the main JSON feed.", url=url)
            return []

        try:
            payload = json.loads(json_text)
            for discipline_group in payload or []:
                discipline_name = (discipline_group.get("Discipline") or "").lower()
                discipline = "greyhound" if "greyhound" in discipline_name else "harness" if "harness" in discipline_name else "thoroughbred"
                
                for country_group in discipline_group.get("Countries", []):
                    country_code = country_group.get("Code", "N/A").upper()
                    for meeting in country_group.get("Meetings", []):
                        course = (meeting.get("Course") or "").strip()
                        if not course: continue
                        
                        meeting_url = meeting.get("PreMeetingUrl") or meeting.get("Url")
                        form_url = meeting.get("PDFUrl")

                        for race_item in meeting.get("Races", []):
                            race_time = parse_local_hhmm(race_item.get("RaceTimeLocal"))
                            if not race_time: continue

                            date_str = today.strftime("%Y-%m-%d")
                            tz_name = get_track_timezone(course, country_code)
                            
                            try:
                                local_dt = datetime.combine(today, datetime.strptime(race_time, "%H:%M").time()).replace(tzinfo=ZoneInfo(tz_name))
                            except Exception:
                                self._add_error(f"Could not parse timezone '{tz_name}' for {course}")
                                continue

                            race_url = race_item.get("Url") or meeting_url

                            out.append(RaceData(
                                id=generate_race_id(course, date_str, race_time),
                                course=course,
                                race_time=race_time,
                                utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                                local_time=local_dt.strftime("%H:%M"),
                                timezone_name=tz_name,
                                field_size=int(race_item.get("FieldSize") or 0),
                                country=country_code,
                                discipline=discipline,
                                race_url=race_url,
                                form_guide_url=form_url,
                                data_sources={"course": "R&S-API"}
                            ))
        except Exception as e:
            self._add_error(f"Failed to parse R&S JSON payload: {e}", url=url)
        return out

class SportingLifeHorseApiSource(DataSourceBase):
    """
    Fetches stable and comprehensive global horse racing data from the 
    Sporting Life JSON API. This is a high-quality, resilient source.
    """
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        out: List[RaceData] = []
        base_url = CONFIG["SOURCES"]["SportingLifeHorseApi"]["base_url"]
        
        for dt in self._days(date_range):
            api_url = f"{base_url}?limit=250&date_start={dt.strftime('%Y-%m-%d')}&date_end={dt.strftime('%Y-%m-%d')}&sort_direction=ASC&sort_field=RACE_TIME"
            json_text = await self.http_client.fetch(api_url)
            if not json_text:
                self._add_error(f"Failed to fetch API data for {dt.strftime('%Y-%m-%d')}", url=api_url)
                continue
            try:
                payload = json.loads(json_text)
                if not isinstance(payload, list):
                    self._add_error(f"API response was not a list for {dt.strftime('%Y-%m-%d')}", url=api_url)
                    continue

                for race_item in payload:
                    if parsed_race := self._parse_race_item(race_item):
                        out.append(parsed_race)
            except Exception as e:
                self._add_error(f"An unexpected error occurred while parsing API data: {e}", url=api_url)
        return out

    def _parse_race_item(self, item: Dict[str, Any]) -> Optional[RaceData]:
        try:
            rs = item.get("race_summary", {})
            course = (rs.get("course_name") or "").strip()
            date_str = rs.get("date")
            time_str = rs.get("time")
            ride_count = int(rs.get("ride_count") or 0)

            if not all([course, date_str, time_str, ride_count > 0]):
                return None

            runners: List[Dict[str, Any]] = []
            for ride in item.get("rides", []):
                horse_info = ride.get("horse", {})
                betting_info = ride.get("betting", {})
                if horse_name := horse_info.get("name"):
                    runners.append({"name": horse_name, "odds_str": (betting_info.get("current_odds") or "").strip()})
            if not runners: return None

            fav_sorted = sorted(runners, key=lambda r: convert_odds_to_fractional(r.get("odds_str", "")))
            country = (rs.get("country_code") or "GB").upper()
            tz_name = get_track_timezone(course, country)
            local_dt = datetime.combine(datetime.fromisoformat(date_str).date(), datetime.strptime(time_str, "%H:%M").time()).replace(tzinfo=ZoneInfo(tz_name))
            race_url = f"https://www.sportinglife.com/racing/racecards/{normalize_course_name(course).replace(' ', '-')}/{date_str}/{time_str.replace(':', '')}"

            return RaceData(
                id=generate_race_id(course, date_str, time_str),
                course=course, race_time=time_str, utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                local_time=local_dt.strftime("%H:%M"), timezone_name=tz_name, field_size=ride_count,
                country=country, discipline="thoroughbred", favorite=fav_sorted[0] if fav_sorted else None,
                second_favorite=fav_sorted[1] if len(fav_sorted) > 1 else None, all_runners=runners,
                race_url=race_url, data_sources={"course": "SL-API", "runners": "SL-API", "odds": "SL-API"}
            )
        except Exception as e:
            logging.debug(f"Could not parse individual Sporting Life API race item: {e}")
            return None

class RacingPostSource(DataSourceBase):
    """Data source for the Racing Post, the gold standard for UK & Irish racing."""
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        races: List[RaceData] = []
        base_url = CONFIG['SOURCES']['RacingPost']['base_url']
        for dt in self._days(date_range):
            date_str = dt.strftime('%Y-%m-%d')
            index_url = f"{base_url}/racecards/{date_str}"
            html = await self.http_client.fetch(index_url)
            if not html: continue

            soup = BeautifulSoup(html, 'html.parser')
            meeting_links = {urljoin(base_url, a['href']) for a in soup.select('a[data-test-selector="link-meetingCourseName"]')}
            tasks = [self._parse_meeting(link, dt) for link in meeting_links]
            results = await asyncio.gather(*tasks)
            for res in results: races.extend(res)
        return races

    async def _parse_meeting(self, meeting_url: str, dt: datetime) -> List[RaceData]:
        html = await self.http_client.fetch(meeting_url)
        if not html: return []

        races = []
        soup = BeautifulSoup(html, 'html.parser')
        course = (soup.select_one('h1[data-test-selector="header-courseName"]') or soup.find('h1')).get_text(strip=True)
        country = "GB" # Assume GB/IE default
        
        for race_container in soup.select('div[data-test-selector^="racecard-raceStream"]'):
            try:
                time_tag = race_container.select_one('span[data-test-selector="racecard-raceTime"]')
                if not time_tag: continue
                race_time = time_tag.get_text(strip=True)

                runner_count_tag = race_container.select_one('span[data-test-selector="racecard-header-runners"]')
                field_size = int(runner_count_tag.get_text(strip=True).split()[0]) if runner_count_tag else 0
                if field_size == 0: continue
                
                race_link = race_container.select_one('a[data-test-selector="racecard-raceTitleLink"]')
                race_url = urljoin(meeting_url, race_link['href']) if race_link else meeting_url

                date_str = dt.strftime("%Y-%m-%d")
                tz_name = get_track_timezone(course, country)
                local_dt = datetime.combine(dt.date(), datetime.strptime(race_time, "%H:%M").time()).replace(tzinfo=ZoneInfo(tz_name))

                races.append(RaceData(
                    id=generate_race_id(course, date_str, race_time),
                    course=course, race_time=race_time, utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                    local_time=local_dt.strftime("%H:%M"), timezone_name=tz_name, field_size=field_size,
                    country=country, discipline="thoroughbred", race_url=race_url, data_sources={"course": "RP", "runners": "RP"}
                ))
            except Exception as e:
                self._add_error(f"Failed to parse RP race container: {e}", url=meeting_url)
        return races

class SkySportsSource(DataSourceBase):
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        races: List[RaceData] = []
        base_url = CONFIG["SOURCES"]["SkySports"]["base_url"]
        for dt in self._days(date_range):
            url = f"{base_url}/{dt.strftime('%d-%m-%Y')}" if dt.date() != datetime.now().date() else base_url
            html = await self.http_client.fetch(url)
            if not html: continue
            soup = BeautifulSoup(html, 'html.parser')
            for container in soup.find_all('div', class_='sdc-site-racing-meetings__event'):
                try:
                    link = container.find('a', class_='sdc-site-racing-meetings__event-link')
                    if not link or not link.get('href'): continue
                    race_url = urljoin(url, link['href'])
                    details = container.find('span', class_='sdc-site-racing-meetings__event-details')
                    if not details: continue
                    details_text = details.get_text(strip=True)
                    runners_match = re.search(r'(\d+)\s+runners?', details_text, re.I)
                    field_size = int(runners_match.group(1)) if runners_match else 0
                    if field_size == 0: continue
                    time_str = parse_local_hhmm(details_text)
                    if not time_str: continue
                    path_parts = urlparse(race_url).path.strip('/').split('/')
                    racecards_idx = path_parts.index('racecards')
                    course_slug = path_parts[racecards_idx + 1]
                    course_name = course_slug.replace('-', ' ').title()
                    country_match = re.search(r'\(([^)]+)\)', details_text)
                    country = country_match.group(1) if country_match else "GB"
                    tz_name = get_track_timezone(course_name, country)
                    local_dt = datetime.combine(dt.date(), datetime.strptime(time_str, "%H:%M").time()).replace(tzinfo=ZoneInfo(tz_name))
                    races.append(RaceData(
                        id=generate_race_id(course_name, dt.strftime("%Y-%m-%d"), time_str),
                        course=course_name, race_time=time_str, utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                        local_time=local_dt.strftime("%H:%M"), timezone_name=tz_name, field_size=field_size,
                        country=country, discipline="thoroughbred", race_url=race_url, data_sources={"course": "SkySports"}
                    ))
                except Exception as e:
                    self._add_error(f"Error parsing SkySports race container: {e}")
                    continue
        return races

class AtTheRacesSource(DataSourceBase):
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        races = []
        for dt in self._days(date_range):
            for region in CONFIG["SOURCES"]["AtTheRaces"]["regions"]:
                url = f"{CONFIG['SOURCES']['AtTheRaces']['base_url']}/ajax/marketmovers/tabs/{region}/{dt.strftime('%Y%m%d')}"
                try: races.extend(await self._parse_atr_region(url, region, dt.date()))
                except Exception as e: self._add_error(f"Failed to parse ATR region {region}: {e}", url=url)
        return races

    async def _parse_atr_region(self, url: str, region: str, date: datetime.date) -> List[RaceData]:
        html = await self.http_client.fetch(url)
        if not html: return []
        races, soup = [], BeautifulSoup(html, 'html.parser')
        for caption in soup.find_all('caption', string=re.compile(r'^\d{2}:\d{2}')):
            try:
                race_time = caption.get_text(strip=True).split()[0]
                panel = caption.find_parent('div', class_=re.compile(r'\bpanel\b'))
                course_heading = panel.find('h2') if panel else caption.find_previous('h2')
                if not course_heading: continue
                course_name = course_heading.get_text(strip=True)
                table = caption.find_next_sibling('table')
                if not table: continue
                runners = [{'name': c[0].get_text(strip=True), 'odds_str': c[1].get_text(strip=True)} for r in (table.find('tbody') or table).find_all('tr') if (c := r.find_all(['td', 'th'])) and len(c) > 1 and c[0].get_text(strip=True)]
                if not runners: continue
                sorted_runners = sorted(runners, key=lambda x: convert_odds_to_fractional(x.get('odds_str', '')))
                country_map = {'uk': 'GB', 'ireland': 'IE', 'usa': 'US', 'france': 'FR', 'saf': 'ZA', 'aus': 'AU'}
                country = country_map.get(region, 'GB')
                tz_name = get_track_timezone(course_name, country)
                local_dt = datetime.combine(date, datetime.strptime(race_time, "%H:%M").time()).replace(tzinfo=ZoneInfo(tz_name))
                races.append(RaceData(
                    id=generate_race_id(course_name, date.strftime("%Y-%m-%d"), race_time),
                    course=course_name, race_time=race_time, utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                    local_time=local_dt.strftime("%H:%M"), timezone_name=tz_name, field_size=len(runners),
                    country=country, discipline="thoroughbred",
                    race_url=f"{CONFIG['SOURCES']['AtTheRaces']['base_url']}/racecard/{normalize_course_name(course_name).replace(' ', '-')}/{date.strftime('%Y-%m-%d')}/{race_time.replace(':', '')}",
                    all_runners=runners, favorite=sorted_runners[0] if sorted_runners else None,
                    second_favorite=sorted_runners[1] if len(sorted_runners) > 1 else None,
                    data_sources={"course": "ATR", "runners": "ATR", "odds": "ATR"}
                ))
            except Exception as e:
                self._add_error(f"Error parsing ATR caption: {e}")
                continue
        return races

class GBGreyhoundSource(DataSourceBase):
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        base_url = CONFIG["SOURCES"]["GBGreyhounds"]["base_url"]
        index_url = f"{base_url}/greyhounds/racecards"
        html = await self.http_client.fetch(index_url)
        if not html: return []
        soup = BeautifulSoup(html, 'html.parser')
        meeting_links = {urljoin(base_url, a['href']) for a in soup.select('a[href*="/greyhounds/racecards/"]')}
        tasks = [self._parse_meeting(link) for link in meeting_links]
        results = await asyncio.gather(*tasks)
        return [race for sublist in results for race in sublist]

    async def _parse_meeting(self, meeting_url: str) -> List[RaceData]:
        html = await self.http_client.fetch(meeting_url)
        if not html: return []
        races = []
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.select('a[href*="/racecard/"]'):
            race_url = urljoin(meeting_url, link['href'])
            try:
                path_parts = urlparse(race_url).path.strip('/').split('/')
                course = path_parts[-3].replace('-', ' ').title()
                date_str = path_parts[-2]
                time_str_raw = path_parts[-1]
                time_str = f"{time_str_raw[:2]}:{time_str_raw[2:]}"
                tz_name = get_track_timezone(course, "GB")
                local_dt = datetime.combine(datetime.fromisoformat(date_str).date(), datetime.strptime(time_str, "%H:%M").time()).replace(tzinfo=ZoneInfo(tz_name))
                races.append(RaceData(
                    id=generate_race_id(course, date_str, time_str),
                    course=course, race_time=time_str, utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                    local_time=local_dt.strftime("%H:%M"), timezone_name=tz_name, field_size=6, # Assume 6
                    country="GB", discipline="greyhound", race_url=race_url, data_sources={"course": "SL-GR"}
                ))
            except Exception as e:
                self._add_error(f"Failed to parse greyhound race link {race_url}: {e}")
        return races

class HarnessAustraliaSource(DataSourceBase):
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        out = []
        for dt in self._days(date_range):
            url = f"{CONFIG['SOURCES']['HarnessAustralia']['base_url']}/racing/fields/?firstDate={dt.strftime('%d/%m/%Y')}"
            html = await self.http_client.fetch(url)
            if not html: continue
            soup = BeautifulSoup(html, 'html.parser')
            meeting_links = {urljoin(url, a['href']) for a in soup.select('a[href*="/racing/fields/race-fields/"]')}
            tasks = [self._parse_meeting(link, dt) for link in meeting_links]
            results = await asyncio.gather(*tasks)
            for res in results: out.extend(res)
        return out

    async def _parse_meeting(self, meeting_url: str, dt: datetime) -> List[RaceData]:
        html = await self.http_client.fetch(meeting_url)
        if not html: return []
        races = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            course = (soup.find('h1') or soup.find('h2')).get_text(strip=True)
            for race_link in soup.select('a[href*="race-fields/?mc="]'):
                race_time = parse_local_hhmm(race_link.get_text(strip=True))
                if not race_time: continue
                tz_name = get_track_timezone(course, "AU")
                local_dt = datetime.combine(dt.date(), datetime.strptime(race_time, "%H:%M").time()).replace(tzinfo=ZoneInfo(tz_name))
                races.append(RaceData(
                    id=generate_race_id(course, dt.strftime("%Y-%m-%d"), race_time),
                    course=course, race_time=race_time, utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                    local_time=local_dt.strftime("%H:%M"), timezone_name=tz_name, field_size=0,
                    country="AU", discipline="harness", race_url=urljoin(meeting_url, race_link['href']),
                    data_sources={"course": "HRA"}
                ))
        except Exception as e:
            self._add_error(f"Failed parsing harness meeting: {e}", url=meeting_url)
        return races

class StandardbredCanadaSource(DataSourceBase):
    async def fetch_races(self, date_range: Tuple[datetime, datetime]) -> List[RaceData]:
        out = []
        for dt in self._days(date_range):
            url = f"{CONFIG['SOURCES']['StandardbredCanada']['base_url']}/racing/entries/date/{dt.strftime('%Y-%m-%d')}"
            html = await self.http_client.fetch(url)
            if not html: continue
            soup = BeautifulSoup(html, 'html.parser')
            meeting_links = {urljoin(url, a['href']) for a in soup.select(f'a[href*="/racing/entries/"][href*="{dt.strftime("%Y-%m-%d")}"]')}
            tasks = [self._parse_meeting(link, dt) for link in meeting_links]
            results = await asyncio.gather(*tasks)
            for res in results: out.extend(res)
        return out

    async def _parse_meeting(self, meeting_url: str, dt: datetime) -> List[RaceData]:
        html = await self.http_client.fetch(meeting_url)
        if not html: return []
        races = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            course = (soup.find('h1') or soup.find('h2')).get_text(strip=True)
            for section in soup.select("section[id^='race-']"):
                time_text = (section.find(class_='post-time') or section).get_text()
                race_time = parse_local_hhmm(time_text)
                if not race_time: continue
                runners = section.select("table.entries tbody tr")
                tz_name = get_track_timezone(course, "CA")
                local_dt = datetime.combine(dt.date(), datetime.strptime(race_time, "%H:%M").time()).replace(tzinfo=ZoneInfo(tz_name))
                races.append(RaceData(
                    id=generate_race_id(course, dt.strftime("%Y-%m-%d"), race_time),
                    course=course, race_time=race_time, utc_datetime=local_dt.astimezone(ZoneInfo("UTC")),
                    local_time=local_dt.strftime("%H:%M"), timezone_name=tz_name, field_size=len(runners),
                    country="CA", discipline="harness", race_url=meeting_url, all_runners=[{"name": "Runner", "odds_str":""}]*len(runners),
                    data_sources={"course": "StdCan", "runners": "StdCan"}
                ))
        except Exception as e:
            self._add_error(f"Failed parsing standardbred meeting: {e}", url=meeting_url)
        return races

# =============================================================================
# CORE LOGIC
# =============================================================================

class RacingDataAggregator:
    def __init__(self, http_client: AsyncHttpClient):
        self.http_client = http_client
        self.scorer = EnhancedValueScorer()
        self.sources = self._initialize_sources()

    def _initialize_sources(self) -> List[DataSourceBase]:
        source_map = {
            "RacingAndSports": RacingAndSportsSource,
            "SportingLifeHorseApi": SportingLifeHorseApiSource,
            "RacingPost": RacingPostSource,
            "SkySports": SkySportsSource,
            "AtTheRaces": AtTheRacesSource,
            "GBGreyhounds": GBGreyhoundSource,
            "HarnessAustralia": HarnessAustraliaSource,
            "StandardbredCanada": StandardbredCanadaSource,
        }
        return [source_map[name](self.http_client) for name, cfg in CONFIG["SOURCES"].items() if cfg.get("enabled") and name in source_map]

    async def fetch_all_races(self, start_dt: datetime, end_dt: datetime) -> Tuple[List[RaceData], ScanStatistics]:
        stats = ScanStatistics()
        tasks = [self._fetch_from_source(source, start_dt, end_dt) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_races = []
        for i, result in enumerate(results):
            source = self.sources[i]
            if isinstance(result, Exception):
                stats.source_errors.append(SourceError(source_name=source.name, error_message=str(result), error_type=type(result).__name__, timestamp=datetime.now()))
            else:
                races, source_errors = result
                stats.per_source_counts[source.name] = len(races)
                stats.source_errors.extend(source_errors)
                all_races.extend(races)
        
        stats.total_races_found = len(all_races)
        deduped_races = self._deduplicate_races(all_races)
        await self._enrich_rs_links(deduped_races)
        stats.races_after_dedup = len(deduped_races)
        
        for race in deduped_races:
            race.value_score = self.scorer.calculate_score(race)
            
        return sorted(deduped_races, key=lambda r: r.value_score, reverse=True), stats

    async def _fetch_from_source(self, source: DataSourceBase, start_dt: datetime, end_dt: datetime) -> Tuple[List[RaceData], List[SourceError]]:
        try:
            races = await source.fetch_races((start_dt, end_dt))
            return races, source.source_errors
        except Exception as e:
            logging.error(f"Error fetching from {source.name}: {e}")
            return [], [SourceError(source_name=source.name, error_message=str(e), error_type=type(e).__name__, timestamp=datetime.now())]

    def _deduplicate_races(self, races: List[RaceData]) -> List[RaceData]:
        unique_races = {}
        for race in races:
            key = generate_race_id(race.course, race.utc_datetime.strftime('%Y-%m-%d'), race.race_time)
            if key not in unique_races or self._is_more_complete(race, unique_races[key]):
                if key in unique_races:
                    race.data_sources.update(unique_races[key].data_sources)
                unique_races[key] = race
            else:
                unique_races[key].data_sources.update(race.data_sources)
        return list(unique_races.values())

    def _is_more_complete(self, race1: RaceData, race2: RaceData) -> bool:
        return self.scorer._calculate_data_quality_score(race1) > self.scorer._calculate_data_quality_score(race2)

    async def _enrich_rs_links(self, races: List[RaceData]) -> None:
        url = "https://www.racingandsports.com.au/todays-racing-json-v2"
        try:
            if not (text := await self.http_client.fetch(url)): return
            payload = json.loads(text); lookup: Dict[Tuple[str, str], str] = {}
            for disc in payload or []:
                for country in disc.get("Countries", []):
                    for meet in country.get("Meetings", []):
                        course = meet.get("Course")
                        link = meet.get("PDFUrl") or meet.get("PreMeetingUrl")
                        if not course or not link: continue
                        if not (m := re.search(r"/(\d{4}-\d{2}-\d{2})", link)): continue
                        lookup[(normalize_course_name(course), m.group(1))] = link
            for r in races:
                date = r.utc_datetime.astimezone(ZoneInfo(r.timezone_name)).strftime("%Y-%m-%d")
                key = (normalize_course_name(r.course), date)
                if (link := lookup.get(key)) and not r.form_guide_url:
                    r.form_guide_url = link
                    r.data_sources["form"] = "R&S"
        except Exception as e:
            logging.debug(f"R&S enrichment failed: {e}")

class OutputManager:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.out_dir.mkdir(exist_ok=True, parents=True)
        self.jinja_env = Environment()

    def write_html_report(self, races: List[RaceData], stats: ScanStatistics, min_r: int, max_r: int):
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
        logging.info(f"Report saved to {filename}")
        if CONFIG["OUTPUT"]["AUTO_OPEN_BROWSER"]:
            webbrowser.open(f"file://{os.path.abspath(filename)}")

    def write_json_report(self, races: List[RaceData], stats: ScanStatistics) -> Path:
        filename = self.out_dir / f"racing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        races_data = [asdict(r, dict_factory=lambda data: {k: v for k, v in data if v is not None}) for r in races]
        for r in races_data: r['utc_datetime'] = r['utc_datetime'].isoformat()
        stats_data = asdict(stats)
        for error in stats_data['source_errors']: error['timestamp'] = error['timestamp'].isoformat()
        output_data = {'generated_at': datetime.now().isoformat(), 'statistics': stats_data, 'races': races_data}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        logging.info(f"JSON data saved to {filename}")
        return filename

    def write_csv_report(self, races: List[RaceData]) -> Path:
        filename = self.out_dir / f"racing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Course", "Time", "Field Size", "Country", "Discipline", "Score", "Fav Name", "Fav Odds", "URL"])
            for r in races:
                fav = r.favorite or {}
                writer.writerow([r.id, r.course, r.local_time, r.field_size, r.country, r.discipline, f"{r.value_score:.1f}", fav.get('name',''), fav.get('odds_str',''), r.race_url])
        logging.info(f"CSV data saved to {filename}")
        return filename

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main_async(args: argparse.Namespace):
    logging.basicConfig(level=logging.INFO if not args.verbose else logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(), logging.FileHandler('racing_scanner.log')])
    start_time = time.time()
    cache = CacheManager(Path(CONFIG["DEFAULT_CACHE_DIR"]))
    http_client = AsyncHttpClient(cache, interactive_fallback=args.interactive)
    try:
        print(f"🚀 Starting {CONFIG['APP_NAME']} v{CONFIG['SCHEMA_VERSION']}")
        print(f"📅 Scanning from {args.days_back} days back to {args.days_forward} days forward")
        aggregator = RacingDataAggregator(http_client)
        start_dt = datetime.now() + timedelta(days=args.days_back)
        end_dt = datetime.now() + timedelta(days=args.days_forward)
        races, stats = await aggregator.fetch_all_races(start_dt, end_dt)
        stats.duration_seconds = time.time() - start_time
        print(f"✅ Scan completed in {stats.duration_seconds:.1f} seconds: Found {stats.total_races_found} total races, {stats.races_after_dedup} unique")
        
        output_manager = OutputManager(Path(CONFIG["DEFAULT_OUTPUT_DIR"]))
        if 'html' in args.formats:
            output_manager.write_html_report(races, stats, args.min_field_size, args.max_field_size)
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
    except KeyboardInterrupt: print("\n⏹️ Scan interrupted by user")
    except Exception as e: logging.error(f"Critical error: {e}", exc_info=True); print(f"❌ Critical error occurred: {e}")
    finally: await http_client.close()

def main():
    parser = argparse.ArgumentParser(description=f"{CONFIG['APP_NAME']} v{CONFIG['SCHEMA_VERSION']}", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""
Examples:
  python racing_scanner.py --days-forward 0       # Scan today only
  python racing_scanner.py --min-field-size 3 --max-field-size 6
  python racing_scanner.py --interactive           # Enable manual HTML input
  python racing_scanner.py --formats html json csv # Specify output formats
    """)
    parser.add_argument("--days-back", type=int, default=0, help="Days back to scan (e.g., -1 for yesterday)")
    parser.add_argument("--days-forward", type=int, default=1, help="Days forward to scan")
    parser.add_argument("--min-field-size", type=int, default=CONFIG["FILTERS"]["MIN_FIELD_SIZE"])
    parser.add_argument("--max-field-size", type=int, default=CONFIG["FILTERS"]["MAX_FIELD_SIZE"])
    parser.add_argument("--interactive", action="store_true", help="Enable interactive fallback for manual HTML input")
    parser.add_argument("--formats", nargs='+', default=['html'], help="Output formats (html, json, csv)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")
    args = parser.parse_args()
    try:
        asyncio.run(main_async(args))
        print("🎯 Scan complete! Good luck with your bets! 🍀")
    except KeyboardInterrupt: print("\n👋 Goodbye!")
    except Exception as e: print(f"💥 Unexpected error: {e}"); sys.exit(1)

if __name__ == "__main__":
    main()