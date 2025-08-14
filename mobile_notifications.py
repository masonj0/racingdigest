#!/usr/bin/env python3
"""
Mobile Notifications for Racing Scanner

Provides notification capabilities for the mobile racing scanner,
including local notifications and optional push notifications.
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class MobileNotifier:
    """Handles notifications for the mobile racing scanner"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".racing_scanner"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "notifications.json"
        self.load_config()
    
    def load_config(self):
        """Load notification configuration"""
        default_config = {
            "enabled": True,
            "high_value_threshold": 70,
            "extreme_value_threshold": 90,
            "notification_types": {
                "high_value": True,
                "extreme_value": True,
                "scan_complete": True,
                "errors": True
            },
            "sound_enabled": True,
            "vibration_enabled": True,
            "quiet_hours": {
                "enabled": False,
                "start": "22:00",
                "end": "07:00"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            except Exception as e:
                print(f"Warning: Could not load notification config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save notification configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save notification config: {e}")
    
    def is_quiet_hours(self) -> bool:
        """Check if current time is during quiet hours"""
        if not self.config["quiet_hours"]["enabled"]:
            return False
        
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        start_time = self.config["quiet_hours"]["start"]
        end_time = self.config["quiet_hours"]["end"]
        
        # Simple time comparison (assumes quiet hours don't cross midnight)
        return start_time <= current_time <= end_time
    
    def send_termux_notification(self, title: str, content: str, priority: str = "default"):
        """Send notification using Termux API"""
        try:
            # Check if Termux API is available
            result = subprocess.run(["termux-notification"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Termux API is available
                cmd = [
                    "termux-notification",
                    "--title", title,
                    "--content", content,
                    "--priority", priority,
                    "--sound" if self.config["sound_enabled"] else "--no-sound",
                    "--vibrate" if self.config["vibration_enabled"] else "--no-vibrate"
                ]
                subprocess.run(cmd, check=True)
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        return False
    
    def send_local_notification(self, title: str, content: str, priority: str = "default"):
        """Send local notification using system commands"""
        try:
            # Try different notification methods
            methods = [
                ["notify-send", title, content],
                ["echo", f"NOTIFICATION: {title} - {content}"],
                ["logger", f"Racing Scanner: {title} - {content}"]
            ]
            
            for method in methods:
                try:
                    subprocess.run(method, check=True, timeout=5)
                    return True
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    continue
        except Exception as e:
            print(f"Warning: Could not send local notification: {e}")
        
        return False
    
    def notify(self, title: str, content: str, notification_type: str = "info", priority: str = "default"):
        """Send a notification"""
        if not self.config["enabled"]:
            return False
        
        # Check notification type settings
        if notification_type in self.config["notification_types"]:
            if not self.config["notification_types"][notification_type]:
                return False
        
        # Check quiet hours
        if self.is_quiet_hours() and priority != "high":
            return False
        
        # Try Termux notification first, then fallback to local
        success = self.send_termux_notification(title, content, priority)
        if not success:
            success = self.send_local_notification(title, content, priority)
        
        # Log notification
        self.log_notification(title, content, notification_type, success)
        
        return success
    
    def log_notification(self, title: str, content: str, notification_type: str, success: bool):
        """Log notification attempt"""
        log_file = self.config_dir / "notifications.log"
        timestamp = datetime.now().isoformat()
        status = "SUCCESS" if success else "FAILED"
        
        log_entry = f"[{timestamp}] {status} - {notification_type.upper()}: {title} - {content}\n"
        
        try:
            with open(log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not log notification: {e}")
    
    def notify_high_value_races(self, races: List[Dict], scan_stats: Dict):
        """Notify about high-value races found"""
        if not races:
            return
        
        # Count races by value level
        extreme_count = len([r for r in races if r.get('value_score', 0) >= self.config["extreme_value_threshold"]])
        high_count = len([r for r in races if r.get('value_score', 0) >= self.config["high_value_threshold"]])
        
        if extreme_count > 0:
            title = "🔥 EXTREME VALUE RACES FOUND!"
            content = f"{extreme_count} extreme value races (90+ score) found in latest scan"
            self.notify(title, content, "extreme_value", "high")
        
        elif high_count > 0:
            title = "🎯 High Value Races Found"
            content = f"{high_count} high value races (70+ score) found in latest scan"
            self.notify(title, content, "high_value", "default")
        
        # Show top race
        if races:
            top_race = max(races, key=lambda r: r.get('value_score', 0))
            score = top_race.get('value_score', 0)
            course = top_race.get('course', 'Unknown')
            time_str = top_race.get('local_time', 'Unknown')
            
            title = f"🏆 Top Race: {course}"
            content = f"Score: {score:.0f}★ | Time: {time_str} | {top_race.get('field_size', 0)} runners"
            self.notify(title, content, "high_value", "default")
    
    def notify_scan_complete(self, scan_stats: Dict):
        """Notify about scan completion"""
        if not self.config["notification_types"]["scan_complete"]:
            return
        
        total_races = scan_stats.get('total_races_found', 0)
        unique_races = scan_stats.get('races_after_dedup', 0)
        duration = scan_stats.get('duration_seconds', 0)
        
        title = "✅ Scan Complete"
        content = f"Found {total_races} races ({unique_races} unique) in {duration:.1f}s"
        self.notify(title, content, "scan_complete", "default")
    
    def notify_error(self, error_message: str):
        """Notify about errors"""
        if not self.config["notification_types"]["errors"]:
            return
        
        title = "❌ Scan Error"
        content = error_message[:100] + "..." if len(error_message) > 100 else error_message
        self.notify(title, content, "errors", "high")
    
    def update_config(self, **kwargs):
        """Update notification configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        
        self.save_config()
    
    def get_status(self) -> Dict:
        """Get notification system status"""
        return {
            "enabled": self.config["enabled"],
            "config_file": str(self.config_file),
            "quiet_hours": self.is_quiet_hours(),
            "notification_types": self.config["notification_types"]
        }

# Command line interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mobile Notifications for Racing Scanner")
    parser.add_argument("--test", action="store_true", help="Send test notification")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    parser.add_argument("--enable", action="store_true", help="Enable notifications")
    parser.add_argument("--disable", action="store_true", help="Disable notifications")
    parser.add_argument("--set-threshold", type=int, help="Set high value threshold")
    parser.add_argument("--quiet-hours", nargs=2, metavar=("START", "END"), 
                       help="Set quiet hours (e.g., 22:00 07:00)")
    
    args = parser.parse_args()
    
    notifier = MobileNotifier()
    
    if args.test:
        print("Sending test notification...")
        success = notifier.notify("Test Notification", "This is a test notification from Racing Scanner")
        print(f"Notification sent: {'Success' if success else 'Failed'}")
    
    elif args.config:
        print("Current notification configuration:")
        print(json.dumps(notifier.config, indent=2))
        print(f"\nStatus: {notifier.get_status()}")
    
    elif args.enable:
        notifier.update_config(enabled=True)
        print("Notifications enabled")
    
    elif args.disable:
        notifier.update_config(enabled=False)
        print("Notifications disabled")
    
    elif args.set_threshold:
        notifier.update_config(high_value_threshold=args.set_threshold)
        print(f"High value threshold set to {args.set_threshold}")
    
    elif args.quiet_hours:
        start, end = args.quiet_hours
        notifier.update_config(quiet_hours={
            "enabled": True,
            "start": start,
            "end": end
        })
        print(f"Quiet hours set to {start} - {end}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()