#!/usr/bin/env python3
"""
Android Deployment System for Prometheus
APK generation and mobile deployment capabilities
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import tempfile


class AndroidAPKBuilder:
    """Builds Android APK for Prometheus monitoring system"""
    
    def __init__(self, prometheus_instance=None):
        self.prometheus = prometheus_instance
        self.build_dir = Path("/workspace/android_build")
        self.output_dir = Path("/workspace/android_output")
        self.config = self._load_android_config()
        
    def _load_android_config(self) -> Dict[str, Any]:
        """Load Android configuration from main config file"""
        try:
            config_file = Path("/workspace/prometheus_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    full_config = json.load(f)
                return full_config.get('android', {})
        except Exception as e:
            if self.prometheus:
                self.prometheus.logger.system_logger.error(f"Error loading Android config: {e}")
        
        # Default configuration
        return {
            "apk_generation_enabled": True,
            "package_name": "com.prometheus.monitoring",
            "app_name": "Prometheus Monitor",
            "version_code": 1,
            "version_name": "1.0.0",
            "min_sdk_version": 21,
            "target_sdk_version": 33,
            "permissions": [
                "android.permission.INTERNET",
                "android.permission.ACCESS_NETWORK_STATE",
                "android.permission.WRITE_EXTERNAL_STORAGE",
                "android.permission.READ_EXTERNAL_STORAGE",
                "android.permission.WAKE_LOCK",
                "android.permission.FOREGROUND_SERVICE",
                "android.permission.SYSTEM_ALERT_WINDOW"
            ]
        }
    
    def check_build_environment(self) -> Dict[str, Any]:
        """Check if build environment is ready"""
        status = {
            'ready': False,
            'issues': [],
            'requirements': []
        }
        
        # Check Python
        if sys.version_info < (3, 7):
            status['issues'].append("Python 3.7+ required")
        
        # Check if buildozer is available
        try:
            result = subprocess.run(['buildozer', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                status['issues'].append("Buildozer not installed or not working")
                status['requirements'].append("pip install buildozer")
        except FileNotFoundError:
            status['issues'].append("Buildozer not found")
            status['requirements'].append("pip install buildozer")
        except Exception as e:
            status['issues'].append(f"Buildozer check failed: {e}")
        
        # Check if Kivy is available (for mobile UI)
        try:
            import kivy
            status['kivy_version'] = kivy.__version__
        except ImportError:
            status['issues'].append("Kivy not installed")
            status['requirements'].append("pip install kivy")
        
        # Check Android SDK requirements
        android_home = os.environ.get('ANDROID_HOME')
        if not android_home:
            status['issues'].append("ANDROID_HOME not set")
            status['requirements'].append("Install Android SDK and set ANDROID_HOME")
        
        # Check Java
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                status['issues'].append("Java not installed or not working")
        except FileNotFoundError:
            status['issues'].append("Java not found")
            status['requirements'].append("Install Java JDK 8 or 11")
        
        status['ready'] = len(status['issues']) == 0
        
        return status
    
    def create_android_project(self) -> bool:
        """Create Android project structure"""
        try:
            # Create build directory
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            self.build_dir.mkdir(parents=True, exist_ok=True)
            
            # Create main Python app for Android
            self._create_main_app()
            
            # Create buildozer.spec configuration
            self._create_buildozer_spec()
            
            # Create Android-specific files
            self._create_android_resources()
            
            # Copy core Prometheus modules
            self._copy_core_modules()
            
            if self.prometheus:
                self.prometheus.logger.system_logger.info("Android project structure created")
            
            return True
            
        except Exception as e:
            if self.prometheus:
                self.prometheus.logger.system_logger.error(f"Error creating Android project: {e}")
            return False
    
    def _create_main_app(self):
        """Create main Android application file"""
        main_app = '''#!/usr/bin/env python3
"""
Prometheus Android App
Mobile monitoring interface for Prometheus AI system
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.logger import Logger
import json
import threading
import time
from datetime import datetime
import requests


