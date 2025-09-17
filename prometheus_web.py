#!/usr/bin/env python3
"""
Prometheus Web Interface
Simple web dashboard for system oversight and manual commands
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
from prometheus_core import PrometheusCore
from hephaestus import HephaestusCore


app = Flask(__name__)
app.secret_key = 'prometheus_web_secret_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
prometheus_instance = None
hephaestus_instance = None
web_thread = None


class PrometheusWebInterface:
    """Web interface controller for Prometheus"""
    
    def __init__(self):
        self.prometheus = None
        self.hephaestus = None
        self.is_running = False
        
    def initialize_systems(self):
        """Initialize Prometheus and Hephaestus systems"""
        global prometheus_instance, hephaestus_instance
        
        try:
            if not prometheus_instance:
                prometheus_instance = PrometheusCore()
                prometheus_instance.start_system()
            
            if not hephaestus_instance:
                hephaestus_instance = HephaestusCore()
                # Register Hephaestus with Prometheus
                prometheus_instance.register_module("Hephaestus", "PROJECT_CONVERTER", "1.0.0")
            
            self.prometheus = prometheus_instance
            self.hephaestus = hephaestus_instance
            self.is_running = True
            
            return True
        except Exception as e:
            print(f"Error initializing systems: {e}")
            return False
    
    def get_dashboard_data(self):
        """Get data for dashboard display"""
        if not self.prometheus:
            return None
        
        try:
            # System status
            system_status = self.prometheus.get_system_status()
            
            # Recent alerts
            recent_alerts = self.prometheus.database.get_active_alerts()
            
            # Hephaestus stats
            hephaestus_stats = self.hephaestus.get_generation_stats() if self.hephaestus else {}
            
            # System metrics from database
            conn = sqlite3.connect(self.prometheus.database.db_path)
            cursor = conn.cursor()
            
            # Get recent system status entries
            cursor.execute('''
                SELECT system_name, status, cpu_usage, memory_usage, disk_usage, last_heartbeat
                FROM system_status 
                ORDER BY last_heartbeat DESC 
                LIMIT 10
            ''')
            system_metrics = cursor.fetchall()
            
            # Get module registry
            cursor.execute('SELECT module_name, module_type, version, status FROM module_registry')
            modules = cursor.fetchall()
            
            conn.close()
            
            return {
                'system_status': system_status,
                'alerts': [
                    {
                        'severity': alert.severity,
                        'type': alert.alert_type,
                        'description': alert.description,
                        'system': alert.affected_system,
                        'timestamp': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    } for alert in recent_alerts
                ],
                'hephaestus_stats': hephaestus_stats,
                'system_metrics': [
                    {
                        'name': row[0],
                        'status': row[1],
                        'cpu': row[2],
                        'memory': row[3],
                        'disk': row[4],
                        'last_seen': row[5]
                    } for row in system_metrics
                ],
                'modules': [
                    {
                        'name': row[0],
                        'type': row[1],
                        'version': row[2],
                        'status': row[3]
                    } for row in modules
                ],
                'is_running': self.is_running
            }
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            return None


# Initialize web interface
web_interface = PrometheusWebInterface()


@app.route('/')
def dashboard():
    """Main dashboard page"""
    data = web_interface.get_dashboard_data()
    if not data:
        return render_template('error.html', message="System not initialized")
    return render_template('dashboard.html', data=data)


@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    data = web_interface.get_dashboard_data()
    return jsonify(data) if data else jsonify({'error': 'System not initialized'})


@app.route('/api/generate_prompt', methods=['POST'])
def api_generate_prompt():
    """API endpoint to generate Cursor prompts"""
    try:
        if not web_interface.hephaestus:
            return jsonify({'error': 'Hephaestus not initialized'}), 500
        
        data = request.json
        project_name = data.get('project_name', '')
        project_description = data.get('project_description', '')
        
        if not project_name or not project_description:
            return jsonify({'error': 'Project name and description required'}), 400
        
        # Generate prompt
        prompt = web_interface.hephaestus.generate_cursor_prompt(project_name, project_description)
        
        # Save to file
        file_path = web_interface.hephaestus.save_prompt_to_file(prompt)
        
        return jsonify({
            'success': True,
            'prompt_id': prompt.prompt_id,
            'file_path': file_path,
            'complexity': prompt.estimated_complexity,
            'security_level': prompt.security_level,
            'generated_at': prompt.generated_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system_command', methods=['POST'])
def api_system_command():
    """API endpoint for system commands"""
    try:
        data = request.json
        command = data.get('command', '')
        
        if command == 'restart_prometheus':
            if web_interface.prometheus:
                web_interface.prometheus.stop_system()
                time.sleep(2)
                web_interface.prometheus.start_system()
            return jsonify({'success': True, 'message': 'Prometheus restarted'})
        
        elif command == 'run_security_scan':
            if web_interface.prometheus:
                alerts = web_interface.prometheus.security_monitor.scan_system_vulnerabilities()
                for alert in alerts:
                    web_interface.prometheus.database.insert_security_alert(alert)
            return jsonify({'success': True, 'message': f'Security scan completed, {len(alerts)} alerts generated'})
        
        elif command == 'clear_alerts':
            if web_interface.prometheus:
                conn = sqlite3.connect(web_interface.prometheus.database.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE security_alerts SET status = 'RESOLVED' WHERE status = 'ACTIVE'")
                conn.commit()
                conn.close()
            return jsonify({'success': True, 'message': 'All alerts cleared'})
        
        else:
            return jsonify({'error': 'Unknown command'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate')
def generate_page():
    """Prompt generation page"""
    return render_template('generate.html')


@app.route('/logs')
def logs_page():
    """Logs viewing page"""
    try:
        log_dir = Path("/workspace/prometheus_logs")
        log_files = []
        
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                # Read last 100 lines
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-100:] if len(lines) > 100 else lines
                
                log_files.append({
                    'name': log_file.name,
                    'size': log_file.stat().st_size,
                    'modified': datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'content': ''.join(recent_lines)
                })
        
        return render_template('logs.html', log_files=log_files)
    except Exception as e:
        return render_template('error.html', message=f"Error reading logs: {e}")


@app.route('/modules')
def modules_page():
    """Modules management page"""
    data = web_interface.get_dashboard_data()
    return render_template('modules.html', modules=data['modules'] if data else [])


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('status', {'message': 'Connected to Prometheus'})


@socketio.on('request_update')
def handle_update_request():
    """Handle real-time update requests"""
    data = web_interface.get_dashboard_data()
    if data:
        emit('dashboard_update', data)


def create_templates():
    """Create HTML templates for the web interface"""
    templates_dir = Path("/workspace/templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Prometheus Control Center{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #0d1117; color: #c9d1d9; }
        .navbar { background-color: #161b22 !important; }
        .card { background-color: #21262d; border-color: #30363d; }
        .alert-danger { background-color: #da3633; border-color: #f85149; }
        .alert-warning { background-color: #bb8009; border-color: #d29922; }
        .alert-info { background-color: #0969da; border-color: #2f81f7; }
        .btn-primary { background-color: #238636; border-color: #238636; }
        .btn-danger { background-color: #da3633; border-color: #da3633; }
        .prometheus-header { 
            background: linear-gradient(135deg, #ff6b35, #f7931e); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            font-weight: bold;
        }
        .status-online { color: #28a745; }
        .status-offline { color: #dc3545; }
        .status-degraded { color: #ffc107; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand prometheus-header" href="/">
                <i class="fas fa-fire"></i> Prometheus Control Center
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                <a class="nav-link" href="/generate"><i class="fas fa-magic"></i> Generate</a>
                <a class="nav-link" href="/modules"><i class="fas fa-cubes"></i> Modules</a>
                <a class="nav-link" href="/logs"><i class="fas fa-file-alt"></i> Logs</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    # Dashboard template
    dashboard_template = '''{% extends "base.html" %}
{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-server"></i> System Status</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Status:</strong> 
                            <span class="status-{{ 'online' if data.is_running else 'offline' }}">
                                {{ 'RUNNING' if data.is_running else 'STOPPED' }}
                            </span>
                        </p>
                        <p><strong>Uptime:</strong> {{ data.system_status.uptime }}</p>
                        <p><strong>Active Modules:</strong> {{ data.system_status.modules }}</p>
                        <p><strong>Active Alerts:</strong> {{ data.system_status.active_alerts }}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>CPU Usage:</strong> {{ "%.1f"|format(data.system_status.system_resources.cpu) }}%</p>
                        <p><strong>Memory Usage:</strong> {{ "%.1f"|format(data.system_status.system_resources.memory) }}%</p>
                        <p><strong>Disk Usage:</strong> {{ "%.1f"|format(data.system_status.system_resources.disk) }}%</p>
                    </div>
                </div>
                <div class="mt-3">
                    <button class="btn btn-primary btn-sm" onclick="executeCommand('restart_prometheus')">
                        <i class="fas fa-redo"></i> Restart Prometheus
                    </button>
                    <button class="btn btn-warning btn-sm" onclick="executeCommand('run_security_scan')">
                        <i class="fas fa-shield-alt"></i> Run Security Scan
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="executeCommand('clear_alerts')">
                        <i class="fas fa-trash"></i> Clear Alerts
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-hammer"></i> Hephaestus Stats</h5>
            </div>
            <div class="card-body">
                {% if data.hephaestus_stats %}
                <p><strong>Total Generated:</strong> {{ data.hephaestus_stats.total_generated }}</p>
                <p><strong>Success Rate:</strong> {{ data.hephaestus_stats.success_rate }}</p>
                <p><strong>Uptime:</strong> {{ data.hephaestus_stats.uptime }}</p>
                <p><strong>Avg/Hour:</strong> {{ "%.1f"|format(data.hephaestus_stats.avg_per_hour) }}</p>
                {% else %}
                <p class="text-muted">No statistics available</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

{% if data.alerts %}
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-exclamation-triangle"></i> Active Alerts</h5>
            </div>
            <div class="card-body">
                {% for alert in data.alerts %}
                <div class="alert alert-{{ 'danger' if alert.severity == 'HIGH' else 'warning' if alert.severity == 'MEDIUM' else 'info' }}">
                    <strong>{{ alert.severity }}:</strong> {{ alert.description }}
                    <br><small>System: {{ alert.system }} | Time: {{ alert.timestamp }}</small>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endif %}

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-cubes"></i> Registered Modules</h5>
            </div>
            <div class="card-body">
                {% if data.modules %}
                <div class="table-responsive">
                    <table class="table table-dark">
                        <thead>
                            <tr>
                                <th>Module</th>
                                <th>Type</th>
                                <th>Version</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for module in data.modules %}
                            <tr>
                                <td>{{ module.name }}</td>
                                <td>{{ module.type }}</td>
                                <td>{{ module.version }}</td>
                                <td><span class="status-{{ 'online' if module.status == 'ACTIVE' else 'offline' }}">{{ module.status }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted">No modules registered</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
const socket = io();

socket.on('connect', function() {
    console.log('Connected to Prometheus');
});

function executeCommand(command) {
    fetch('/api/system_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({command: command})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    });
}

// Auto-refresh every 30 seconds
setInterval(() => {
    location.reload();
}, 30000);
</script>
{% endblock %}'''
    
    # Generate template
    generate_template = '''{% extends "base.html" %}
{% block title %}Generate Cursor Prompt - Prometheus{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-8 mx-auto">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-magic"></i> Generate Cursor Prompt</h5>
            </div>
            <div class="card-body">
                <form id="generateForm">
                    <div class="mb-3">
                        <label for="projectName" class="form-label">Project Name</label>
                        <input type="text" class="form-control" id="projectName" required>
                    </div>
                    <div class="mb-3">
                        <label for="projectDescription" class="form-label">Project Description</label>
                        <textarea class="form-control" id="projectDescription" rows="10" required 
                                placeholder="Describe your project in detail. Include features, requirements, technology preferences, and any specific constraints..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-cog"></i> Generate Prompt
                    </button>
                </form>
            </div>
        </div>
        
        <div id="resultCard" class="card mt-4" style="display: none;">
            <div class="card-header">
                <h5><i class="fas fa-check-circle"></i> Generated Prompt</h5>
            </div>
            <div class="card-body">
                <div id="resultContent"></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.getElementById('generateForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const projectName = document.getElementById('projectName').value;
    const projectDescription = document.getElementById('projectDescription').value;
    
    fetch('/api/generate_prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            project_name: projectName,
            project_description: projectDescription
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('resultContent').innerHTML = `
                <div class="alert alert-success">
                    <strong>Success!</strong> Cursor prompt generated successfully.
                </div>
                <p><strong>Prompt ID:</strong> ${data.prompt_id}</p>
                <p><strong>Complexity:</strong> ${data.complexity}</p>
                <p><strong>Security Level:</strong> ${data.security_level}</p>
                <p><strong>File Path:</strong> <code>${data.file_path}</code></p>
                <p><strong>Generated:</strong> ${new Date(data.generated_at).toLocaleString()}</p>
            `;
            document.getElementById('resultCard').style.display = 'block';
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error: ' + error.message);
    });
});
</script>
{% endblock %}'''
    
    # Error template
    error_template = '''{% extends "base.html" %}
{% block title %}Error - Prometheus{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-6 mx-auto">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-exclamation-triangle"></i> Error</h5>
            </div>
            <div class="card-body">
                <div class="alert alert-danger">
                    {{ message }}
                </div>
                <a href="/" class="btn btn-primary">Return to Dashboard</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Logs template
    logs_template = '''{% extends "base.html" %}
{% block title %}System Logs - Prometheus{% endblock %}
{% block content %}
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-file-alt"></i> System Logs</h5>
            </div>
            <div class="card-body">
                {% for log_file in log_files %}
                <div class="mb-4">
                    <h6>{{ log_file.name }} 
                        <small class="text-muted">({{ log_file.size }} bytes, modified: {{ log_file.modified }})</small>
                    </h6>
                    <pre class="bg-dark p-3" style="max-height: 400px; overflow-y: auto; font-size: 0.8em;">{{ log_file.content }}</pre>
                </div>
                {% endfor %}
                {% if not log_files %}
                <p class="text-muted">No log files found</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Modules template
    modules_template = '''{% extends "base.html" %}
{% block title %}Modules - Prometheus{% endblock %}
{% block content %}
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-cubes"></i> Module Registry</h5>
            </div>
            <div class="card-body">
                {% if modules %}
                <div class="table-responsive">
                    <table class="table table-dark">
                        <thead>
                            <tr>
                                <th>Module Name</th>
                                <th>Type</th>
                                <th>Version</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for module in modules %}
                            <tr>
                                <td>{{ module.name }}</td>
                                <td>{{ module.type }}</td>
                                <td>{{ module.version }}</td>
                                <td><span class="status-{{ 'online' if module.status == 'ACTIVE' else 'offline' }}">{{ module.status }}</span></td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary">Monitor</button>
                                    <button class="btn btn-sm btn-outline-warning">Restart</button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted">No modules registered</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Write templates
    with open(templates_dir / "base.html", "w") as f:
        f.write(base_template)
    with open(templates_dir / "dashboard.html", "w") as f:
        f.write(dashboard_template)
    with open(templates_dir / "generate.html", "w") as f:
        f.write(generate_template)
    with open(templates_dir / "error.html", "w") as f:
        f.write(error_template)
    with open(templates_dir / "logs.html", "w") as f:
        f.write(logs_template)
    with open(templates_dir / "modules.html", "w") as f:
        f.write(modules_template)


def run_web_interface():
    """Run the web interface"""
    print("🌐 Starting Prometheus Web Interface...")
    
    # Create templates
    create_templates()
    
    # Initialize systems
    if not web_interface.initialize_systems():
        print("❌ Failed to initialize systems")
        return
    
    print("✅ Systems initialized successfully")
    print("🚀 Web interface available at: http://localhost:5000")
    
    # Run the Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    run_web_interface()