#!/usr/bin/env python3
"""
Mobile Performance Monitor for Racing Scanner

Monitors and reports on the performance of the mobile racing scanner,
including resource usage, scan times, and system health.
"""

import json
import os
import time
import psutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class MobileMonitor:
    """Monitors performance of the mobile racing scanner"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".racing_scanner"
        self.config_dir.mkdir(exist_ok=True)
        self.stats_file = self.config_dir / "performance_stats.json"
        self.log_file = self.config_dir / "performance.log"
        self.load_stats()
    
    def load_stats(self):
        """Load performance statistics"""
        default_stats = {
            "scans": [],
            "system_info": {},
            "performance_history": [],
            "last_updated": None
        }
        
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
                    # Ensure all required keys exist
                    for key, default_value in default_stats.items():
                        if key not in self.stats:
                            self.stats[key] = default_value
            except Exception as e:
                print(f"Warning: Could not load performance stats: {e}")
                self.stats = default_stats
        else:
            self.stats = default_stats
            self.update_system_info()
    
    def save_stats(self):
        """Save performance statistics"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save performance stats: {e}")
    
    def update_system_info(self):
        """Update system information"""
        try:
            self.stats["system_info"] = {
                "platform": os.uname().sysname if hasattr(os, 'uname') else os.name,
                "architecture": os.uname().machine if hasattr(os, 'uname') else "unknown",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                "is_termux": os.path.exists("/data/data/com.termux"),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Warning: Could not update system info: {e}")
    
    def log_performance(self, scan_data: Dict):
        """Log performance data for a scan"""
        timestamp = datetime.now().isoformat()
        
        # Get current system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        performance_data = {
            "timestamp": timestamp,
            "scan_duration": scan_data.get("duration_seconds", 0),
            "races_found": scan_data.get("total_races_found", 0),
            "unique_races": scan_data.get("races_after_dedup", 0),
            "high_value_races": scan_data.get("high_value_count", 0),
            "system_metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
        }
        
        # Add to performance history (keep last 100 entries)
        self.stats["performance_history"].append(performance_data)
        if len(self.stats["performance_history"]) > 100:
            self.stats["performance_history"] = self.stats["performance_history"][-100:]
        
        # Add to scans list
        self.stats["scans"].append({
            "timestamp": timestamp,
            "duration": scan_data.get("duration_seconds", 0),
            "races_found": scan_data.get("total_races_found", 0),
            "success": scan_data.get("success", True)
        })
        
        # Keep only last 50 scans
        if len(self.stats["scans"]) > 50:
            self.stats["scans"] = self.stats["scans"][-50:]
        
        self.stats["last_updated"] = timestamp
        self.save_stats()
        
        # Log to file
        self.log_to_file(performance_data)
    
    def log_to_file(self, data: Dict):
        """Log performance data to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"[{data['timestamp']}] Scan: {data['scan_duration']:.1f}s, "
                       f"Races: {data['races_found']}, CPU: {data['system_metrics']['cpu_percent']:.1f}%, "
                       f"Memory: {data['system_metrics']['memory_percent']:.1f}%\n")
        except Exception as e:
            print(f"Warning: Could not log to file: {e}")
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        if not self.stats["performance_history"]:
            return {"message": "No performance data available"}
        
        recent_data = self.stats["performance_history"][-10:]  # Last 10 scans
        
        avg_duration = sum(d["scan_duration"] for d in recent_data) / len(recent_data)
        avg_races = sum(d["races_found"] for d in recent_data) / len(recent_data)
        avg_cpu = sum(d["system_metrics"]["cpu_percent"] for d in recent_data) / len(recent_data)
        avg_memory = sum(d["system_metrics"]["memory_percent"] for d in recent_data) / len(recent_data)
        
        # Calculate success rate
        successful_scans = sum(1 for scan in self.stats["scans"] if scan.get("success", True))
        total_scans = len(self.stats["scans"])
        success_rate = (successful_scans / total_scans * 100) if total_scans > 0 else 0
        
        return {
            "avg_scan_duration": round(avg_duration, 1),
            "avg_races_found": round(avg_races, 1),
            "avg_cpu_usage": round(avg_cpu, 1),
            "avg_memory_usage": round(avg_memory, 1),
            "success_rate": round(success_rate, 1),
            "total_scans": total_scans,
            "last_scan": self.stats["scans"][-1]["timestamp"] if self.stats["scans"] else None
        }
    
    def get_system_health(self) -> Dict:
        """Get current system health status"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine health status
            health_status = "good"
            warnings = []
            
            if cpu_percent > 80:
                health_status = "warning"
                warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > 85:
                health_status = "warning"
                warnings.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > 90:
                health_status = "critical"
                warnings.append(f"Low disk space: {disk.percent:.1f}% used")
            
            if cpu_percent > 95:
                health_status = "critical"
                warnings.append(f"Critical CPU usage: {cpu_percent:.1f}%")
            
            return {
                "status": health_status,
                "warnings": warnings,
                "metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": disk.percent,
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                }
            }
        except Exception as e:
            return {
                "status": "unknown",
                "warnings": [f"Could not determine system health: {e}"],
                "metrics": {}
            }
    
    def get_recommendations(self) -> List[str]:
        """Get performance recommendations"""
        recommendations = []
        summary = self.get_performance_summary()
        health = self.get_system_health()
        
        # Performance recommendations
        if summary.get("avg_scan_duration", 0) > 60:
            recommendations.append("Consider reducing concurrent requests to improve scan speed")
        
        if summary.get("avg_cpu_usage", 0) > 80:
            recommendations.append("High CPU usage detected - consider battery saver mode")
        
        if summary.get("avg_memory_usage", 0) > 85:
            recommendations.append("High memory usage - consider closing other apps")
        
        # System health recommendations
        if health["status"] == "critical":
            recommendations.append("System health is critical - check available resources")
        elif health["status"] == "warning":
            recommendations.append("System health shows warnings - monitor resource usage")
        
        # Success rate recommendations
        if summary.get("success_rate", 100) < 90:
            recommendations.append("Low success rate - check network connectivity and settings")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Performance looks good! No optimizations needed")
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate a comprehensive performance report"""
        summary = self.get_performance_summary()
        health = self.get_system_health()
        recommendations = self.get_recommendations()
        
        report = []
        report.append("=" * 50)
        report.append("📊 RACING SCANNER PERFORMANCE REPORT")
        report.append("=" * 50)
        
        # System Information
        report.append("\n🖥️  SYSTEM INFORMATION:")
        for key, value in self.stats["system_info"].items():
            if key != "last_updated":
                report.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Performance Summary
        report.append("\n📈 PERFORMANCE SUMMARY:")
        report.append(f"  Average Scan Duration: {summary.get('avg_scan_duration', 0)}s")
        report.append(f"  Average Races Found: {summary.get('avg_races_found', 0)}")
        report.append(f"  Average CPU Usage: {summary.get('avg_cpu_usage', 0)}%")
        report.append(f"  Average Memory Usage: {summary.get('avg_memory_usage', 0)}%")
        report.append(f"  Success Rate: {summary.get('success_rate', 0)}%")
        report.append(f"  Total Scans: {summary.get('total_scans', 0)}")
        
        # System Health
        report.append(f"\n🏥 SYSTEM HEALTH: {health['status'].upper()}")
        for warning in health["warnings"]:
            report.append(f"  ⚠️  {warning}")
        
        if health["metrics"]:
            report.append(f"  CPU: {health['metrics']['cpu_percent']:.1f}%")
            report.append(f"  Memory: {health['metrics']['memory_percent']:.1f}%")
            report.append(f"  Disk: {health['metrics']['disk_percent']:.1f}%")
        
        # Recommendations
        report.append("\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            report.append(f"  • {rec}")
        
        # Recent Activity
        if self.stats["scans"]:
            report.append("\n🕒 RECENT ACTIVITY:")
            recent_scans = self.stats["scans"][-5:]  # Last 5 scans
            for scan in recent_scans:
                timestamp = scan["timestamp"][:19].replace("T", " ")
                status = "✅" if scan.get("success", True) else "❌"
                report.append(f"  {status} {timestamp}: {scan['duration']:.1f}s, {scan['races_found']} races")
        
        report.append("\n" + "=" * 50)
        report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(report)
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up performance data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff_date.isoformat()
        
        # Clean up performance history
        original_count = len(self.stats["performance_history"])
        self.stats["performance_history"] = [
            entry for entry in self.stats["performance_history"]
            if entry["timestamp"] > cutoff_timestamp
        ]
        cleaned_count = len(self.stats["performance_history"])
        
        # Clean up scans
        original_scans = len(self.stats["scans"])
        self.stats["scans"] = [
            scan for scan in self.stats["scans"]
            if scan["timestamp"] > cutoff_timestamp
        ]
        cleaned_scans = len(self.stats["scans"])
        
        self.save_stats()
        
        return {
            "performance_history_removed": original_count - cleaned_count,
            "scans_removed": original_scans - cleaned_scans
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mobile Performance Monitor")
    parser.add_argument("--report", action="store_true", help="Generate performance report")
    parser.add_argument("--summary", action="store_true", help="Show performance summary")
    parser.add_argument("--health", action="store_true", help="Show system health")
    parser.add_argument("--recommendations", action="store_true", help="Show recommendations")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="Clean up data older than DAYS")
    parser.add_argument("--log-scan", nargs="+", metavar=("DURATION", "RACES", "SUCCESS"),
                       help="Log a scan (duration, races_found, success)")
    
    args = parser.parse_args()
    
    monitor = MobileMonitor()
    
    if args.report:
        print(monitor.generate_report())
    
    elif args.summary:
        summary = monitor.get_performance_summary()
        print("Performance Summary:")
        print(json.dumps(summary, indent=2))
    
    elif args.health:
        health = monitor.get_system_health()
        print("System Health:")
        print(json.dumps(health, indent=2))
    
    elif args.recommendations:
        recommendations = monitor.get_recommendations()
        print("Recommendations:")
        for rec in recommendations:
            print(f"• {rec}")
    
    elif args.cleanup:
        result = monitor.cleanup_old_data(args.cleanup)
        print(f"Cleanup completed: {result}")
    
    elif args.log_scan:
        if len(args.log_scan) >= 2:
            scan_data = {
                "duration_seconds": float(args.log_scan[0]),
                "total_races_found": int(args.log_scan[1]),
                "success": args.log_scan[2].lower() == "true" if len(args.log_scan) > 2 else True
            }
            monitor.log_performance(scan_data)
            print("Scan performance logged")
        else:
            print("Error: log-scan requires at least duration and races_found")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()