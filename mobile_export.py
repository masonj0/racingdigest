#!/usr/bin/env python3
"""
Mobile Data Export for Racing Scanner

Provides data export capabilities for the mobile racing scanner,
including various formats for easy sharing and analysis.
"""

import json
import csv
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import shutil

class MobileExporter:
    """Handles data export for the mobile racing scanner"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path.home() / ".racing_scanner"
        self.data_dir.mkdir(exist_ok=True)
        self.export_dir = self.data_dir / "exports"
        self.export_dir.mkdir(exist_ok=True)
    
    def find_scan_files(self, days_back: int = 7) -> List[Path]:
        """Find scan files from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        scan_files = []
        
        # Look for JSON scan files
        json_pattern = "racing_data_*.json"
        for file_path in self.data_dir.glob(json_pattern):
            try:
                # Extract timestamp from filename
                timestamp_str = file_path.stem.split("_")[-2] + "_" + file_path.stem.split("_")[-1]
                file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                if file_date >= cutoff_date:
                    scan_files.append(file_path)
            except (ValueError, IndexError):
                continue
        
        return sorted(scan_files, reverse=True)
    
    def load_scan_data(self, file_path: Path) -> Dict:
        """Load scan data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
            return {}
    
    def export_to_csv(self, scan_files: List[Path], output_file: str = None) -> str:
        """Export scan data to CSV format"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.export_dir / f"racing_export_{timestamp}.csv"
        
        all_races = []
        
        for file_path in scan_files:
            scan_data = self.load_scan_data(file_path)
            if scan_data and 'races' in scan_data:
                for race in scan_data['races']:
                    # Add scan metadata
                    race['scan_timestamp'] = scan_data.get('generated_at', '')
                    race['scan_file'] = file_path.name
                    all_races.append(race)
        
        if not all_races:
            print("No race data found to export")
            return ""
        
        # Define CSV columns
        columns = [
            'scan_timestamp', 'id', 'course', 'local_time', 'timezone_name',
            'field_size', 'country', 'discipline', 'value_score',
            'favorite_name', 'favorite_odds', 'second_favorite_name', 'second_favorite_odds',
            'race_url', 'form_guide_url', 'data_sources'
        ]
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                
                for race in all_races:
                    # Prepare row data
                    row = {}
                    for col in columns:
                        if col == 'favorite_name':
                            row[col] = race.get('favorite', {}).get('name', '')
                        elif col == 'favorite_odds':
                            row[col] = race.get('favorite', {}).get('odds_str', '')
                        elif col == 'second_favorite_name':
                            row[col] = race.get('second_favorite', {}).get('name', '')
                        elif col == 'second_favorite_odds':
                            row[col] = race.get('second_favorite', {}).get('odds_str', '')
                        elif col == 'data_sources':
                            sources = race.get('data_sources', {})
                            row[col] = ','.join(sources.values()) if sources else ''
                        else:
                            row[col] = race.get(col, '')
                    
                    writer.writerow(row)
            
            print(f"CSV export completed: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return ""
    
    def export_to_json(self, scan_files: List[Path], output_file: str = None) -> str:
        """Export scan data to JSON format"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.export_dir / f"racing_export_{timestamp}.json"
        
        export_data = {
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "scan_files_count": len(scan_files),
                "total_races": 0,
                "date_range": {
                    "start": None,
                    "end": None
                }
            },
            "scans": [],
            "races": []
        }
        
        all_races = []
        scan_timestamps = []
        
        for file_path in scan_files:
            scan_data = self.load_scan_data(file_path)
            if scan_data:
                export_data["scans"].append({
                    "file": file_path.name,
                    "generated_at": scan_data.get('generated_at', ''),
                    "statistics": scan_data.get('statistics', {})
                })
                
                if 'races' in scan_data:
                    for race in scan_data['races']:
                        race['scan_file'] = file_path.name
                        all_races.append(race)
                        scan_timestamps.append(scan_data.get('generated_at', ''))
        
        export_data["races"] = all_races
        export_data["export_info"]["total_races"] = len(all_races)
        
        if scan_timestamps:
            export_data["export_info"]["date_range"]["start"] = min(scan_timestamps)
            export_data["export_info"]["date_range"]["end"] = max(scan_timestamps)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"JSON export completed: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return ""
    
    def export_to_sqlite(self, scan_files: List[Path], output_file: str = None) -> str:
        """Export scan data to SQLite database"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.export_dir / f"racing_export_{timestamp}.db"
        
        try:
            conn = sqlite3.connect(output_file)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT,
                    generated_at TEXT,
                    total_races_found INTEGER,
                    races_after_dedup INTEGER,
                    duration_seconds REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS races (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    race_id TEXT,
                    course TEXT,
                    local_time TEXT,
                    timezone_name TEXT,
                    field_size INTEGER,
                    country TEXT,
                    discipline TEXT,
                    value_score REAL,
                    favorite_name TEXT,
                    favorite_odds TEXT,
                    second_favorite_name TEXT,
                    second_favorite_odds TEXT,
                    race_url TEXT,
                    form_guide_url TEXT,
                    data_sources TEXT,
                    FOREIGN KEY (scan_id) REFERENCES scans (id)
                )
            ''')
            
            # Insert scan data
            for file_path in scan_files:
                scan_data = self.load_scan_data(file_path)
                if scan_data:
                    stats = scan_data.get('statistics', {})
                    cursor.execute('''
                        INSERT INTO scans (file_name, generated_at, total_races_found, 
                                         races_after_dedup, duration_seconds)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        file_path.name,
                        scan_data.get('generated_at', ''),
                        stats.get('total_races_found', 0),
                        stats.get('races_after_dedup', 0),
                        stats.get('duration_seconds', 0)
                    ))
                    
                    scan_id = cursor.lastrowid
                    
                    # Insert race data
                    if 'races' in scan_data:
                        for race in scan_data['races']:
                            sources = race.get('data_sources', {})
                            sources_str = ','.join(sources.values()) if sources else ''
                            
                            cursor.execute('''
                                INSERT INTO races (scan_id, race_id, course, local_time, 
                                                 timezone_name, field_size, country, discipline,
                                                 value_score, favorite_name, favorite_odds,
                                                 second_favorite_name, second_favorite_odds,
                                                 race_url, form_guide_url, data_sources)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                scan_id,
                                race.get('id', ''),
                                race.get('course', ''),
                                race.get('local_time', ''),
                                race.get('timezone_name', ''),
                                race.get('field_size', 0),
                                race.get('country', ''),
                                race.get('discipline', ''),
                                race.get('value_score', 0),
                                race.get('favorite', {}).get('name', ''),
                                race.get('favorite', {}).get('odds_str', ''),
                                race.get('second_favorite', {}).get('name', ''),
                                race.get('second_favorite', {}).get('odds_str', ''),
                                race.get('race_url', ''),
                                race.get('form_guide_url', ''),
                                sources_str
                            ))
            
            conn.commit()
            conn.close()
            
            print(f"SQLite export completed: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"Error exporting to SQLite: {e}")
            return ""
    
    def create_archive(self, files: List[str], output_file: str = None) -> str:
        """Create a ZIP archive of exported files"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.export_dir / f"racing_export_{timestamp}.zip"
        
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if Path(file_path).exists():
                        zipf.write(file_path, Path(file_path).name)
            
            print(f"Archive created: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"Error creating archive: {e}")
            return ""
    
    def export_all_formats(self, days_back: int = 7, create_archive: bool = True) -> Dict[str, str]:
        """Export data in all available formats"""
        scan_files = self.find_scan_files(days_back)
        
        if not scan_files:
            print(f"No scan files found from the last {days_back} days")
            return {}
        
        print(f"Found {len(scan_files)} scan files to export")
        
        exported_files = {}
        
        # Export to CSV
        csv_file = self.export_to_csv(scan_files)
        if csv_file:
            exported_files['csv'] = csv_file
        
        # Export to JSON
        json_file = self.export_to_json(scan_files)
        if json_file:
            exported_files['json'] = json_file
        
        # Export to SQLite
        sqlite_file = self.export_to_sqlite(scan_files)
        if sqlite_file:
            exported_files['sqlite'] = sqlite_file
        
        # Create archive if requested
        if create_archive and exported_files:
            archive_file = self.create_archive(list(exported_files.values()))
            if archive_file:
                exported_files['archive'] = archive_file
        
        return exported_files
    
    def cleanup_old_exports(self, days: int = 30):
        """Clean up old export files"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        for file_path in self.export_dir.glob("*"):
            if file_path.is_file():
                try:
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        cleaned_count += 1
                except Exception as e:
                    print(f"Warning: Could not check/delete {file_path}: {e}")
        
        print(f"Cleaned up {cleaned_count} old export files")
    
    def get_export_summary(self) -> Dict:
        """Get summary of available exports"""
        summary = {
            "export_directory": str(self.export_dir),
            "total_files": 0,
            "file_types": {},
            "recent_exports": []
        }
        
        for file_path in self.export_dir.glob("*"):
            if file_path.is_file():
                summary["total_files"] += 1
                file_ext = file_path.suffix.lower()
                summary["file_types"][file_ext] = summary["file_types"].get(file_ext, 0) + 1
                
                # Add to recent exports (last 10)
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                summary["recent_exports"].append({
                    "file": file_path.name,
                    "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                    "modified": file_time.isoformat()
                })
        
        # Sort recent exports by modification time
        summary["recent_exports"].sort(key=lambda x: x["modified"], reverse=True)
        summary["recent_exports"] = summary["recent_exports"][:10]
        
        return summary

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mobile Data Export for Racing Scanner")
    parser.add_argument("--csv", action="store_true", help="Export to CSV format")
    parser.add_argument("--json", action="store_true", help="Export to JSON format")
    parser.add_argument("--sqlite", action="store_true", help="Export to SQLite database")
    parser.add_argument("--all", action="store_true", help="Export to all formats")
    parser.add_argument("--days", type=int, default=7, help="Number of days back to export")
    parser.add_argument("--archive", action="store_true", help="Create ZIP archive")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="Clean up exports older than DAYS")
    parser.add_argument("--summary", action="store_true", help="Show export summary")
    parser.add_argument("--output", metavar="FILE", help="Output file name")
    
    args = parser.parse_args()
    
    exporter = MobileExporter()
    
    if args.summary:
        summary = exporter.get_export_summary()
        print("Export Summary:")
        print(json.dumps(summary, indent=2))
    
    elif args.cleanup:
        exporter.cleanup_old_exports(args.cleanup)
    
    elif args.all:
        exported_files = exporter.export_all_formats(args.days, args.archive)
        print(f"Export completed: {len(exported_files)} files created")
        for format_type, file_path in exported_files.items():
            print(f"  {format_type}: {file_path}")
    
    elif args.csv:
        scan_files = exporter.find_scan_files(args.days)
        csv_file = exporter.export_to_csv(scan_files, args.output)
        if csv_file:
            print(f"CSV export: {csv_file}")
    
    elif args.json:
        scan_files = exporter.find_scan_files(args.days)
        json_file = exporter.export_to_json(scan_files, args.output)
        if json_file:
            print(f"JSON export: {json_file}")
    
    elif args.sqlite:
        scan_files = exporter.find_scan_files(args.days)
        sqlite_file = exporter.export_to_sqlite(scan_files, args.output)
        if sqlite_file:
            print(f"SQLite export: {sqlite_file}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()