class PrometheusMonitorApp(App):
    """Main Prometheus monitoring app for Android"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_url = "http://192.168.1.100:5000"  # Default server URL
        self.status_data = {}
        self.monitoring_active = False
        
    def build(self):
        """Build the main UI"""
        self.title = "Prometheus Monitor"
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(text='🔥 Prometheus Monitor', 
                     size_hint_y=None, height=50,
                     font_size='20sp')
        main_layout.add_widget(title)
        
        # Server URL input
        url_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        url_layout.add_widget(Label(text='Server:', size_hint_x=0.3))
        self.url_input = TextInput(text=self.server_url, multiline=False)
        url_layout.add_widget(self.url_input)
        main_layout.add_widget(url_layout)
        
        # Control buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        self.connect_btn = Button(text='Connect')
        self.connect_btn.bind(on_press=self.connect_to_server)
        button_layout.add_widget(self.connect_btn)
        
        self.monitor_btn = Button(text='Start Monitoring')
        self.monitor_btn.bind(on_press=self.toggle_monitoring)
        button_layout.add_widget(self.monitor_btn)
        
        self.refresh_btn = Button(text='Refresh')
        self.refresh_btn.bind(on_press=self.refresh_status)
        button_layout.add_widget(self.refresh_btn)
        
        main_layout.add_widget(button_layout)
        
        # Status display
        self.status_label = Label(text='Status: Disconnected', 
                                 size_hint_y=None, height=40)
        main_layout.add_widget(self.status_label)
        
        # Scrollable content area
        scroll = ScrollView()
        self.content_label = Label(text='Welcome to Prometheus Monitor\\n\\n'
                                       'Enter server URL and click Connect to start monitoring.',
                                  text_size=(None, None),
                                  valign='top')
        scroll.add_widget(self.content_label)
        main_layout.add_widget(scroll)
        
        return main_layout
    
    def connect_to_server(self, instance):
        """Connect to Prometheus server"""
        self.server_url = self.url_input.text.strip()
        
        try:
            response = requests.get(f"{self.server_url}/api/status", timeout=10)
            if response.status_code == 200:
                self.status_label.text = "Status: Connected ✅"
                self.connect_btn.text = "Connected"
                self.refresh_status(None)
            else:
                self.status_label.text = f"Status: Connection Failed ({response.status_code})"
        except Exception as e:
            self.status_label.text = f"Status: Connection Error - {str(e)[:50]}"
    
    def toggle_monitoring(self, instance):
        """Toggle monitoring mode"""
        if self.monitoring_active:
            self.monitoring_active = False
            self.monitor_btn.text = "Start Monitoring"
            self.status_label.text = "Status: Monitoring Stopped"
        else:
            self.monitoring_active = True
            self.monitor_btn.text = "Stop Monitoring"
            self.status_label.text = "Status: Monitoring Active 📊"
            
            # Start monitoring thread
            threading.Thread(target=self.monitoring_loop, daemon=True).start()
    
    def monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                Clock.schedule_once(lambda dt: self.refresh_status(None), 0)
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                Logger.error(f"Monitoring loop error: {e}")
                break
    
    def refresh_status(self, instance):
        """Refresh system status"""
        try:
            response = requests.get(f"{self.server_url}/api/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.status_data = data
                self.update_display(data)
            else:
                self.content_label.text = f"Error: HTTP {response.status_code}"
        except Exception as e:
            self.content_label.text = f"Error: {str(e)}"
    
    def update_display(self, data):
        """Update display with status data"""
        try:
            if not data:
                return
            
            # Format status information
            content = "🔥 PROMETHEUS STATUS\\n"
            content += "=" * 30 + "\\n\\n"
            
            # System status
            if 'system_status' in data:
                sys_status = data['system_status']
                content += f"System: {sys_status.get('prometheus_status', 'Unknown')}\\n"
                content += f"Uptime: {sys_status.get('uptime', 'Unknown')}\\n"
                content += f"Modules: {sys_status.get('modules', 0)}\\n"
                content += f"Alerts: {sys_status.get('active_alerts', 0)}\\n\\n"
                
                # Resource usage
                resources = sys_status.get('system_resources', {})
                content += "📊 RESOURCES:\\n"
                content += f"CPU: {resources.get('cpu', 0):.1f}%\\n"
                content += f"Memory: {resources.get('memory', 0):.1f}%\\n"
                content += f"Disk: {resources.get('disk', 0):.1f}%\\n\\n"
            
            # Alerts
            if 'alerts' in data and data['alerts']:
                content += f"⚠️ ACTIVE ALERTS ({len(data['alerts'])}):\\n"
                for alert in data['alerts'][:5]:  # Show first 5 alerts
                    content += f"[{alert.get('severity', 'UNKNOWN')}] {alert.get('description', 'No description')[:50]}...\\n"
                content += "\\n"
            
            # Hephaestus stats
            if 'hephaestus_stats' in data:
                hep_stats = data['hephaestus_stats']
                content += "🔨 HEPHAESTUS:\\n"
                content += f"Generated: {hep_stats.get('total_generated', 0)}\\n"
                content += f"Success Rate: {hep_stats.get('success_rate', '0%')}\\n"
                content += f"Avg/Hour: {hep_stats.get('avg_per_hour', 0):.1f}\\n\\n"
            
            # Modules
            if 'modules' in data and data['modules']:
                content += f"🧩 MODULES ({len(data['modules'])}):\\n"
                for module in data['modules'][:5]:  # Show first 5 modules
                    content += f"{module.get('name', 'Unknown')} v{module.get('version', '?')} - {module.get('status', 'Unknown')}\\n"
                content += "\\n"
            
            content += f"Last Updated: {datetime.now().strftime('%H:%M:%S')}"
            
            # Update display
            self.content_label.text = content
            self.content_label.text_size = (400, None)  # Set text width for wrapping
            
        except Exception as e:
            self.content_label.text = f"Display update error: {str(e)}"


if __name__ == '__main__':
    PrometheusMonitorApp().run()
'''
        
        with open(self.build_dir / "main.py", 'w') as f:
            f.write(main_app)
    
    def _create_buildozer_spec(self):
        """Create buildozer.spec configuration file"""
        spec_content = f'''[app]
# (str) Title of your application
title = {self.config['app_name']}

# (str) Package name
package.name = prometheus_monitor

# (str) Package domain (needed for android/ios packaging)
package.domain = {self.config['package_name']}

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = {self.config['version_name']}

# (list) Application requirements
requirements = python3,kivy,requests,urllib3,certifi,charset-normalizer,idna

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = {self.config['target_sdk_version']}

# (int) Minimum API your APK will support.
android.minapi = {self.config['min_sdk_version']}

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android SDK version to use
android.sdk = 33

# (str) Android permissions
android.permissions = {','.join(self.config['permissions'])}

# (str) Android application theme
android.theme = @android:style/Theme.NoTitleBar

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
android.enable_androidx = True

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
'''
        
        with open(self.build_dir / "buildozer.spec", 'w') as f:
            f.write(spec_content)
    
    def _create_android_resources(self):
        """Create Android-specific resource files"""
        # Create icon (simple text-based icon for now)
        icon_content = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:fillColor="#FF6B35"
          android:pathData="M0,0h108v108h-108z"/>
    <path android:fillColor="#FFFFFF"
          android:pathData="M54,20L54,88M20,54L88,54"/>
</vector>'''
        
        # Create resources directory
        res_dir = self.build_dir / "res"
        res_dir.mkdir(exist_ok=True)
        
        # Create a simple icon file (this would be replaced with actual icon)
        icon_file = self.build_dir / "icon.png"
        # For now, just create an empty file - in production, add actual icon
        icon_file.touch()
    
    def _copy_core_modules(self):
        """Copy essential Prometheus modules for Android"""
        # Copy lightweight versions of core modules
        modules_to_copy = [
            'prometheus_config.json'
        ]
        
        for module in modules_to_copy:
            src_path = Path(f"/workspace/{module}")
            if src_path.exists():
                dst_path = self.build_dir / module
                shutil.copy2(src_path, dst_path)
        
        # Create a lightweight Prometheus client for Android
        android_client = '''#!/usr/bin/env python3
"""
Lightweight Prometheus client for Android
"""

import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional


class PrometheusAndroidClient:
    """Lightweight client for communicating with Prometheus server"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
    
    def get_system_status(self) -> Optional[Dict[str, Any]]:
        """Get system status from server"""
        try:
            response = self.session.get(f"{self.server_url}/api/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting system status: {e}")
            return None
    
    def generate_prompt(self, project_name: str, description: str) -> Optional[Dict[str, Any]]:
        """Generate Cursor prompt via server"""
        try:
            data = {
                'project_name': project_name,
                'project_description': description
            }
            response = self.session.post(f"{self.server_url}/api/generate_prompt", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error generating prompt: {e}")
            return None
    
    def execute_system_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Execute system command on server"""
        try:
            data = {'command': command}
            response = self.session.post(f"{self.server_url}/api/system_command", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error executing command: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test connection to server"""
        try:
            response = self.session.get(f"{self.server_url}/api/status", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
'''
        
        with open(self.build_dir / "prometheus_client.py", 'w') as f:
            f.write(android_client)
    
    def build_apk(self, debug: bool = True) -> Dict[str, Any]:
        """Build Android APK"""
        result = {
            'success': False,
            'apk_path': None,
            'build_log': '',
            'errors': []
        }
        
        try:
            # Check build environment
            env_check = self.check_build_environment()
            if not env_check['ready']:
                result['errors'] = env_check['issues']
                return result
            
            # Create project if it doesn't exist
            if not (self.build_dir / "buildozer.spec").exists():
                if not self.create_android_project():
                    result['errors'].append("Failed to create Android project")
                    return result
            
            # Change to build directory
            original_cwd = os.getcwd()
            os.chdir(self.build_dir)
            
            try:
                # Build command
                build_cmd = ['buildozer', 'android', 'debug' if debug else 'release']
                
                if self.prometheus:
                    self.prometheus.logger.system_logger.info(f"Starting APK build: {' '.join(build_cmd)}")
                
                # Run buildozer
                process = subprocess.Popen(
                    build_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                build_output = []
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        build_output.append(output.strip())
                        if self.prometheus:
                            self.prometheus.logger.system_logger.info(f"Build: {output.strip()}")
                
                result['build_log'] = '\n'.join(build_output)
                
                # Check if build was successful
                if process.returncode == 0:
                    # Find generated APK
                    bin_dir = self.build_dir / "bin"
                    if bin_dir.exists():
                        apk_files = list(bin_dir.glob("*.apk"))
                        if apk_files:
                            # Copy APK to output directory
                            self.output_dir.mkdir(exist_ok=True)
                            apk_name = f"prometheus_monitor_v{self.config['version_name']}_{'debug' if debug else 'release'}.apk"
                            output_apk = self.output_dir / apk_name
                            shutil.copy2(apk_files[0], output_apk)
                            
                            result['success'] = True
                            result['apk_path'] = str(output_apk)
                            
                            if self.prometheus:
                                self.prometheus.logger.system_logger.info(f"APK built successfully: {output_apk}")
                        else:
                            result['errors'].append("APK file not found after build")
                    else:
                        result['errors'].append("Build output directory not found")
                else:
                    result['errors'].append(f"Build failed with return code {process.returncode}")
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            result['errors'].append(str(e))
            if self.prometheus:
                self.prometheus.logger.system_logger.error(f"APK build error: {e}")
        
        return result
    
    def create_installation_instructions(self, apk_path: str) -> str:
        """Create installation instructions for the APK"""
        instructions = f'''# Prometheus Monitor Android App Installation

## APK Information
- **File**: {Path(apk_path).name}
- **Version**: {self.config['version_name']}
- **Package**: {self.config['package_name']}
- **Min Android**: API {self.config['min_sdk_version']} (Android 5.0+)
- **Target Android**: API {self.config['target_sdk_version']}

## Installation Steps

### Method 1: Direct Installation
1. Copy the APK file to your Android device
2. Enable "Unknown Sources" in Settings > Security
3. Tap the APK file to install
4. Grant necessary permissions when prompted

### Method 2: ADB Installation
```bash
adb install {Path(apk_path).name}
```

## Permissions Required
The app requires the following permissions:
{chr(10).join(f"- {perm}" for perm in self.config['permissions'])}

## Usage
1. Launch the Prometheus Monitor app
2. Enter your Prometheus server URL (e.g., http://192.168.1.100:5000)
3. Tap "Connect" to establish connection
4. Use "Start Monitoring" for continuous updates
5. Tap "Refresh" for manual status updates

## Server Configuration
Make sure your Prometheus server is:
- Running and accessible on the network
- Web interface enabled on port 5000
- Firewall allows connections from mobile devices

## Troubleshooting
- **Connection Failed**: Check server URL and network connectivity
- **App Won't Install**: Enable "Unknown Sources" in device settings
- **Permissions Denied**: Grant all requested permissions in app settings
- **App Crashes**: Check server compatibility and network stability

## Features
- Real-time system monitoring
- Alert notifications
- System status overview
- Resource usage tracking
- Module status monitoring
- Hephaestus statistics

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
        
        # Save instructions file
        instructions_file = self.output_dir / f"installation_instructions_{self.config['version_name']}.md"
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        return str(instructions_file)


def main():
    """Test Android APK building"""
    print("📱 Testing Android APK Builder")
    
    # Create APK builder
    builder = AndroidAPKBuilder()
    
    # Check build environment
    print("🔍 Checking build environment...")
    env_status = builder.check_build_environment()
    
    if env_status['ready']:
        print("✅ Build environment ready")
        
        # Create Android project
        print("📁 Creating Android project...")
        if builder.create_android_project():
            print("✅ Android project created")
            
            # Note: Actual APK building requires Android SDK and takes time
            # For demonstration, we'll just show what would happen
            print("📱 APK build would start here...")
            print("💡 To actually build APK, run:")
            print("   cd android_build && buildozer android debug")
            
        else:
            print("❌ Failed to create Android project")
    else:
        print("❌ Build environment not ready:")
        for issue in env_status['issues']:
            print(f"   - {issue}")
        
        if env_status['requirements']:
            print("\n💡 Requirements to install:")
            for req in env_status['requirements']:
                print(f"   - {req}")


if __name__ == "__main__":
    main()