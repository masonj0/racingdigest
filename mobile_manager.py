#!/usr/bin/env python3
"""
Mobile Manager for Racing Scanner

Provides a unified interface for managing all aspects of the mobile racing scanner,
including settings, notifications, monitoring, and data export.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class MobileManager:
    """Unified manager for mobile racing scanner features"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.config_dir = Path.home() / ".racing_scanner"
        self.config_dir.mkdir(exist_ok=True)
    
    def run_command(self, command: List[str], capture_output: bool = False) -> Dict:
        """Run a command and return results"""
        try:
            if capture_output:
                result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            else:
                result = subprocess.run(command, check=True)
                return {"success": True, "returncode": 0}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e), "returncode": e.returncode}
        except FileNotFoundError:
            return {"success": False, "error": "Command not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        info = {
            "platform": os.name,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "is_termux": os.path.exists("/data/data/com.termux"),
            "script_directory": str(self.script_dir),
            "config_directory": str(self.config_dir)
        }
        
        # Try to get more detailed system info
        try:
            import psutil
            info.update({
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2)
            })
        except ImportError:
            info["psutil_available"] = False
        
        return info
    
    def check_dependencies(self) -> Dict:
        """Check if all required dependencies are available"""
        dependencies = {
            "python": {"command": ["python3", "--version"], "required": True},
            "pip": {"command": ["pip", "--version"], "required": True},
            "git": {"command": ["git", "--version"], "required": False},
            "termux-api": {"command": ["termux-notification"], "required": False}
        }
        
        results = {}
        for name, config in dependencies.items():
            result = self.run_command(config["command"], capture_output=True)
            results[name] = {
                "available": result["success"],
                "required": config["required"],
                "version": result.get("stdout", "").strip() if result["success"] else None
            }
        
        return results
    
    def get_status(self) -> Dict:
        """Get comprehensive status of the mobile racing scanner"""
        status = {
            "system_info": self.get_system_info(),
            "dependencies": self.check_dependencies(),
            "services": {},
            "files": {}
        }
        
        # Check service status
        if (self.script_dir / "background_service.sh").exists():
            result = self.run_command(["./background_service.sh", "status"], capture_output=True)
            status["services"]["background_service"] = {
                "available": True,
                "running": "RUNNING" in result.get("stdout", "")
            }
        else:
            status["services"]["background_service"] = {"available": False}
        
        # Check file status
        mobile_files = [
            "racing_scanner_mobile.py",
            "launcher.sh", 
            "background_service.sh",
            "mobile_notifications.py",
            "mobile_settings.py",
            "mobile_monitor.py",
            "mobile_export.py"
        ]
        
        for file_name in mobile_files:
            file_path = self.script_dir / file_name
            status["files"][file_name] = {
                "exists": file_path.exists(),
                "executable": file_path.exists() and os.access(file_path, os.X_OK),
                "size_bytes": file_path.stat().st_size if file_path.exists() else 0
            }
        
        return status
    
    def setup_mobile(self) -> Dict:
        """Complete mobile setup"""
        print("🚀 Setting up Mobile Racing Scanner...")
        
        results = {
            "launcher_setup": False,
            "settings_configured": False,
            "notifications_configured": False,
            "icons_created": False,
            "permissions_set": False
        }
        
        # 1. Run launcher setup
        print("📦 Installing dependencies...")
        launcher_result = self.run_command(["./launcher.sh", "setup"])
        results["launcher_setup"] = launcher_result["success"]
        
        if not results["launcher_setup"]:
            print("❌ Launcher setup failed")
            return results
        
        # 2. Configure mobile settings
        print("⚙️  Configuring mobile settings...")
        settings_result = self.run_command(["python3", "mobile_settings.py", "--auto"])
        results["settings_configured"] = settings_result["success"]
        
        # 3. Configure notifications
        print("🔔 Configuring notifications...")
        notif_result = self.run_command(["python3", "mobile_notifications.py", "--enable"])
        results["notifications_configured"] = notif_result["success"]
        
        # 4. Create PWA icons
        print("🎨 Creating PWA icons...")
        icons_result = self.run_command(["./create_icons.sh"])
        results["icons_created"] = icons_result["success"]
        
        # 5. Set permissions
        print("🔐 Setting file permissions...")
        permission_files = [
            "launcher.sh",
            "background_service.sh", 
            "create_icons.sh"
        ]
        
        for file_name in permission_files:
            file_path = self.script_dir / file_name
            if file_path.exists():
                try:
                    os.chmod(file_path, 0o755)
                except Exception:
                    pass
        
        results["permissions_set"] = True
        
        print("✅ Mobile setup completed!")
        return results
    
    def run_scan(self, options: Dict = None) -> Dict:
        """Run a scan with optional parameters"""
        if options is None:
            options = {}
        
        command = ["./launcher.sh", "run"]
        
        # Add custom options if provided
        if options.get("verbose"):
            command.extend(["--verbose"])
        
        print("🔍 Running scan...")
        result = self.run_command(command, capture_output=True)
        
        return {
            "success": result["success"],
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "returncode": result.get("returncode", 0)
        }
    
    def manage_background_service(self, action: str) -> Dict:
        """Manage background service"""
        if action not in ["start", "stop", "status", "restart"]:
            return {"success": False, "error": "Invalid action"}
        
        command = ["./background_service.sh", action]
        result = self.run_command(command, capture_output=True)
        
        return {
            "success": result["success"],
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "action": action
        }
    
    def configure_notifications(self, **kwargs) -> Dict:
        """Configure notification settings"""
        command = ["python3", "mobile_notifications.py"]
        
        if kwargs.get("enable"):
            command.append("--enable")
        elif kwargs.get("disable"):
            command.append("--disable")
        elif kwargs.get("test"):
            command.append("--test")
        elif kwargs.get("threshold"):
            command.extend(["--set-threshold", str(kwargs["threshold"])])
        elif kwargs.get("quiet_hours"):
            start, end = kwargs["quiet_hours"]
            command.extend(["--quiet-hours", start, end])
        else:
            command.append("--config")
        
        result = self.run_command(command, capture_output=True)
        
        return {
            "success": result["success"],
            "output": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
    
    def configure_settings(self, **kwargs) -> Dict:
        """Configure mobile settings"""
        command = ["python3", "mobile_settings.py"]
        
        if kwargs.get("preset"):
            command.extend(["--preset", kwargs["preset"]])
        elif kwargs.get("auto"):
            command.append("--auto")
        elif kwargs.get("validate"):
            command.append("--validate")
        elif kwargs.get("get"):
            command.extend(["--get", kwargs["get"]])
        elif kwargs.get("set"):
            path, value = kwargs["set"]
            command.extend(["--set", path, str(value)])
        else:
            command.append("--show")
        
        result = self.run_command(command, capture_output=True)
        
        return {
            "success": result["success"],
            "output": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
    
    def get_performance_report(self) -> Dict:
        """Get performance report"""
        command = ["python3", "mobile_monitor.py", "--report"]
        result = self.run_command(command, capture_output=True)
        
        return {
            "success": result["success"],
            "report": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
    
    def export_data(self, format_type: str = "all", days: int = 7) -> Dict:
        """Export data in specified format"""
        command = ["python3", "mobile_export.py"]
        
        if format_type == "all":
            command.append("--all")
        elif format_type == "csv":
            command.append("--csv")
        elif format_type == "json":
            command.append("--json")
        elif format_type == "sqlite":
            command.append("--sqlite")
        
        command.extend(["--days", str(days)])
        
        result = self.run_command(command, capture_output=True)
        
        return {
            "success": result["success"],
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "format": format_type
        }
    
    def cleanup(self, days: int = 30) -> Dict:
        """Clean up old data and exports"""
        results = {}
        
        # Clean up performance data
        monitor_result = self.run_command(["python3", "mobile_monitor.py", "--cleanup", str(days)])
        results["performance_data"] = monitor_result["success"]
        
        # Clean up exports
        export_result = self.run_command(["python3", "mobile_export.py", "--cleanup", str(days)])
        results["exports"] = export_result["success"]
        
        # Clean up cache
        cache_dir = self.script_dir / ".cache_v7_final"
        if cache_dir.exists():
            try:
                # Remove files older than specified days
                import time
                cutoff_time = time.time() - (days * 24 * 60 * 60)
                
                cleaned_count = 0
                for file_path in cache_dir.glob("*"):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                
                results["cache"] = {"success": True, "files_removed": cleaned_count}
            except Exception as e:
                results["cache"] = {"success": False, "error": str(e)}
        
        return results
    
    def get_help(self) -> str:
        """Get help information"""
        return """
🎯 Mobile Racing Scanner Manager

Available Commands:
  setup                    - Complete mobile setup
  status                   - Show system status
  scan [--verbose]         - Run a scan
  service <action>         - Manage background service (start/stop/status/restart)
  notifications <action>   - Configure notifications
  settings <action>        - Configure mobile settings
  performance              - Get performance report
  export <format> [days]   - Export data (csv/json/sqlite/all)
  cleanup [days]           - Clean up old data
  help                     - Show this help

Examples:
  python3 mobile_manager.py setup
  python3 mobile_manager.py scan --verbose
  python3 mobile_manager.py service start
  python3 mobile_manager.py notifications --test
  python3 mobile_manager.py settings --preset battery_saver
  python3 mobile_manager.py export all 7
  python3 mobile_manager.py cleanup 30
"""

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Mobile Manager for Racing Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=MobileManager().get_help()
    )
    
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--preset", choices=["battery_saver", "balanced", "performance"], 
                       help="Performance preset for settings")
    parser.add_argument("--threshold", type=int, help="Notification threshold")
    parser.add_argument("--days", type=int, default=7, help="Number of days for export/cleanup")
    parser.add_argument("--format", choices=["csv", "json", "sqlite", "all"], default="all",
                       help="Export format")
    
    args = parser.parse_args()
    
    manager = MobileManager()
    
    if not args.command or args.command == "help":
        print(manager.get_help())
        return
    
    if args.command == "setup":
        results = manager.setup_mobile()
        print("Setup Results:")
        for key, value in results.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")
    
    elif args.command == "status":
        status = manager.get_status()
        print("System Status:")
        print(json.dumps(status, indent=2))
    
    elif args.command == "scan":
        options = {"verbose": args.verbose}
        result = manager.run_scan(options)
        if result["success"]:
            print("✅ Scan completed successfully")
            if args.verbose:
                print(result["output"])
        else:
            print(f"❌ Scan failed: {result.get('error', 'Unknown error')}")
    
    elif args.command == "service":
        if len(sys.argv) < 3:
            print("Error: service command requires an action (start/stop/status/restart)")
            return
        
        action = sys.argv[2]
        result = manager.manage_background_service(action)
        if result["success"]:
            print(f"✅ Service {action} completed")
            if result["output"]:
                print(result["output"])
        else:
            print(f"❌ Service {action} failed: {result.get('error', 'Unknown error')}")
    
    elif args.command == "notifications":
        options = {}
        if args.threshold:
            options["threshold"] = args.threshold
        elif "--test" in sys.argv:
            options["test"] = True
        elif "--enable" in sys.argv:
            options["enable"] = True
        elif "--disable" in sys.argv:
            options["disable"] = True
        
        result = manager.configure_notifications(**options)
        if result["success"]:
            print("✅ Notifications configured")
            if result["output"]:
                print(result["output"])
        else:
            print(f"❌ Notification configuration failed: {result.get('error', 'Unknown error')}")
    
    elif args.command == "settings":
        options = {}
        if args.preset:
            options["preset"] = args.preset
        elif "--auto" in sys.argv:
            options["auto"] = True
        elif "--validate" in sys.argv:
            options["validate"] = True
        
        result = manager.configure_settings(**options)
        if result["success"]:
            print("✅ Settings configured")
            if result["output"]:
                print(result["output"])
        else:
            print(f"❌ Settings configuration failed: {result.get('error', 'Unknown error')}")
    
    elif args.command == "performance":
        result = manager.get_performance_report()
        if result["success"]:
            print(result["report"])
        else:
            print(f"❌ Performance report failed: {result.get('error', 'Unknown error')}")
    
    elif args.command == "export":
        result = manager.export_data(args.format, args.days)
        if result["success"]:
            print("✅ Export completed")
            if result["output"]:
                print(result["output"])
        else:
            print(f"❌ Export failed: {result.get('error', 'Unknown error')}")
    
    elif args.command == "cleanup":
        results = manager.cleanup(args.days)
        print("Cleanup Results:")
        for key, value in results.items():
            if isinstance(value, dict):
                status = "✅" if value.get("success", False) else "❌"
                print(f"  {status} {key}: {value}")
            else:
                status = "✅" if value else "❌"
                print(f"  {status} {key}: {value}")
    
    else:
        print(f"Unknown command: {args.command}")
        print(manager.get_help())

if __name__ == "__main__":
    main()