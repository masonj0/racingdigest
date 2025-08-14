#!/usr/bin/env python3
"""
Mobile Settings Configuration for Racing Scanner

Provides an easy way to configure mobile-specific settings
for the racing scanner without editing code files.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

class MobileSettings:
    """Manages mobile-specific settings for the racing scanner"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".racing_scanner"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "mobile_settings.json"
        self.load_config()
    
    def load_config(self):
        """Load mobile settings configuration"""
        default_config = {
            "performance": {
                "max_concurrent_requests": 6,
                "request_timeout": 45.0,
                "max_retries": 2,
                "retry_backoff_base": 1.5
            },
            "caching": {
                "default_ttl": 3600,  # 1 hour
                "manual_fetch_ttl": 43200,  # 12 hours
                "enabled": True
            },
            "filters": {
                "min_field_size": 4,
                "max_field_size": 6,
                "min_value_score": 60
            },
            "output": {
                "mobile_output_dir": "/sdcard/Download/RacingScanner",
                "auto_open_browser": False,
                "save_to_shared_storage": True
            },
            "ui": {
                "auto_refresh_interval": 300,  # 5 minutes
                "touch_target_size": 44,
                "dark_mode_enabled": True,
                "pwa_enabled": True
            },
            "background": {
                "enabled": True,
                "scan_interval": 1800,  # 30 minutes
                "racing_hours_start": 6,
                "racing_hours_end": 22,
                "only_during_racing_hours": True
            },
            "notifications": {
                "enabled": True,
                "high_value_threshold": 70,
                "extreme_value_threshold": 90,
                "sound_enabled": True,
                "vibration_enabled": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Deep merge with defaults
                    self.config = self.deep_merge(default_config, loaded_config)
            except Exception as e:
                print(f"Warning: Could not load mobile settings: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def deep_merge(self, default: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """Save mobile settings configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save mobile settings: {e}")
    
    def get_setting(self, path: str, default: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'performance.max_concurrent_requests')"""
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_setting(self, path: str, value: Any):
        """Set a setting value using dot notation"""
        keys = path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        self.save_config()
    
    def get_performance_preset(self, preset: str) -> Dict:
        """Get performance preset settings"""
        presets = {
            "battery_saver": {
                "max_concurrent_requests": 3,
                "request_timeout": 60.0,
                "max_retries": 1,
                "retry_backoff_base": 2.0
            },
            "balanced": {
                "max_concurrent_requests": 6,
                "request_timeout": 45.0,
                "max_retries": 2,
                "retry_backoff_base": 1.5
            },
            "performance": {
                "max_concurrent_requests": 8,
                "request_timeout": 30.0,
                "max_retries": 3,
                "retry_backoff_base": 1.2
            }
        }
        
        return presets.get(preset, presets["balanced"])
    
    def apply_performance_preset(self, preset: str):
        """Apply a performance preset"""
        preset_config = self.get_performance_preset(preset)
        for key, value in preset_config.items():
            self.set_setting(f"performance.{key}", value)
        print(f"Applied {preset} performance preset")
    
    def get_device_recommendations(self) -> Dict:
        """Get device-specific recommendations"""
        import psutil
        
        recommendations = {
            "performance_preset": "balanced",
            "max_concurrent_requests": 6,
            "caching_enabled": True
        }
        
        # Check available memory
        memory_gb = psutil.virtual_memory().total / (1024**3)
        if memory_gb < 2:
            recommendations["performance_preset"] = "battery_saver"
            recommendations["max_concurrent_requests"] = 3
        elif memory_gb > 6:
            recommendations["performance_preset"] = "performance"
            recommendations["max_concurrent_requests"] = 8
        
        # Check if we're on a mobile device (Termux)
        if os.path.exists("/data/data/com.termux"):
            recommendations["performance_preset"] = "battery_saver"
            recommendations["max_concurrent_requests"] = 4
        
        return recommendations
    
    def auto_configure(self):
        """Auto-configure settings based on device capabilities"""
        recommendations = self.get_device_recommendations()
        
        print("Auto-configuring mobile settings...")
        print(f"Recommended preset: {recommendations['performance_preset']}")
        
        self.apply_performance_preset(recommendations["performance_preset"])
        
        # Set recommended concurrent requests
        self.set_setting("performance.max_concurrent_requests", 
                        recommendations["max_concurrent_requests"])
        
        print("Auto-configuration complete!")
    
    def export_config(self, output_file: str = None):
        """Export current configuration"""
        if not output_file:
            output_file = f"mobile_settings_export_{int(time.time())}.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration exported to: {output_file}")
        except Exception as e:
            print(f"Error exporting configuration: {e}")
    
    def import_config(self, input_file: str):
        """Import configuration from file"""
        try:
            with open(input_file, 'r') as f:
                imported_config = json.load(f)
            
            self.config = self.deep_merge(self.config, imported_config)
            self.save_config()
            print(f"Configuration imported from: {input_file}")
        except Exception as e:
            print(f"Error importing configuration: {e}")
    
    def show_config(self, section: str = None):
        """Show current configuration"""
        if section:
            if section in self.config:
                print(f"\n=== {section.upper()} SETTINGS ===")
                print(json.dumps(self.config[section], indent=2))
            else:
                print(f"Section '{section}' not found")
        else:
            print("\n=== MOBILE SETTINGS CONFIGURATION ===")
            print(json.dumps(self.config, indent=2))
    
    def validate_config(self) -> bool:
        """Validate current configuration"""
        errors = []
        
        # Validate performance settings
        if self.config["performance"]["max_concurrent_requests"] < 1:
            errors.append("max_concurrent_requests must be at least 1")
        
        if self.config["performance"]["request_timeout"] < 10:
            errors.append("request_timeout must be at least 10 seconds")
        
        # Validate filter settings
        if self.config["filters"]["min_field_size"] > self.config["filters"]["max_field_size"]:
            errors.append("min_field_size cannot be greater than max_field_size")
        
        # Validate background settings
        if self.config["background"]["racing_hours_start"] > self.config["background"]["racing_hours_end"]:
            errors.append("racing_hours_start cannot be greater than racing_hours_end")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("Configuration validation passed!")
        return True

def main():
    import argparse
    import time
    
    parser = argparse.ArgumentParser(description="Mobile Settings Configuration")
    parser.add_argument("--show", nargs="?", const="all", metavar="SECTION",
                       help="Show configuration (optional section name)")
    parser.add_argument("--get", metavar="PATH", help="Get specific setting (e.g., performance.max_concurrent_requests)")
    parser.add_argument("--set", nargs=2, metavar=("PATH", "VALUE"),
                       help="Set specific setting (e.g., performance.max_concurrent_requests 8)")
    parser.add_argument("--preset", choices=["battery_saver", "balanced", "performance"],
                       help="Apply performance preset")
    parser.add_argument("--auto", action="store_true", help="Auto-configure based on device")
    parser.add_argument("--validate", action="store_true", help="Validate current configuration")
    parser.add_argument("--export", metavar="FILE", help="Export configuration to file")
    parser.add_argument("--import", dest="import_file", metavar="FILE", help="Import configuration from file")
    
    args = parser.parse_args()
    
    settings = MobileSettings()
    
    if args.show:
        settings.show_config(args.show if args.show != "all" else None)
    
    elif args.get:
        value = settings.get_setting(args.get)
        print(f"{args.get}: {value}")
    
    elif args.set:
        path, value = args.set
        # Try to convert value to appropriate type
        try:
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass  # Keep as string
        
        settings.set_setting(path, value)
        print(f"Set {path} = {value}")
    
    elif args.preset:
        settings.apply_performance_preset(args.preset)
    
    elif args.auto:
        settings.auto_configure()
    
    elif args.validate:
        settings.validate_config()
    
    elif args.export:
        settings.export_config(args.export)
    
    elif args.import_file:
        settings.import_config(args.import_file)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()