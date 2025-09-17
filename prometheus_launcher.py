#!/usr/bin/env python3
"""
Prometheus Launcher
Main entry point for the Prometheus AI monitoring system
"""

import os
import sys
import threading
import time
import signal
from pathlib import Path
from prometheus_core import PrometheusCore
from hephaestus import HephaestusCore
from prometheus_web import run_web_interface, web_interface


class PrometheusLauncher:
    """Main launcher for Prometheus system"""
    
    def __init__(self):
        self.prometheus = None
        self.hephaestus = None
        self.web_thread = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def initialize_environment(self):
        """Initialize the environment and check dependencies"""
        print("🔥 Initializing Prometheus Environment")
        print("=" * 50)
        
        # Create necessary directories
        directories = [
            "/workspace/prometheus_logs",
            "/workspace/prometheus_data",
            "/workspace/generated_prompts",
            "/workspace/templates"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            print(f"📁 Directory ready: {directory}")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
            print(f"❌ Python 3.7+ required, found {python_version.major}.{python_version.minor}")
            return False
        
        print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check and install dependencies
        try:
            import flask, cryptography, watchdog, psutil, requests
            print("✅ Core dependencies available")
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            print("💡 Run: pip install -r requirements.txt")
            return False
        
        return True
    
    def start_systems(self):
        """Start all Prometheus systems"""
        print("\n🚀 Starting Prometheus Systems")
        print("=" * 50)
        
        try:
            # Initialize Prometheus Core
            print("🔥 Initializing Prometheus Core...")
            self.prometheus = PrometheusCore()
            self.prometheus.start_system()
            print("✅ Prometheus Core started")
            
            # Initialize Hephaestus
            print("🔨 Initializing Hephaestus...")
            self.hephaestus = HephaestusCore()
            self.prometheus.register_module("Hephaestus", "PROJECT_CONVERTER", "1.0.0")
            print("✅ Hephaestus initialized")
            
            # Start web interface in separate thread
            print("🌐 Starting Web Interface...")
            self.web_thread = threading.Thread(target=self._run_web_interface, daemon=True)
            self.web_thread.start()
            time.sleep(2)  # Give web server time to start
            print("✅ Web Interface started on http://localhost:5000")
            
            self.running = True
            return True
            
        except Exception as e:
            print(f"❌ Error starting systems: {e}")
            return False
    
    def _run_web_interface(self):
        """Run web interface in thread"""
        try:
            # Set up web interface with our instances
            web_interface.prometheus = self.prometheus
            web_interface.hephaestus = self.hephaestus
            web_interface.is_running = True
            
            # Import and run
            from prometheus_web import app, socketio
            socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            print(f"❌ Web interface error: {e}")
    
    def run_autonomous_mode(self):
        """Run in autonomous monitoring mode"""
        print("\n🤖 Entering Autonomous Mode")
        print("=" * 50)
        print("🔍 Monitoring all systems...")
        print("🌐 Web interface: http://localhost:5000")
        print("📊 CLI available: python prometheus_cli.py status")
        print("🛑 Press Ctrl+C to shutdown gracefully")
        
        try:
            heartbeat_counter = 0
            while self.running:
                # Heartbeat every 60 seconds
                if heartbeat_counter % 60 == 0:
                    status = self.prometheus.get_system_status()
                    alerts = len(self.prometheus.database.get_active_alerts())
                    
                    print(f"💓 Heartbeat - Uptime: {status['uptime']}, "
                          f"Modules: {status['modules']}, Active Alerts: {alerts}")
                    
                    # Auto-generate example prompts periodically for testing
                    if heartbeat_counter % 300 == 0 and heartbeat_counter > 0:  # Every 5 minutes
                        self._generate_example_prompt()
                
                time.sleep(1)
                heartbeat_counter += 1
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
        except Exception as e:
            print(f"❌ Error in autonomous mode: {e}")
    
    def _generate_example_prompt(self):
        """Generate an example prompt for testing"""
        try:
            example_projects = [
                ("Task Manager App", "Create a simple task management application with user authentication, task creation, editing, and deletion. Include due dates and priority levels."),
                ("Weather Dashboard", "Build a weather dashboard that shows current weather and 5-day forecast. Include location search and favorite locations."),
                ("Expense Tracker", "Develop an expense tracking application with categories, monthly budgets, and spending analytics.")
            ]
            
            import random
            project_name, description = random.choice(example_projects)
            
            print(f"🔨 Auto-generating example prompt: {project_name}")
            prompt = self.hephaestus.generate_cursor_prompt(project_name, description)
            file_path = self.hephaestus.save_prompt_to_file(prompt)
            print(f"📄 Example prompt saved: {file_path}")
            
        except Exception as e:
            print(f"❌ Error generating example prompt: {e}")
    
    def shutdown(self):
        """Shutdown all systems gracefully"""
        print("\n🛑 Shutting down Prometheus systems...")
        
        self.running = False
        
        if self.prometheus:
            self.prometheus.stop_system()
            print("✅ Prometheus Core stopped")
        
        if self.web_thread and self.web_thread.is_alive():
            print("✅ Web interface stopping...")
        
        print("👋 Prometheus shutdown complete")
    
    def show_banner(self):
        """Show startup banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    🔥 PROMETHEUS - MONITORING & ARCHITECT AI SYSTEM 🔥       ║
║                                                               ║
║    Autonomous AI system for creating and monitoring          ║
║    all subsequent modules with full operational oversight     ║
║                                                               ║
║    🔨 Hephaestus: Project → Cursor Prompt Converter          ║
║    🛡️  Security: Continuous threat monitoring                ║
║    📊 Analytics: Comprehensive system logging                ║
║    🌐 Interface: Web dashboard + CLI control                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)


def main():
    """Main entry point"""
    launcher = PrometheusLauncher()
    
    # Show banner
    launcher.show_banner()
    
    # Initialize environment
    if not launcher.initialize_environment():
        sys.exit(1)
    
    # Start systems
    if not launcher.start_systems():
        sys.exit(1)
    
    # Run autonomous mode
    try:
        launcher.run_autonomous_mode()
    finally:
        launcher.shutdown()


if __name__ == "__main__":
    main()