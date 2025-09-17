# 🔥 Prometheus Deployment Guide

**Complete deployment guide for the Prometheus AI Monitoring and Architect System**

## 🎯 Quick Start

### 1. Automated Installation
```bash
# Make installation script executable
chmod +x install.sh

# Run automated installation
./install.sh

# Start Prometheus
python3 prometheus_launcher.py
```

### 2. Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set executable permissions
chmod +x *.py

# Start the system
python3 prometheus_launcher.py
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows with WSL
- **Python**: 3.7 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 5GB free space
- **Network**: Internet access for updates and monitoring

### Recommended Requirements
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **Python**: 3.9 or higher
- **RAM**: 8GB or more
- **Storage**: 20GB free space (for logs, backups, and APK builds)
- **CPU**: Multi-core processor for optimal performance

## 🚀 Deployment Options

### Option 1: Standalone Deployment
```bash
# Clone or download Prometheus
cd /workspace

# Install dependencies
pip install cryptography flask flask-socketio watchdog psutil requests

# Configure system
cp prometheus_config.json prometheus_config_local.json
# Edit prometheus_config_local.json as needed

# Launch system
python3 prometheus_launcher.py
```

### Option 2: Development Environment
```bash
# Create virtual environment
python3 -m venv prometheus_env
source prometheus_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
python3 prometheus_launcher.py
```

### Option 3: Production Deployment
```bash
# Install as system service
sudo ./install.sh

# Configure for production
sudo systemctl enable prometheus-monitor
sudo systemctl start prometheus-monitor

# Monitor service
sudo systemctl status prometheus-monitor
```

### Option 4: Docker Deployment (Future)
```bash
# Build Docker image (configuration provided)
docker build -t prometheus-monitor .

# Run container
docker run -d -p 5000:5000 --name prometheus prometheus-monitor
```

## ⚙️ Configuration

### Core Configuration (`prometheus_config.json`)
```json
{
  "prometheus": {
    "encryption_password": "YOUR_SECURE_PASSWORD_HERE",
    "autonomous_mode": true,
    "auto_start": true
  },
  "security": {
    "scan_interval": 300,
    "threat_detection_enabled": true,
    "alert_thresholds": {
      "cpu_usage": 90,
      "memory_usage": 90,
      "disk_usage": 95
    }
  },
  "monitoring": {
    "heartbeat_interval": 60,
    "log_retention_days": 30,
    "performance_tracking": true
  },
  "web_interface": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 5000
  }
}
```

### Environment Variables
```bash
export PROMETHEUS_CONFIG="/path/to/config.json"
export PROMETHEUS_DATA_DIR="/path/to/data"
export PROMETHEUS_LOG_LEVEL="INFO"
export PROMETHEUS_WEB_PORT="5000"
```

## 🌐 Network Configuration

### Firewall Rules
```bash
# Allow web interface access
sudo ufw allow 5000/tcp

# For Android APK communication
sudo ufw allow from 192.168.0.0/16 to any port 5000
```

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name prometheus.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 📱 Android APK Deployment

### Prerequisites
```bash
# Install Android development tools
pip install buildozer kivy

# Set Android environment (Linux)
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools"

# Install Java JDK
sudo apt-get install openjdk-11-jdk
```

### Build APK
```bash
# Check build environment
python3 android_deployment.py

# Build APK (requires Android SDK)
cd android_build
buildozer android debug

# Install on device
adb install bin/prometheus_monitor-*.apk
```

## 🔧 System Administration

### Starting Services
```bash
# Start full system
python3 prometheus_launcher.py

# Start individual components
python3 prometheus_core.py        # Core monitoring
python3 hephaestus.py            # Prompt generation
python3 prometheus_web.py        # Web interface only
```

### Command Line Management
```bash
# System status
python3 prometheus_cli.py status

# Generate prompts
python3 prometheus_cli.py generate "My Project" -d "Description here"

# View logs
python3 prometheus_cli.py logs --type security

# Run security scan
python3 prometheus_cli.py scan

# Monitor system live
python3 prometheus_cli.py monitor --interval 10
```

### Web Interface
- **URL**: http://localhost:5000
- **Dashboard**: Real-time system monitoring
- **Prompt Generation**: Interactive Hephaestus interface
- **System Control**: Start/stop services, run scans
- **Log Viewing**: Real-time log monitoring

## 📊 Monitoring and Maintenance

### System Health Checks
```bash
# Automated health monitoring
python3 -c "
from system_integration import PrometheusIntegratedSystem
system = PrometheusIntegratedSystem()
system.initialize_system()
results = system.run_system_test()
print(f'System Health: {results[\"overall_result\"]}')
"
```

### Log Management
```bash
# View system logs
tail -f prometheus_logs/prometheus_system.log

# View security logs
tail -f prometheus_logs/prometheus_security.log

# Rotate logs manually
python3 -c "
from prometheus_core import PrometheusCore
p = PrometheusCore()
p.watchdog_manager._rotate_logs()
"
```

