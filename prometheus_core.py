#!/usr/bin/env python3
"""
Prometheus - Monitoring and Architect AI System
Core module for autonomous system management and oversight
"""

import asyncio
import logging
import json
import os
import time
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import subprocess
import psutil
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


@dataclass
class SecurityAlert:
    """Security alert data structure"""
    timestamp: datetime
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    alert_type: str
    description: str
    affected_system: str
    remediation_suggested: str
    status: str = "ACTIVE"


@dataclass
class SystemStatus:
    """System status monitoring data"""
    system_name: str
    status: str  # ONLINE, OFFLINE, ERROR, DEGRADED
    last_heartbeat: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_status: str
    error_count: int = 0


class PrometheusEncryption:
    """End-to-end encryption handler"""
    
    def __init__(self, password: str):
        self.password = password.encode()
        self._key = None
        self._generate_key()
    
    def _generate_key(self):
        """Generate encryption key from password"""
        salt = b'prometheus_salt_2024'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        self._key = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self._key.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self._key.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_file(self, file_path: str) -> str:
        """Encrypt file and return encrypted content"""
        with open(file_path, 'rb') as f:
            encrypted_data = self._key.encrypt(f.read())
        return encrypted_data.decode()
    
    def decrypt_file(self, encrypted_content: str, output_path: str):
        """Decrypt content and save to file"""
        decrypted_data = self._key.decrypt(encrypted_content.encode())
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)


