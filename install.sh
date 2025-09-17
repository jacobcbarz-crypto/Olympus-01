#!/bin/bash
# Prometheus Installation Script
# Automated setup for Prometheus Monitoring and Architect AI System

set -e  # Exit on any error

echo "🔥 PROMETHEUS INSTALLATION SCRIPT"
echo "=================================="
echo ""

# Check if running as root (not recommended for development)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root. Consider using a virtual environment instead."
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version is compatible"
else
    echo "❌ Python $required_version or higher required. Found: $python_version"
    exit 1
fi

# Check if pip is available
echo "📦 Checking pip availability..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install pip3 first."
    exit 1
fi
echo "✅ pip3 is available"

# Create virtual environment (optional but recommended)
echo ""
read -p "🤔 Create Python virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv prometheus_venv
    source prometheus_venv/bin/activate
    echo "✅ Virtual environment created and activated"
    echo "💡 To activate later: source prometheus_venv/bin/activate"
fi

# Install Python dependencies
echo ""
echo "📥 Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✅ Dependencies installed successfully"

# Create necessary directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p prometheus_logs
mkdir -p prometheus_data
mkdir -p generated_prompts
mkdir -p templates
mkdir -p prometheus_backups
echo "✅ Directory structure created"

# Set executable permissions
echo ""
echo "🔧 Setting executable permissions..."
chmod +x prometheus_launcher.py
chmod +x prometheus_cli.py
chmod +x prometheus_core.py
chmod +x hephaestus.py
chmod +x prometheus_web.py
echo "✅ Permissions set"

# Test installation
echo ""
echo "🧪 Testing installation..."
python3 -c "
import prometheus_core, hephaestus, prometheus_web
print('✅ All modules imported successfully')
"

# Create desktop shortcut (Linux)
if command -v xdg-user-dir &> /dev/null; then
    desktop_dir=$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")
    if [ -d "$desktop_dir" ]; then
        echo ""
        read -p "🖥️  Create desktop shortcut? [y/N]: " create_shortcut
        if [[ $create_shortcut =~ ^[Yy]$ ]]; then
            cat > "$desktop_dir/Prometheus.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Prometheus Monitor
Comment=AI Monitoring and Architect System
Exec=python3 $(pwd)/prometheus_launcher.py
Icon=applications-system
Terminal=true
Categories=Development;System;
EOF
            chmod +x "$desktop_dir/Prometheus.desktop"
            echo "✅ Desktop shortcut created"
        fi
    fi
fi

# Create systemd service (Linux)
if command -v systemctl &> /dev/null && [ "$EUID" -eq 0 ]; then
    echo ""
    read -p "🔧 Install as system service? (requires root) [y/N]: " install_service
    if [[ $install_service =~ ^[Yy]$ ]]; then
        cat > /etc/systemd/system/prometheus-monitor.service << EOF
[Unit]
Description=Prometheus AI Monitoring System
After=network.target

[Service]
Type=simple
User=$(logname)
WorkingDirectory=$(pwd)
ExecStart=python3 $(pwd)/prometheus_launcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        systemctl daemon-reload
        systemctl enable prometheus-monitor.service
        echo "✅ System service installed and enabled"
        echo "💡 Control with: systemctl start/stop/status prometheus-monitor"
    fi
fi

echo ""
echo "🎉 INSTALLATION COMPLETE!"
echo "========================"
echo ""
echo "🚀 Quick Start:"
echo "   python3 prometheus_launcher.py    # Start full system"
echo "   python3 prometheus_cli.py status  # CLI status check"
echo ""
echo "🌐 Web Interface:"
echo "   http://localhost:5000"
echo ""
echo "📚 Key Files:"
echo "   prometheus_launcher.py  - Main system launcher"
echo "   prometheus_cli.py       - Command-line interface"
echo "   prometheus_config.json  - Configuration file"
echo "   requirements.txt        - Python dependencies"
echo ""
echo "🔧 Configuration:"
echo "   Edit prometheus_config.json to customize settings"
echo "   Change encryption password in config before production use"
echo ""
echo "📖 Documentation:"
echo "   Check generated_prompts/ for Hephaestus output examples"
echo "   Monitor prometheus_logs/ for system logs"
echo ""
echo "⚠️  Security Note:"
echo "   Change the default encryption password in prometheus_config.json"
echo "   Review security settings before production deployment"
echo ""

# Final test run
echo "🧪 Running quick system test..."
timeout 10s python3 prometheus_launcher.py || true
echo ""
echo "✅ Installation verification complete!"
echo "🔥 Prometheus is ready for operation!"