### Backup and Recovery
```bash
# Create system backup
python3 -c "
from failsafe_recovery import BackupManager
backup = BackupManager()
checkpoint = backup.create_system_checkpoint()
print(f'Backup created: {checkpoint.checkpoint_id}')
"

# List available backups
ls -la prometheus_backups/

# Restore from backup
python3 -c "
from failsafe_recovery import BackupManager
backup = BackupManager()
backup.restore_from_checkpoint('checkpoint_id_here')
"
```

## 🔒 Security Considerations

### Production Security
1. **Change Default Passwords**: Update encryption password in config
2. **Enable HTTPS**: Use SSL/TLS for web interface
3. **Firewall Configuration**: Restrict access to necessary ports
4. **Regular Updates**: Enable autonomous updates or update manually
5. **Access Control**: Implement authentication for web interface
6. **Log Monitoring**: Monitor security logs for threats

### Network Security
```bash
# Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure HTTPS in prometheus_config.json
{
  "web_interface": {
    "ssl_enabled": true,
    "ssl_cert": "/path/to/cert.pem",
    "ssl_key": "/path/to/key.pem"
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**System Won't Start**
```bash
# Check Python version
python3 --version  # Should be 3.7+

# Check dependencies
pip list | grep -E "(flask|cryptography|watchdog|psutil|requests)"

# Check permissions
ls -la *.py  # Should be executable

# Check configuration
python3 -c "import json; print(json.load(open('prometheus_config.json')))"
```

**Web Interface Not Accessible**
```bash
# Check if port is in use
netstat -tlnp | grep :5000

# Check firewall
sudo ufw status

# Check logs
tail -f prometheus_logs/prometheus_system.log
```

**Database Issues**
```bash
# Check database file
ls -la prometheus_data/prometheus.db

# Test database connection
python3 -c "
import sqlite3
conn = sqlite3.connect('prometheus_data/prometheus.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
print('Tables:', cursor.fetchall())
conn.close()
"
```

**Memory/Performance Issues**
```bash
# Check system resources
python3 -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent}%')
"

# Reduce monitoring frequency in config
# Increase log rotation frequency
# Enable memory optimization in autonomous updates
```

### Error Recovery
```bash
# Reset to factory defaults
rm -rf prometheus_data/ prometheus_logs/
python3 prometheus_launcher.py

# Restore from backup
python3 failsafe_recovery.py

# Reinstall system
./install.sh --force-reinstall
```

## 📈 Performance Optimization

### System Optimization
1. **Resource Monitoring**: Adjust monitoring intervals based on usage
2. **Log Management**: Configure appropriate retention periods
3. **Database Optimization**: Enable automatic database maintenance
4. **Memory Management**: Enable autonomous memory optimization
5. **Network Optimization**: Use local caching where possible

### Configuration Tuning
```json
{
  "monitoring": {
    "system_metrics_interval": 30,  // Reduce for less CPU usage
    "heartbeat_interval": 60,       // Increase for less network traffic
    "log_retention_days": 7         // Reduce for less disk usage
  },
  "security": {
    "scan_interval": 600,           // Increase for less CPU usage
    "alert_thresholds": {
      "cpu_usage": 95,              // Adjust based on system capacity
      "memory_usage": 95,
      "disk_usage": 90
    }
  }
}
```

## 🔄 Updates and Maintenance

### Automatic Updates
- Autonomous updates are enabled by default
- Updates are applied based on priority and risk assessment
- System creates backups before applying updates
- Failed updates are automatically rolled back

### Manual Updates
```bash
# Check for updates
python3 autonomous_update.py

# Update Python packages
pip install --upgrade -r requirements.txt

# Update system configuration
# Edit prometheus_config.json as needed

# Restart system to apply changes
```

### Maintenance Schedule
- **Daily**: Automated health checks and log rotation
- **Weekly**: Security vulnerability scans
- **Monthly**: System backup and cleanup
- **Quarterly**: Performance analysis and optimization

## 📞 Support and Documentation

### Getting Help
1. **Check Logs**: Review system logs for error details
2. **Run Diagnostics**: Use built-in diagnostic tools
3. **System Status**: Check web dashboard and CLI status
4. **Configuration**: Verify configuration settings

### Additional Resources
- **Web Dashboard**: http://localhost:5000
- **System Logs**: `/workspace/prometheus_logs/`
- **Configuration**: `/workspace/prometheus_config.json`
- **Generated Prompts**: `/workspace/generated_prompts/`
- **Backups**: `/workspace/prometheus_backups/`

### System Information
```bash
# Generate system report
python3 system_integration.py

# View system report
cat prometheus_system_report.txt
```

---

## 🎉 Deployment Complete!

Your Prometheus AI Monitoring and Architect System is now ready for operation. The system will:

- ✅ Monitor all system components autonomously
- ✅ Generate Cursor prompts through Hephaestus
- ✅ Detect and respond to security threats
- ✅ Automatically recover from failures
- ✅ Update and refine itself continuously
- ✅ Provide web and CLI interfaces for oversight
- ✅ Generate Android APKs for mobile monitoring

**🔥 Welcome to the future of autonomous AI systems!**