class PrometheusLogger:
    """Comprehensive logging system"""
    
    def __init__(self, log_dir: str = "/workspace/prometheus_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self._setup_loggers()
        
    def _setup_loggers(self):
        """Setup different loggers for different purposes"""
        # Main system logger
        self.system_logger = self._create_logger('system', 'prometheus_system.log')
        # Security logger
        self.security_logger = self._create_logger('security', 'prometheus_security.log')
        # Performance logger
        self.performance_logger = self._create_logger('performance', 'prometheus_performance.log')
        # Alert logger
        self.alert_logger = self._create_logger('alerts', 'prometheus_alerts.log')
    
    def _create_logger(self, name: str, filename: str) -> logging.Logger:
        """Create a configured logger"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(self.log_dir / filename)
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger


class PrometheusDatabase:
    """Database management for Prometheus"""
    
    def __init__(self, db_path: str = "/workspace/prometheus_data/prometheus.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # System status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_name TEXT NOT NULL,
                status TEXT NOT NULL,
                last_heartbeat TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                network_status TEXT,
                error_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Security alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                severity TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                description TEXT NOT NULL,
                affected_system TEXT NOT NULL,
                remediation_suggested TEXT,
                status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Module registry table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_name TEXT UNIQUE NOT NULL,
                module_type TEXT NOT NULL,
                version TEXT,
                status TEXT DEFAULT 'INACTIVE',
                last_updated TIMESTAMP,
                configuration TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_name TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_security_alert(self, alert: SecurityAlert):
        """Insert security alert into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO security_alerts 
            (timestamp, severity, alert_type, description, affected_system, remediation_suggested, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (alert.timestamp, alert.severity, alert.alert_type, alert.description,
              alert.affected_system, alert.remediation_suggested, alert.status))
        conn.commit()
        conn.close()
    
    def update_system_status(self, status: SystemStatus):
        """Update system status in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO system_status 
            (system_name, status, last_heartbeat, cpu_usage, memory_usage, disk_usage, network_status, error_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (status.system_name, status.status, status.last_heartbeat, status.cpu_usage,
              status.memory_usage, status.disk_usage, status.network_status, status.error_count))
        conn.commit()
        conn.close()
    
    def get_active_alerts(self) -> List[SecurityAlert]:
        """Get all active security alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM security_alerts WHERE status = "ACTIVE"')
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            alert = SecurityAlert(
                timestamp=datetime.fromisoformat(row[1]),
                severity=row[2],
                alert_type=row[3],
                description=row[4],
                affected_system=row[5],
                remediation_suggested=row[6],
                status=row[7]
            )
            alerts.append(alert)
        return alerts


class SecurityMonitor:
    """Security monitoring and threat detection"""
    
    def __init__(self, prometheus_instance):
        self.prometheus = prometheus_instance
        self.threat_patterns = [
            r'unauthorized.*access',
            r'failed.*login',
            r'suspicious.*activity',
            r'malware.*detected',
            r'intrusion.*attempt',
            r'data.*breach',
            r'vulnerability.*exploit'
        ]
    
    def scan_system_vulnerabilities(self) -> List[SecurityAlert]:
        """Scan system for vulnerabilities"""
        alerts = []
        
        # Check for open ports
        try:
            result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
            open_ports = len(result.stdout.split('\n')) - 1
            
            if open_ports > 50:  # Threshold for suspicious port activity
                alert = SecurityAlert(
                    timestamp=datetime.now(),
                    severity="MEDIUM",
                    alert_type="NETWORK_SECURITY",
                    description=f"High number of open ports detected: {open_ports}",
                    affected_system="NETWORK",
                    remediation_suggested="Review and close unnecessary ports"
                )
                alerts.append(alert)
        except Exception as e:
            self.prometheus.logger.security_logger.error(f"Port scan failed: {e}")
        
        # Check disk usage for potential data exfiltration
        disk_usage = psutil.disk_usage('/')
        if disk_usage.percent > 95:
            alert = SecurityAlert(
                timestamp=datetime.now(),
                severity="HIGH",
                alert_type="RESOURCE_EXHAUSTION",
                description=f"Critical disk usage: {disk_usage.percent}%",
                affected_system="STORAGE",
                remediation_suggested="Investigate unusual disk usage patterns"
            )
            alerts.append(alert)
        
        return alerts
    
    def monitor_file_integrity(self, monitored_paths: List[str]) -> List[SecurityAlert]:
        """Monitor file integrity for unauthorized changes"""
        alerts = []
        
        for path in monitored_paths:
            if os.path.exists(path):
                # Calculate file hash
                with open(path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                # Store/check against known good hashes
                hash_file = f"{path}.prometheus_hash"
                if os.path.exists(hash_file):
                    with open(hash_file, 'r') as f:
                        stored_hash = f.read().strip()
                    
                    if file_hash != stored_hash:
                        alert = SecurityAlert(
                            timestamp=datetime.now(),
                            severity="HIGH",
                            alert_type="FILE_INTEGRITY",
                            description=f"Unauthorized modification detected: {path}",
                            affected_system="FILE_SYSTEM",
                            remediation_suggested="Investigate file changes and restore from backup if necessary"
                        )
                        alerts.append(alert)
                else:
                    # Store initial hash
                    with open(hash_file, 'w') as f:
                        f.write(file_hash)
        
        return alerts


class WatchdogManager:
    """Watchdog system for continuous monitoring"""
    
    def __init__(self, prometheus_instance):
        self.prometheus = prometheus_instance
        self.watchdog_threads = {}
        self.running = False
    
    def start_watchdog(self, name: str, target_function: Callable, interval: int = 60):
        """Start a watchdog thread for a specific function"""
        if name in self.watchdog_threads:
            return
        
        def watchdog_loop():
            while self.running:
                try:
                    target_function()
                    self.prometheus.logger.system_logger.info(f"Watchdog {name} executed successfully")
                except Exception as e:
                    self.prometheus.logger.system_logger.error(f"Watchdog {name} failed: {e}")
                    # Create alert for watchdog failure
                    alert = SecurityAlert(
                        timestamp=datetime.now(),
                        severity="HIGH",
                        alert_type="SYSTEM_FAILURE",
                        description=f"Watchdog {name} failed: {str(e)}",
                        affected_system="WATCHDOG",
                        remediation_suggested="Investigate and restart failed watchdog"
                    )
                    self.prometheus.database.insert_security_alert(alert)
                
                time.sleep(interval)
        
        thread = threading.Thread(target=watchdog_loop, daemon=True)
        self.watchdog_threads[name] = thread
        thread.start()
        self.prometheus.logger.system_logger.info(f"Started watchdog: {name}")
    
    def start_all_watchdogs(self):
        """Start all watchdog processes"""
        self.running = True
        
        # System health watchdog
        self.start_watchdog("system_health", self._monitor_system_health, 30)
        
        # Security scan watchdog
        self.start_watchdog("security_scan", self._run_security_scan, 300)  # 5 minutes
        
        # Module health watchdog
        self.start_watchdog("module_health", self._monitor_modules, 60)
        
        # Log rotation watchdog
        self.start_watchdog("log_rotation", self._rotate_logs, 3600)  # 1 hour
    
    def stop_all_watchdogs(self):
        """Stop all watchdog processes"""
        self.running = False
        self.prometheus.logger.system_logger.info("Stopping all watchdogs")
    
    def _monitor_system_health(self):
        """Monitor overall system health"""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = SystemStatus(
            system_name="PROMETHEUS_CORE",
            status="ONLINE" if cpu_usage < 90 and memory.percent < 90 else "DEGRADED",
            last_heartbeat=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_status="ONLINE"
        )
        
        self.prometheus.database.update_system_status(status)
    
    def _run_security_scan(self):
        """Run security scanning"""
        alerts = self.prometheus.security_monitor.scan_system_vulnerabilities()
        for alert in alerts:
            self.prometheus.database.insert_security_alert(alert)
            self.prometheus.logger.security_logger.warning(f"Security Alert: {alert.description}")
    
    def _monitor_modules(self):
        """Monitor all registered modules"""
        # This will be expanded when Hephaestus creates modules
        pass
    
    def _rotate_logs(self):
        """Rotate log files to prevent disk space issues"""
        log_dir = Path("/workspace/prometheus_logs")
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_size > 100 * 1024 * 1024:  # 100MB
                backup_name = f"{log_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                log_file.rename(log_dir / backup_name)
                # Create new empty log file
                log_file.touch()


class PrometheusCore:
    """Main Prometheus system class"""
    
    def __init__(self, encryption_password: str = "prometheus_secure_2024"):
        self.encryption = PrometheusEncryption(encryption_password)
        self.logger = PrometheusLogger()
        self.database = PrometheusDatabase()
        self.security_monitor = SecurityMonitor(self)
        self.watchdog_manager = WatchdogManager(self)
        
        # System state
        self.running = False
        self.modules = {}
        self.startup_time = datetime.now()
        
        self.logger.system_logger.info("Prometheus Core initialized")
    
    def start_system(self):
        """Start the Prometheus monitoring system"""
        self.running = True
        self.logger.system_logger.info("Starting Prometheus monitoring system")
        
        # Start watchdog processes
        self.watchdog_manager.start_all_watchdogs()
        
        # Initialize system status
        initial_status = SystemStatus(
            system_name="PROMETHEUS_CORE",
            status="ONLINE",
            last_heartbeat=datetime.now(),
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            network_status="ONLINE"
        )
        self.database.update_system_status(initial_status)
        
        self.logger.system_logger.info("Prometheus system started successfully")
    
    def stop_system(self):
        """Stop the Prometheus monitoring system"""
        self.running = False
        self.watchdog_manager.stop_all_watchdogs()
        self.logger.system_logger.info("Prometheus system stopped")
    
    def register_module(self, name: str, module_type: str, version: str = "1.0.0", config: Dict = None):
        """Register a new module for monitoring"""
        self.modules[name] = {
            'type': module_type,
            'version': version,
            'status': 'ACTIVE',
            'config': config or {},
            'last_updated': datetime.now()
        }
        
        # Store in database
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO module_registry 
            (module_name, module_type, version, status, last_updated, configuration)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, module_type, version, 'ACTIVE', datetime.now(), json.dumps(config or {})))
        conn.commit()
        conn.close()
        
        self.logger.system_logger.info(f"Registered module: {name} ({module_type} v{version})")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'prometheus_status': 'RUNNING' if self.running else 'STOPPED',
            'uptime': str(datetime.now() - self.startup_time),
            'modules': len(self.modules),
            'active_alerts': len(self.database.get_active_alerts()),
            'system_resources': {
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent
            }
        }
    
    def create_hephaestus_specification(self) -> str:
        """Create specification for Hephaestus module"""
        spec = {
            "module_name": "Hephaestus",
            "module_type": "PROJECT_CONVERTER",
            "description": "Converts project descriptions into detailed Cursor prompts for autonomous app/module building",
            "core_functions": [
                "Parse project descriptions and requirements",
                "Generate comprehensive Cursor prompts with technical specifications",
                "Include security, performance, and scalability considerations",
                "Create deployment and testing instructions",
                "Integrate with Prometheus monitoring hooks"
            ],
            "technical_requirements": [
                "Natural language processing capabilities",
                "Template-based prompt generation",
                "Integration with Prometheus monitoring",
                "Validation and testing framework",
                "Version control and iteration support"
            ],
            "security_requirements": [
                "Input sanitization and validation",
                "Secure prompt generation",
                "Audit trail for all generated prompts",
                "Integration with Prometheus security monitoring"
            ],
            "monitoring_hooks": [
                "Register with Prometheus on startup",
                "Send heartbeat signals every 60 seconds",
                "Report generation metrics and success rates",
                "Alert on generation failures or security issues"
            ]
        }
        
        return json.dumps(spec, indent=2)


def main():
    """Main entry point for Prometheus"""
    print("🔥 Initializing Prometheus - Monitoring and Architect AI System")
    
    # Initialize Prometheus
    prometheus = PrometheusCore()
    
    try:
        # Start the system
        prometheus.start_system()
        
        # Create Hephaestus specification
        hephaestus_spec = prometheus.create_hephaestus_specification()
        with open("/workspace/hephaestus_specification.json", "w") as f:
            f.write(hephaestus_spec)
        
        print("✅ Prometheus system started successfully")
        print("📊 System Status:", prometheus.get_system_status())
        print("🔧 Hephaestus specification created")
        
        # Keep running
        try:
            while True:
                time.sleep(60)
                status = prometheus.get_system_status()
                print(f"💓 Heartbeat - Active Alerts: {status['active_alerts']}, Uptime: {status['uptime']}")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Prometheus...")
            prometheus.stop_system()
            
    except Exception as e:
        prometheus.logger.system_logger.error(f"Critical error in Prometheus: {e}")
        print(f"❌ Critical error: {e}")


if __name__ == "__main__":
    main()