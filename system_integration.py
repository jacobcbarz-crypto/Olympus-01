#!/usr/bin/env python3
"""
Prometheus System Integration
Complete system integration and orchestration
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import all Prometheus components
from prometheus_core import PrometheusCore
from hephaestus import HephaestusCore
from security_advanced import AdvancedSecurityManager
from failsafe_recovery import AutoRecoverySystem
from autonomous_update import AutoUpdateManager
from android_deployment import AndroidAPKBuilder


class PrometheusIntegratedSystem:
    """Complete integrated Prometheus system"""
    
    def __init__(self, config_file: str = "/workspace/prometheus_config.json"):
        self.config_file = config_file
        self.config = self._load_configuration()
        
        # Core components
        self.prometheus_core = None
        self.hephaestus = None
        self.security_manager = None
        self.recovery_system = None
        self.update_manager = None
        self.android_builder = None
        
        # System state
        self.initialized = False
        self.running = False
        self.startup_time = None
        
        # Integration threads
        self.integration_threads = {}
        
    def _load_configuration(self) -> Dict[str, Any]:
        """Load system configuration"""
        try:
            import json
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_file}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "prometheus": {
                "name": "Prometheus Monitoring System",
                "version": "1.0.0",
                "autonomous_mode": True,
                "encryption_password": "prometheus_secure_2024_change_me"
            },
            "security": {
                "advanced_monitoring": True,
                "auto_response": True,
                "scan_interval": 300
            },
            "recovery": {
                "auto_recovery": True,
                "checkpoint_interval": 3600
            },
            "updates": {
                "autonomous_updates": True,
                "check_interval": 3600
            },
            "android": {
                "apk_generation_enabled": True
            }
        }
    
    def initialize_system(self) -> bool:
        """Initialize all system components"""
        try:
            print("🔥 Initializing Prometheus Integrated System")
            print("=" * 60)
            
            # Initialize core Prometheus
            print("🚀 Initializing Prometheus Core...")
            self.prometheus_core = PrometheusCore(
                encryption_password=self.config.get('prometheus', {}).get('encryption_password', 'default_password')
            )
            print("✅ Prometheus Core initialized")
            
            # Initialize Hephaestus
            print("🔨 Initializing Hephaestus...")
            self.hephaestus = HephaestusCore(prometheus_integration=True)
            self.prometheus_core.register_module("Hephaestus", "PROJECT_CONVERTER", "1.0.0")
            print("✅ Hephaestus initialized")
            
            # Initialize Advanced Security
            if self.config.get('security', {}).get('advanced_monitoring', True):
                print("🛡️ Initializing Advanced Security...")
                self.security_manager = AdvancedSecurityManager(self.prometheus_core)
                self.prometheus_core.register_module("AdvancedSecurity", "SECURITY_MONITOR", "1.0.0")
                print("✅ Advanced Security initialized")
            
            # Initialize Recovery System
            if self.config.get('recovery', {}).get('auto_recovery', True):
                print("🔧 Initializing Recovery System...")
                self.recovery_system = AutoRecoverySystem(self.prometheus_core)
                self.prometheus_core.register_module("AutoRecovery", "FAILSAFE_RECOVERY", "1.0.0")
                print("✅ Recovery System initialized")
            
            # Initialize Update Manager
            if self.config.get('updates', {}).get('autonomous_updates', True):
                print("🔄 Initializing Update Manager...")
                self.update_manager = AutoUpdateManager(self.prometheus_core)
                self.prometheus_core.register_module("AutoUpdate", "AUTONOMOUS_UPDATE", "1.0.0")
                print("✅ Update Manager initialized")
            
            # Initialize Android Builder
            if self.config.get('android', {}).get('apk_generation_enabled', False):
                print("📱 Initializing Android Builder...")
                self.android_builder = AndroidAPKBuilder(self.prometheus_core)
                self.prometheus_core.register_module("AndroidBuilder", "APK_GENERATOR", "1.0.0")
                print("✅ Android Builder initialized")
            
            self.initialized = True
            print("\n🎉 All components initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False
    
    def start_system(self) -> bool:
        """Start all system components"""
        if not self.initialized:
            print("❌ System not initialized. Call initialize_system() first.")
            return False
        
        try:
            print("\n🚀 Starting Prometheus Integrated System")
            print("=" * 60)
            
            self.startup_time = datetime.now()
            
            # Start core Prometheus
            print("🔥 Starting Prometheus Core...")
            self.prometheus_core.start_system()
            print("✅ Prometheus Core started")
            
            # Start security monitoring
            if self.security_manager:
                print("🛡️ Starting Security Monitoring...")
                self.security_manager.start_security_monitoring()
                print("✅ Security Monitoring started")
            
            # Start recovery system
            if self.recovery_system:
                print("🔧 Starting Recovery System...")
                self.recovery_system.start_auto_recovery()
                print("✅ Recovery System started")
            
            # Start update manager
            if self.update_manager:
                print("🔄 Starting Update Manager...")
                self.update_manager.start_autonomous_updates()
                print("✅ Update Manager started")
            
            # Start integration monitoring
            self._start_integration_monitoring()
            
            self.running = True
            
            print(f"\n🎉 Prometheus System fully operational!")
            print(f"📊 System Status: {self.get_integrated_status()['overall_status']}")
            print(f"🌐 Web Interface: http://localhost:5000")
            print(f"💻 CLI Interface: python prometheus_cli.py status")
            
            return True
            
        except Exception as e:
            print(f"❌ System startup failed: {e}")
            return False
    
    def stop_system(self):
        """Stop all system components gracefully"""
        print("\n🛑 Stopping Prometheus Integrated System...")
        
        self.running = False
        
        # Stop integration monitoring
        self._stop_integration_monitoring()
        
        # Stop update manager
        if self.update_manager:
            self.update_manager.stop_autonomous_updates()
            print("✅ Update Manager stopped")
        
        # Stop recovery system
        if self.recovery_system:
            self.recovery_system.stop_auto_recovery()
            print("✅ Recovery System stopped")
        
        # Stop security monitoring
        if self.security_manager:
            self.security_manager.stop_security_monitoring()
            print("✅ Security Monitoring stopped")
        
        # Stop core Prometheus
        if self.prometheus_core:
            self.prometheus_core.stop_system()
            print("✅ Prometheus Core stopped")
        
        print("👋 Prometheus System shutdown complete")
    
    def _start_integration_monitoring(self):
        """Start integration monitoring threads"""
        # System health integration
        health_thread = threading.Thread(
            target=self._integration_health_monitor,
            daemon=True,
            name="IntegrationHealthMonitor"
        )
        health_thread.start()
        self.integration_threads['health'] = health_thread
        
        # Performance integration
        perf_thread = threading.Thread(
            target=self._integration_performance_monitor,
            daemon=True,
            name="IntegrationPerfMonitor"
        )
        perf_thread.start()
        self.integration_threads['performance'] = perf_thread
        
        print("✅ Integration monitoring started")
    
    def _stop_integration_monitoring(self):
        """Stop integration monitoring threads"""
        # Threads are daemon threads, so they'll stop when main program stops
        self.integration_threads.clear()
        print("✅ Integration monitoring stopped")
    
    def _integration_health_monitor(self):
        """Monitor integration health between components"""
        while self.running:
            try:
                # Check component health
                health_status = self._check_component_health()
                
                # Log any integration issues
                if health_status['issues']:
                    for issue in health_status['issues']:
                        self.prometheus_core.logger.system_logger.warning(f"Integration issue: {issue}")
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                if self.prometheus_core:
                    self.prometheus_core.logger.system_logger.error(f"Integration health monitor error: {e}")
                time.sleep(120)  # Wait longer on error
    
    def _integration_performance_monitor(self):
        """Monitor integration performance"""
        while self.running:
            try:
                # Collect performance metrics from all components
                perf_metrics = self._collect_integration_metrics()
                
                # Log performance summary
                if perf_metrics:
                    self.prometheus_core.logger.performance_logger.info(
                        f"Integration performance: {len(perf_metrics)} metrics collected"
                    )
                
                # Sleep for monitoring interval
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                if self.prometheus_core:
                    self.prometheus_core.logger.performance_logger.error(f"Integration perf monitor error: {e}")
                time.sleep(600)  # Wait longer on error
    
    def _check_component_health(self) -> Dict[str, Any]:
        """Check health of all integrated components"""
        health_status = {
            'overall_healthy': True,
            'components': {},
            'issues': []
        }
        
        # Check Prometheus Core
        if self.prometheus_core:
            core_status = self.prometheus_core.get_system_status()
            health_status['components']['prometheus_core'] = {
                'status': core_status.get('prometheus_status', 'UNKNOWN'),
                'healthy': core_status.get('prometheus_status') == 'RUNNING'
            }
            if not health_status['components']['prometheus_core']['healthy']:
                health_status['issues'].append("Prometheus Core not running")
                health_status['overall_healthy'] = False
        
        # Check Hephaestus
        if self.hephaestus:
            hep_stats = self.hephaestus.get_generation_stats()
            health_status['components']['hephaestus'] = {
                'status': 'RUNNING' if hep_stats.get('total_generated', 0) >= 0 else 'ERROR',
                'healthy': True
            }
        
        # Check Security Manager
        if self.security_manager:
            health_status['components']['security_manager'] = {
                'status': 'RUNNING' if self.security_manager.running else 'STOPPED',
                'healthy': self.security_manager.running
            }
            if not self.security_manager.running:
                health_status['issues'].append("Security Manager not running")
        
        # Check Recovery System
        if self.recovery_system:
            health_status['components']['recovery_system'] = {
                'status': 'RUNNING' if self.recovery_system.running else 'STOPPED',
                'healthy': self.recovery_system.running
            }
            if not self.recovery_system.running:
                health_status['issues'].append("Recovery System not running")
        
        # Check Update Manager
        if self.update_manager:
            health_status['components']['update_manager'] = {
                'status': 'RUNNING' if self.update_manager.running else 'STOPPED',
                'healthy': self.update_manager.running
            }
            if not self.update_manager.running:
                health_status['issues'].append("Update Manager not running")
        
        return health_status
    
    def _collect_integration_metrics(self) -> List[Dict[str, Any]]:
        """Collect performance metrics from all components"""
        metrics = []
        
        try:
            # Core system metrics
            if self.prometheus_core:
                core_status = self.prometheus_core.get_system_status()
                metrics.append({
                    'component': 'prometheus_core',
                    'metric': 'uptime',
                    'value': core_status.get('uptime', '0'),
                    'timestamp': datetime.now()
                })
                
                resources = core_status.get('system_resources', {})
                for resource, value in resources.items():
                    metrics.append({
                        'component': 'system',
                        'metric': resource,
                        'value': value,
                        'timestamp': datetime.now()
                    })
            
            # Hephaestus metrics
            if self.hephaestus:
                hep_stats = self.hephaestus.get_generation_stats()
                metrics.append({
                    'component': 'hephaestus',
                    'metric': 'total_generated',
                    'value': hep_stats.get('total_generated', 0),
                    'timestamp': datetime.now()
                })
                metrics.append({
                    'component': 'hephaestus',
                    'metric': 'success_rate',
                    'value': float(hep_stats.get('success_rate', '0%').rstrip('%')),
                    'timestamp': datetime.now()
                })
            
            # Security metrics
            if self.security_manager:
                try:
                    security_report = self.security_manager.generate_security_report()
                    metrics.append({
                        'component': 'security',
                        'metric': 'threats_24h',
                        'value': security_report.get('threats_24h', 0),
                        'timestamp': datetime.now()
                    })
                except Exception:
                    pass  # Security report might not be available
            
        except Exception as e:
            if self.prometheus_core:
                self.prometheus_core.logger.performance_logger.error(f"Error collecting integration metrics: {e}")
        
        return metrics
    
    def get_integrated_status(self) -> Dict[str, Any]:
        """Get comprehensive integrated system status"""
        status = {
            'timestamp': datetime.now(),
            'overall_status': 'UNKNOWN',
            'uptime': str(datetime.now() - self.startup_time) if self.startup_time else '0',
            'initialized': self.initialized,
            'running': self.running,
            'components': {}
        }
        
        try:
            # Get component health
            health_status = self._check_component_health()
            status['components'] = health_status['components']
            
            # Determine overall status
            if not self.running:
                status['overall_status'] = 'STOPPED'
            elif not health_status['overall_healthy']:
                status['overall_status'] = 'DEGRADED'
            elif health_status['issues']:
                status['overall_status'] = 'WARNING'
            else:
                status['overall_status'] = 'HEALTHY'
            
            # Add component-specific status
            if self.prometheus_core:
                core_status = self.prometheus_core.get_system_status()
                status['prometheus_core'] = core_status
            
            if self.hephaestus:
                status['hephaestus'] = self.hephaestus.get_generation_stats()
            
            if self.security_manager:
                try:
                    security_report = self.security_manager.generate_security_report()
                    status['security'] = {
                        'monitoring_active': security_report.get('monitoring_status') == 'ACTIVE',
                        'threats_24h': security_report.get('threats_24h', 0),
                        'blocked_ips': security_report.get('blocked_ips', 0)
                    }
                except Exception:
                    status['security'] = {'monitoring_active': self.security_manager.running}
            
            if self.update_manager:
                status['updates'] = self.update_manager.get_update_status()
            
        except Exception as e:
            status['error'] = str(e)
            if self.prometheus_core:
                self.prometheus_core.logger.system_logger.error(f"Error getting integrated status: {e}")
        
        return status
    
    def run_system_test(self) -> Dict[str, Any]:
        """Run comprehensive system test"""
        test_results = {
            'timestamp': datetime.now(),
            'overall_result': 'UNKNOWN',
            'tests': {},
            'summary': {
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
        print("🧪 Running Prometheus System Tests")
        print("=" * 50)
        
        # Test 1: Component Initialization
        print("🔍 Testing component initialization...")
        try:
            if self.initialized:
                test_results['tests']['initialization'] = {'result': 'PASS', 'message': 'All components initialized'}
                test_results['summary']['passed'] += 1
            else:
                test_results['tests']['initialization'] = {'result': 'FAIL', 'message': 'System not initialized'}
                test_results['summary']['failed'] += 1
        except Exception as e:
            test_results['tests']['initialization'] = {'result': 'FAIL', 'message': str(e)}
            test_results['summary']['failed'] += 1
        
        # Test 2: Core Functionality
        print("🔍 Testing core functionality...")
        try:
            if self.prometheus_core and self.prometheus_core.running:
                core_status = self.prometheus_core.get_system_status()
                if core_status.get('prometheus_status') == 'RUNNING':
                    test_results['tests']['core_functionality'] = {'result': 'PASS', 'message': 'Core system operational'}
                    test_results['summary']['passed'] += 1
                else:
                    test_results['tests']['core_functionality'] = {'result': 'FAIL', 'message': 'Core system not running'}
                    test_results['summary']['failed'] += 1
            else:
                test_results['tests']['core_functionality'] = {'result': 'FAIL', 'message': 'Core system not available'}
                test_results['summary']['failed'] += 1
        except Exception as e:
            test_results['tests']['core_functionality'] = {'result': 'FAIL', 'message': str(e)}
            test_results['summary']['failed'] += 1
        
        # Test 3: Hephaestus Functionality
        print("🔍 Testing Hephaestus functionality...")
        try:
            if self.hephaestus:
                # Test prompt generation
                test_prompt = self.hephaestus.generate_cursor_prompt(
                    "Test Project",
                    "A simple test project for validation"
                )
                if test_prompt and test_prompt.prompt_id:
                    test_results['tests']['hephaestus'] = {'result': 'PASS', 'message': 'Hephaestus generating prompts'}
                    test_results['summary']['passed'] += 1
                else:
                    test_results['tests']['hephaestus'] = {'result': 'FAIL', 'message': 'Hephaestus not generating prompts'}
                    test_results['summary']['failed'] += 1
            else:
                test_results['tests']['hephaestus'] = {'result': 'FAIL', 'message': 'Hephaestus not available'}
                test_results['summary']['failed'] += 1
        except Exception as e:
            test_results['tests']['hephaestus'] = {'result': 'FAIL', 'message': str(e)}
            test_results['summary']['failed'] += 1
        
        # Test 4: Security System
        print("🔍 Testing security system...")
        try:
            if self.security_manager and self.security_manager.running:
                test_results['tests']['security'] = {'result': 'PASS', 'message': 'Security monitoring active'}
                test_results['summary']['passed'] += 1
            else:
                test_results['tests']['security'] = {'result': 'WARNING', 'message': 'Security monitoring not active'}
                test_results['summary']['warnings'] += 1
        except Exception as e:
            test_results['tests']['security'] = {'result': 'FAIL', 'message': str(e)}
            test_results['summary']['failed'] += 1
        
        # Test 5: Recovery System
        print("🔍 Testing recovery system...")
        try:
            if self.recovery_system and self.recovery_system.running:
                test_results['tests']['recovery'] = {'result': 'PASS', 'message': 'Recovery system active'}
                test_results['summary']['passed'] += 1
            else:
                test_results['tests']['recovery'] = {'result': 'WARNING', 'message': 'Recovery system not active'}
                test_results['summary']['warnings'] += 1
        except Exception as e:
            test_results['tests']['recovery'] = {'result': 'FAIL', 'message': str(e)}
            test_results['summary']['failed'] += 1
        
        # Test 6: Database Connectivity
        print("🔍 Testing database connectivity...")
        try:
            if self.prometheus_core and hasattr(self.prometheus_core, 'database'):
                # Test database connection
                alerts = self.prometheus_core.database.get_active_alerts()
                test_results['tests']['database'] = {'result': 'PASS', 'message': 'Database accessible'}
                test_results['summary']['passed'] += 1
            else:
                test_results['tests']['database'] = {'result': 'FAIL', 'message': 'Database not accessible'}
                test_results['summary']['failed'] += 1
        except Exception as e:
            test_results['tests']['database'] = {'result': 'FAIL', 'message': str(e)}
            test_results['summary']['failed'] += 1
        
        # Determine overall result
        if test_results['summary']['failed'] > 0:
            test_results['overall_result'] = 'FAIL'
        elif test_results['summary']['warnings'] > 0:
            test_results['overall_result'] = 'WARNING'
        else:
            test_results['overall_result'] = 'PASS'
        
        print(f"\n📊 Test Results: {test_results['overall_result']}")
        print(f"✅ Passed: {test_results['summary']['passed']}")
        print(f"⚠️  Warnings: {test_results['summary']['warnings']}")
        print(f"❌ Failed: {test_results['summary']['failed']}")
        
        return test_results
    
    def generate_system_report(self) -> str:
        """Generate comprehensive system report"""
        report_lines = [
            "🔥 PROMETHEUS INTEGRATED SYSTEM REPORT",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # System overview
        status = self.get_integrated_status()
        report_lines.extend([
            "📊 SYSTEM OVERVIEW",
            "-" * 30,
            f"Overall Status: {status['overall_status']}",
            f"Uptime: {status['uptime']}",
            f"Initialized: {status['initialized']}",
            f"Running: {status['running']}",
            ""
        ])
        
        # Component status
        report_lines.extend([
            "🧩 COMPONENT STATUS",
            "-" * 30
        ])
        
        for component, info in status.get('components', {}).items():
            report_lines.append(f"{component}: {info.get('status', 'UNKNOWN')}")
        
        report_lines.append("")
        
        # Performance metrics
        if 'prometheus_core' in status:
            core_status = status['prometheus_core']
            resources = core_status.get('system_resources', {})
            
            report_lines.extend([
                "📈 PERFORMANCE METRICS",
                "-" * 30,
                f"CPU Usage: {resources.get('cpu', 0):.1f}%",
                f"Memory Usage: {resources.get('memory', 0):.1f}%",
                f"Disk Usage: {resources.get('disk', 0):.1f}%",
                f"Active Modules: {core_status.get('modules', 0)}",
                f"Active Alerts: {core_status.get('active_alerts', 0)}",
                ""
            ])
        
        # Hephaestus statistics
        if 'hephaestus' in status:
            hep_stats = status['hephaestus']
            report_lines.extend([
                "🔨 HEPHAESTUS STATISTICS",
                "-" * 30,
                f"Total Generated: {hep_stats.get('total_generated', 0)}",
                f"Success Rate: {hep_stats.get('success_rate', '0%')}",
                f"Average per Hour: {hep_stats.get('avg_per_hour', 0):.1f}",
                ""
            ])
        
        # Security status
        if 'security' in status:
            security = status['security']
            report_lines.extend([
                "🛡️ SECURITY STATUS",
                "-" * 30,
                f"Monitoring Active: {security.get('monitoring_active', False)}",
                f"Threats (24h): {security.get('threats_24h', 0)}",
                f"Blocked IPs: {security.get('blocked_ips', 0)}",
                ""
            ])
        
        # Update status
        if 'updates' in status:
            updates = status['updates']
            report_lines.extend([
                "🔄 UPDATE STATUS",
                "-" * 30,
                f"Autonomous Updates: {updates.get('autonomous_updates_enabled', False)}",
                f"Pending Updates: {updates.get('pending_updates', 0)}",
                f"Completed Updates: {updates.get('completed_updates', 0)}",
                ""
            ])
        
        # System health
        health_status = self._check_component_health()
        if health_status['issues']:
            report_lines.extend([
                "⚠️ SYSTEM ISSUES",
                "-" * 30
            ])
            for issue in health_status['issues']:
                report_lines.append(f"- {issue}")
            report_lines.append("")
        
        # Configuration summary
        report_lines.extend([
            "⚙️ CONFIGURATION",
            "-" * 30,
            f"Config File: {self.config_file}",
            f"Autonomous Mode: {self.config.get('prometheus', {}).get('autonomous_mode', False)}",
            f"Advanced Security: {self.config.get('security', {}).get('advanced_monitoring', False)}",
            f"Auto Recovery: {self.config.get('recovery', {}).get('auto_recovery', False)}",
            f"Auto Updates: {self.config.get('updates', {}).get('autonomous_updates', False)}",
            f"Android APK: {self.config.get('android', {}).get('apk_generation_enabled', False)}",
            ""
        ])
        
        # Footer
        report_lines.extend([
            "-" * 60,
            "🔥 Prometheus - Autonomous AI Monitoring and Architect System",
            "Building the future of self-sustaining AI ecosystems"
        ])
        
        return "\n".join(report_lines)


def main():
    """Main integration test and demonstration"""
    print("🔥 Prometheus Integrated System Test")
    print("=" * 60)
    
    # Create integrated system
    integrated_system = PrometheusIntegratedSystem()
    
    try:
        # Initialize system
        if not integrated_system.initialize_system():
            print("❌ System initialization failed")
            return
        
        # Start system
        if not integrated_system.start_system():
            print("❌ System startup failed")
            return
        
        # Run system tests
        print("\n" + "=" * 60)
        test_results = integrated_system.run_system_test()
        
        # Generate system report
        print("\n" + "=" * 60)
        print("📋 Generating system report...")
        report = integrated_system.generate_system_report()
        
        # Save report to file
        report_file = Path("/workspace/prometheus_system_report.txt")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📄 System report saved to: {report_file}")
        
        # Show summary
        print("\n" + "=" * 60)
        print("🎉 PROMETHEUS SYSTEM READY!")
        print("=" * 60)
        
        status = integrated_system.get_integrated_status()
        print(f"Overall Status: {status['overall_status']}")
        print(f"Components: {len(status.get('components', {}))}")
        print(f"Web Interface: http://localhost:5000")
        print(f"CLI Interface: python prometheus_cli.py status")
        
        if test_results['overall_result'] == 'PASS':
            print("✅ All systems operational and ready for autonomous operation")
        else:
            print(f"⚠️ System operational with {test_results['summary']['warnings']} warnings and {test_results['summary']['failed']} issues")
        
        # Keep system running for demonstration
        print("\n💡 System running... Press Ctrl+C to shutdown")
        try:
            while True:
                time.sleep(60)
                current_status = integrated_system.get_integrated_status()
                print(f"💓 Heartbeat - Status: {current_status['overall_status']}, Uptime: {current_status['uptime']}")
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
    
    finally:
        # Shutdown system
        integrated_system.stop_system()


if __name__ == "__main__":
    main()