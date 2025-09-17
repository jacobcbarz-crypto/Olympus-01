#!/usr/bin/env python3
"""
Prometheus CLI Interface
Command-line interface for system oversight and manual commands
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from prometheus_core import PrometheusCore
from hephaestus import HephaestusCore


class PrometheusCommandLineInterface:
    """Command-line interface for Prometheus"""
    
    def __init__(self):
        self.prometheus = None
        self.hephaestus = None
        
    def initialize_systems(self):
        """Initialize Prometheus and Hephaestus systems"""
        try:
            print("🔥 Initializing Prometheus systems...")
            
            self.prometheus = PrometheusCore()
            self.prometheus.start_system()
            
            self.hephaestus = HephaestusCore()
            self.prometheus.register_module("Hephaestus", "PROJECT_CONVERTER", "1.0.0")
            
            print("✅ Systems initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing systems: {e}")
            return False
    
    def show_status(self):
        """Show system status"""
        if not self.prometheus:
            print("❌ Prometheus not initialized")
            return
        
        print("\n🔥 PROMETHEUS SYSTEM STATUS")
        print("=" * 50)
        
        status = self.prometheus.get_system_status()
        print(f"Status: {status['prometheus_status']}")
        print(f"Uptime: {status['uptime']}")
        print(f"Modules: {status['modules']}")
        print(f"Active Alerts: {status['active_alerts']}")
        
        print(f"\nSystem Resources:")
        print(f"  CPU: {status['system_resources']['cpu']:.1f}%")
        print(f"  Memory: {status['system_resources']['memory']:.1f}%")
        print(f"  Disk: {status['system_resources']['disk']:.1f}%")
        
        # Show recent alerts
        alerts = self.prometheus.database.get_active_alerts()
        if alerts:
            print(f"\n⚠️  ACTIVE ALERTS ({len(alerts)}):")
            for alert in alerts[:5]:  # Show first 5
                print(f"  [{alert.severity}] {alert.description}")
        
        # Show Hephaestus stats
        if self.hephaestus:
            print(f"\n🔨 HEPHAESTUS STATISTICS")
            stats = self.hephaestus.get_generation_stats()
            print(f"  Total Generated: {stats['total_generated']}")
            print(f"  Success Rate: {stats['success_rate']}")
            print(f"  Average per Hour: {stats['avg_per_hour']:.1f}")
    
    def run_security_scan(self):
        """Run security vulnerability scan"""
        if not self.prometheus:
            print("❌ Prometheus not initialized")
            return
        
        print("🛡️  Running security vulnerability scan...")
        
        alerts = self.prometheus.security_monitor.scan_system_vulnerabilities()
        
        if alerts:
            print(f"⚠️  Found {len(alerts)} security issues:")
            for alert in alerts:
                print(f"  [{alert.severity}] {alert.description}")
                self.prometheus.database.insert_security_alert(alert)
        else:
            print("✅ No security vulnerabilities detected")
    
    def generate_prompt(self, project_name: str, description_file: str = None, description_text: str = None):
        """Generate Cursor prompt from project description"""
        if not self.hephaestus:
            print("❌ Hephaestus not initialized")
            return
        
        # Get project description
        if description_file:
            try:
                with open(description_file, 'r') as f:
                    description = f.read()
                print(f"📄 Loaded description from: {description_file}")
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                return
        elif description_text:
            description = description_text
        else:
            print("❌ No project description provided")
            return
        
        try:
            print(f"🔨 Generating Cursor prompt for: {project_name}")
            
            prompt = self.hephaestus.generate_cursor_prompt(project_name, description)
            
            # Save to file
            file_path = self.hephaestus.save_prompt_to_file(prompt)
            
            print(f"✅ Prompt generated successfully!")
            print(f"📁 Saved to: {file_path}")
            print(f"🏷️  Prompt ID: {prompt.prompt_id}")
            print(f"🔧 Complexity: {prompt.estimated_complexity}")
            print(f"🔒 Security Level: {prompt.security_level}")
            
        except Exception as e:
            print(f"❌ Error generating prompt: {e}")
    
    def list_modules(self):
        """List all registered modules"""
        if not self.prometheus:
            print("❌ Prometheus not initialized")
            return
        
        print("\n🧩 REGISTERED MODULES")
        print("=" * 50)
        
        if not self.prometheus.modules:
            print("No modules registered")
            return
        
        for name, info in self.prometheus.modules.items():
            print(f"📦 {name}")
            print(f"   Type: {info['type']}")
            print(f"   Version: {info['version']}")
            print(f"   Status: {info['status']}")
            print(f"   Last Updated: {info['last_updated']}")
            print()
    
    def show_logs(self, log_type: str = "system", lines: int = 50):
        """Show recent log entries"""
        log_dir = Path("/workspace/prometheus_logs")
        log_file_map = {
            "system": "prometheus_system.log",
            "security": "prometheus_security.log",
            "performance": "prometheus_performance.log",
            "alerts": "prometheus_alerts.log"
        }
        
        log_file = log_dir / log_file_map.get(log_type, "prometheus_system.log")
        
        if not log_file.exists():
            print(f"❌ Log file not found: {log_file}")
            return
        
        print(f"\n📋 {log_type.upper()} LOGS (last {lines} lines)")
        print("=" * 60)
        
        try:
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
            for line in recent_lines:
                print(line.rstrip())
                
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    
    def monitor_mode(self, interval: int = 10):
        """Enter continuous monitoring mode"""
        if not self.prometheus:
            print("❌ Prometheus not initialized")
            return
        
        print(f"📊 Entering monitoring mode (refresh every {interval}s)")
        print("Press Ctrl+C to exit")
        
        try:
            while True:
                # Clear screen (works on most terminals)
                print("\033[2J\033[H")
                
                print(f"🔥 PROMETHEUS LIVE MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 70)
                
                self.show_status()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Exiting monitoring mode")
    
    def shutdown_system(self):
        """Shutdown Prometheus system"""
        if self.prometheus:
            print("🛑 Shutting down Prometheus system...")
            self.prometheus.stop_system()
            print("✅ System shutdown complete")
        else:
            print("❌ No system to shutdown")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Prometheus CLI - Monitoring and Architect AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  prometheus_cli.py status                    # Show system status
  prometheus_cli.py scan                      # Run security scan
  prometheus_cli.py generate "My App" -f description.txt
  prometheus_cli.py generate "My App" -d "Create a web app..."
  prometheus_cli.py logs --type security      # Show security logs
  prometheus_cli.py monitor --interval 5      # Monitor mode (5s refresh)
  prometheus_cli.py modules                   # List registered modules
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Security scan command
    subparsers.add_parser('scan', help='Run security vulnerability scan')
    
    # Generate prompt command
    gen_parser = subparsers.add_parser('generate', help='Generate Cursor prompt')
    gen_parser.add_argument('project_name', help='Name of the project')
    gen_parser.add_argument('-f', '--file', help='File containing project description')
    gen_parser.add_argument('-d', '--description', help='Project description text')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show log entries')
    logs_parser.add_argument('--type', choices=['system', 'security', 'performance', 'alerts'], 
                           default='system', help='Type of logs to show')
    logs_parser.add_argument('--lines', type=int, default=50, help='Number of lines to show')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Enter continuous monitoring mode')
    monitor_parser.add_argument('--interval', type=int, default=10, help='Refresh interval in seconds')
    
    # Modules command
    subparsers.add_parser('modules', help='List registered modules')
    
    # Shutdown command
    subparsers.add_parser('shutdown', help='Shutdown Prometheus system')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = PrometheusCommandLineInterface()
    
    # Handle shutdown command without initialization
    if args.command == 'shutdown':
        cli.shutdown_system()
        return
    
    # Initialize systems for other commands
    if not cli.initialize_systems():
        sys.exit(1)
    
    try:
        # Execute commands
        if args.command == 'status':
            cli.show_status()
        
        elif args.command == 'scan':
            cli.run_security_scan()
        
        elif args.command == 'generate':
            cli.generate_prompt(args.project_name, args.file, args.description)
        
        elif args.command == 'logs':
            cli.show_logs(args.type, args.lines)
        
        elif args.command == 'monitor':
            cli.monitor_mode(args.interval)
        
        elif args.command == 'modules':
            cli.list_modules()
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup
        if cli.prometheus:
            cli.prometheus.stop_system()


if __name__ == "__main__":
    main()