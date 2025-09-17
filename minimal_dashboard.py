#!/usr/bin/env python3
"""
Minimal Prometheus Web Dashboard
Simple interface to input project descriptions and see generated Cursor prompts
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import time
from datetime import datetime
from pathlib import Path
import os

app = Flask(__name__)

# Simple in-memory storage for this minimal version
generated_prompts = []
system_stats = {
    'total_generated': 0,
    'last_generation': None,
    'uptime_start': datetime.now()
}

class MinimalHephaestus:
    """Simplified Hephaestus for the minimal dashboard"""
    
    def __init__(self):
        self.templates = {
            'web_app': '''Project: {project_name}

Create a modern web application with the following requirements:
{description}

Technical Implementation:
1. Frontend: React with TypeScript
2. Backend: Node.js with Express
3. Database: PostgreSQL
4. Authentication: JWT tokens
5. Styling: Tailwind CSS

Key Features to Implement:
- User authentication and authorization
- Responsive design for all devices
- RESTful API endpoints
- Input validation and sanitization
- Error handling and logging
- Unit and integration tests

Security Considerations:
- HTTPS/SSL encryption
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure session management

Deployment:
- Docker containerization
- Environment configuration
- Database migrations
- Health check endpoints
- Monitoring and logging setup

Please implement this project following modern development best practices with clean, maintainable code.''',

            'mobile_app': '''Project: {project_name}

Create a mobile application with the following specifications:
{description}

Technical Stack:
1. Framework: React Native
2. State Management: Redux Toolkit
3. Navigation: React Navigation
4. UI Components: Native Base
5. Backend API: RESTful services

Core Implementation:
- Cross-platform compatibility (iOS/Android)
- Native device features integration
- Offline functionality support
- Push notifications
- Secure data storage
- Performance optimization

Security Features:
- Biometric authentication
- Encrypted local storage
- Secure API communication
- Certificate pinning
- Privacy compliance

Testing & Deployment:
- Unit and integration tests
- Device compatibility testing
- App store deployment preparation
- Beta testing distribution
- Analytics integration

Build a production-ready mobile app with excellent user experience and robust security.''',

            'api_service': '''Project: {project_name}

Develop a RESTful API service with the following requirements:
{description}

Technical Architecture:
1. Framework: FastAPI (Python) or Express.js (Node.js)
2. Database: PostgreSQL with connection pooling
3. Authentication: OAuth 2.0 / JWT
4. Documentation: OpenAPI/Swagger
5. Caching: Redis

API Design:
- RESTful endpoints with proper HTTP methods
- Consistent response formats
- Comprehensive error handling
- Request/response validation
- Rate limiting and throttling
- API versioning strategy

Security Implementation:
- Authentication and authorization
- Input validation and sanitization
- SQL injection prevention
- API rate limiting
- CORS configuration
- Security headers

Performance & Scalability:
- Database query optimization
- Caching strategies
- Async/await patterns
- Connection pooling
- Load balancing ready
- Monitoring and metrics

Deployment:
- Docker containerization
- Environment configuration
- Database migrations
- Health check endpoints
- CI/CD pipeline integration

Create a robust, scalable API service following industry best practices.''',

            'automation_script': '''Project: {project_name}

Create an automation script/tool with the following functionality:
{description}

Technical Implementation:
1. Language: Python 3.9+
2. Task Scheduling: APScheduler or Celery
3. Configuration: YAML/JSON config files
4. Logging: Structured logging with rotation
5. Error Handling: Comprehensive exception handling

Core Features:
- Configurable automation workflows
- Error recovery and retry mechanisms
- Progress tracking and reporting
- Email/webhook notifications
- Dry-run mode for testing
- Command-line interface

Reliability Features:
- Graceful error handling
- Automatic retries with backoff
- Health checks and monitoring
- Resource usage optimization
- Concurrent task execution
- State persistence

Monitoring & Logging:
- Detailed execution logs
- Performance metrics
- Error tracking and alerting
- Progress reporting
- Resource usage monitoring
- Audit trail maintenance

Deployment:
- Virtual environment setup
- Configuration management
- Service/daemon setup
- Monitoring integration
- Documentation and runbooks

Build a reliable automation solution that can run unattended with proper monitoring and error handling.'''
        }
    
    def analyze_project(self, description):
        """Simple project type detection"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['website', 'web app', 'dashboard', 'frontend', 'backend']):
            return 'web_app'
        elif any(word in description_lower for word in ['mobile', 'app', 'android', 'ios', 'react native']):
            return 'mobile_app'
        elif any(word in description_lower for word in ['api', 'service', 'endpoint', 'rest', 'graphql']):
            return 'api_service'
        elif any(word in description_lower for word in ['automation', 'script', 'bot', 'scheduler', 'task']):
            return 'automation_script'
        else:
            return 'web_app'  # Default
    
    def generate_prompt(self, project_name, description):
        """Generate a Cursor prompt"""
        project_type = self.analyze_project(description)
        template = self.templates.get(project_type, self.templates['web_app'])
        
        prompt_content = template.format(
            project_name=project_name,
            description=description
        )
        
        return {
            'id': f"prompt_{int(time.time())}",
            'project_name': project_name,
            'project_type': project_type,
            'description': description,
            'prompt_content': prompt_content,
            'generated_at': datetime.now().isoformat(),
            'word_count': len(prompt_content.split())
        }

# Initialize minimal Hephaestus
hephaestus = MinimalHephaestus()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('minimal_dashboard.html', stats=system_stats)

@app.route('/api/generate', methods=['POST'])
def generate_prompt():
    """Generate a Cursor prompt"""
    try:
        data = request.json
        project_name = data.get('project_name', '').strip()
        description = data.get('description', '').strip()
        
        if not project_name or not description:
            return jsonify({'error': 'Project name and description are required'}), 400
        
        # Generate prompt
        prompt = hephaestus.generate_prompt(project_name, description)
        
        # Store in memory
        generated_prompts.append(prompt)
        
        # Update stats
        system_stats['total_generated'] += 1
        system_stats['last_generation'] = datetime.now().isoformat()
        
        # Keep only last 10 prompts in memory
        if len(generated_prompts) > 10:
            generated_prompts.pop(0)
        
        return jsonify({
            'success': True,
            'prompt': prompt
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prompts')
def get_prompts():
    """Get recent prompts"""
    return jsonify({
        'prompts': generated_prompts[-5:],  # Last 5 prompts
        'total': len(generated_prompts)
    })

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    uptime = datetime.now() - system_stats['uptime_start']
    return jsonify({
        'total_generated': system_stats['total_generated'],
        'last_generation': system_stats['last_generation'],
        'uptime': str(uptime),
        'recent_prompts': len(generated_prompts)
    })

@app.route('/api/download/<prompt_id>')
def download_prompt(prompt_id):
    """Download a specific prompt as text file"""
    prompt = next((p for p in generated_prompts if p['id'] == prompt_id), None)
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    # Create temporary file
    temp_dir = Path('/tmp')
    temp_file = temp_dir / f"{prompt['project_name'].replace(' ', '_')}_{prompt_id}.txt"
    
    content = f"""# {prompt['project_name']}
Generated: {prompt['generated_at']}
Type: {prompt['project_type']}
Word Count: {prompt['word_count']}

## Project Description
{prompt['description']}

## Generated Cursor Prompt
{prompt['prompt_content']}

---
Generated by Prometheus Minimal Dashboard
"""
    
    with open(temp_file, 'w') as f:
        f.write(content)
    
    return send_from_directory(temp_dir, temp_file.name, as_attachment=True)

def create_template():
    """Create the HTML template"""
    template_dir = Path('templates')
    template_dir.mkdir(exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 Prometheus Minimal Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .prometheus-glow {
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        }
        .typing-animation {
            border-right: 2px solid #667eea;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { border-right-color: #667eea; }
            51%, 100% { border-right-color: transparent; }
        }
        .prompt-content {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            line-height: 1.6;
        }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <!-- Header -->
    <div class="gradient-bg p-6 prometheus-glow">
        <div class="container mx-auto">
            <h1 class="text-4xl font-bold text-center mb-2">🔥 Prometheus Dashboard</h1>
            <p class="text-center text-blue-100">Transform project ideas into detailed Cursor prompts</p>
        </div>
    </div>

    <div class="container mx-auto p-6">
        <!-- Stats Bar -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-gray-800 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-blue-400" id="totalGenerated">{{ stats.total_generated }}</div>
                <div class="text-sm text-gray-400">Total Generated</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-green-400" id="uptime">Starting...</div>
                <div class="text-sm text-gray-400">System Uptime</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-purple-400" id="lastGeneration">Never</div>
                <div class="text-sm text-gray-400">Last Generation</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Input Section -->
            <div class="bg-gray-800 rounded-lg p-6">
                <h2 class="text-2xl font-bold mb-6 text-center">📝 Project Input</h2>
                
                <form id="projectForm" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium mb-2">Project Name</label>
                        <input 
                            type="text" 
                            id="projectName" 
                            placeholder="e.g., Task Manager App"
                            class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                            required
                        >
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium mb-2">Project Description</label>
                        <textarea 
                            id="projectDescription" 
                            rows="8"
                            placeholder="Describe your project in detail. Include features, requirements, technology preferences, and any specific constraints..."
                            class="w-full p-3 bg-gray-700 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
                            required
                        ></textarea>
                    </div>
                    
                    <button 
                        type="submit" 
                        id="generateBtn"
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200"
                    >
                        🚀 Generate Cursor Prompt
                    </button>
                </form>
            </div>

            <!-- Output Section -->
            <div class="bg-gray-800 rounded-lg p-6">
                <h2 class="text-2xl font-bold mb-6 text-center">🔨 Generated Prompt</h2>
                
                <div id="outputSection" class="hidden">
                    <div class="mb-4 p-3 bg-gray-700 rounded-lg">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm text-gray-400">Project:</span>
                            <span id="outputProjectName" class="font-medium"></span>
                        </div>
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm text-gray-400">Type:</span>
                            <span id="outputProjectType" class="font-medium text-blue-400"></span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-sm text-gray-400">Words:</span>
                            <span id="outputWordCount" class="font-medium text-green-400"></span>
                        </div>
                    </div>
                    
                    <div class="relative">
                        <button 
                            id="copyBtn"
                            class="absolute top-2 right-2 bg-blue-600 hover:bg-blue-700 text-xs px-3 py-1 rounded"
                        >
                            📋 Copy
                        </button>
                        <button 
                            id="downloadBtn"
                            class="absolute top-2 right-20 bg-green-600 hover:bg-green-700 text-xs px-3 py-1 rounded"
                        >
                            💾 Download
                        </button>
                        <pre id="promptOutput" class="prompt-content bg-gray-900 p-4 rounded-lg text-sm overflow-auto max-h-96 pr-32"></pre>
                    </div>
                </div>
                
                <div id="placeholderSection" class="text-center text-gray-500 py-12">
                    <div class="text-6xl mb-4">🤖</div>
                    <p>Enter a project description above to generate a detailed Cursor prompt</p>
                </div>
            </div>
        </div>

        <!-- Recent Prompts -->
        <div class="mt-8 bg-gray-800 rounded-lg p-6">
            <h3 class="text-xl font-bold mb-4">📚 Recent Prompts</h3>
            <div id="recentPrompts" class="space-y-2">
                <p class="text-gray-500 text-center py-4">No prompts generated yet</p>
            </div>
        </div>
    </div>

    <!-- Loading Modal -->
    <div id="loadingModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center hidden z-50">
        <div class="bg-gray-800 rounded-lg p-8 text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p>Generating your Cursor prompt...</p>
        </div>
    </div>

    <script>
        let currentPrompt = null;

        // Update stats periodically
        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('totalGenerated').textContent = data.total_generated;
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('lastGeneration').textContent = 
                        data.last_generation ? new Date(data.last_generation).toLocaleTimeString() : 'Never';
                });
        }

        // Load recent prompts
        function loadRecentPrompts() {
            fetch('/api/prompts')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('recentPrompts');
                    if (data.prompts.length === 0) {
                        container.innerHTML = '<p class="text-gray-500 text-center py-4">No prompts generated yet</p>';
                        return;
                    }
                    
                    container.innerHTML = data.prompts.map(prompt => `
                        <div class="bg-gray-700 rounded p-3 cursor-pointer hover:bg-gray-600 transition duration-200" 
                             onclick="loadPrompt('${prompt.id}')">
                            <div class="flex justify-between items-center">
                                <span class="font-medium">${prompt.project_name}</span>
                                <span class="text-xs text-gray-400">${new Date(prompt.generated_at).toLocaleTimeString()}</span>
                            </div>
                            <div class="text-sm text-gray-400 mt-1">${prompt.project_type} • ${prompt.word_count} words</div>
                        </div>
                    `).join('');
                });
        }

        // Load a specific prompt
        function loadPrompt(promptId) {
            fetch('/api/prompts')
                .then(response => response.json())
                .then(data => {
                    const prompt = data.prompts.find(p => p.id === promptId);
                    if (prompt) {
                        displayPrompt(prompt);
                    }
                });
        }

        // Display prompt in output section
        function displayPrompt(prompt) {
            currentPrompt = prompt;
            
            document.getElementById('outputProjectName').textContent = prompt.project_name;
            document.getElementById('outputProjectType').textContent = prompt.project_type.replace('_', ' ').toUpperCase();
            document.getElementById('outputWordCount').textContent = prompt.word_count;
            document.getElementById('promptOutput').textContent = prompt.prompt_content;
            
            document.getElementById('placeholderSection').classList.add('hidden');
            document.getElementById('outputSection').classList.remove('hidden');
        }

        // Handle form submission
        document.getElementById('projectForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const projectName = document.getElementById('projectName').value.trim();
            const projectDescription = document.getElementById('projectDescription').value.trim();
            
            if (!projectName || !projectDescription) {
                alert('Please fill in both project name and description');
                return;
            }
            
            // Show loading
            document.getElementById('loadingModal').classList.remove('hidden');
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('generateBtn').textContent = '⏳ Generating...';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        project_name: projectName,
                        project_description: projectDescription
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayPrompt(data.prompt);
                    updateStats();
                    loadRecentPrompts();
                    
                    // Clear form
                    document.getElementById('projectForm').reset();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Network error: ' + error.message);
            } finally {
                // Hide loading
                document.getElementById('loadingModal').classList.add('hidden');
                document.getElementById('generateBtn').disabled = false;
                document.getElementById('generateBtn').textContent = '🚀 Generate Cursor Prompt';
            }
        });

        // Copy to clipboard
        document.getElementById('copyBtn').addEventListener('click', () => {
            if (currentPrompt) {
                navigator.clipboard.writeText(currentPrompt.prompt_content).then(() => {
                    const btn = document.getElementById('copyBtn');
                    const originalText = btn.textContent;
                    btn.textContent = '✅ Copied!';
                    setTimeout(() => {
                        btn.textContent = originalText;
                    }, 2000);
                });
            }
        });

        // Download prompt
        document.getElementById('downloadBtn').addEventListener('click', () => {
            if (currentPrompt) {
                window.location.href = `/api/download/${currentPrompt.id}`;
            }
        });

        // Initialize
        updateStats();
        loadRecentPrompts();
        setInterval(updateStats, 30000); // Update every 30 seconds
        setInterval(loadRecentPrompts, 30000);
    </script>
</body>
</html>'''
    
    with open(template_dir / 'minimal_dashboard.html', 'w') as f:
        f.write(html_content)

if __name__ == '__main__':
    print("🔥 Starting Prometheus Minimal Dashboard")
    print("=" * 50)
    
    # Create template
    create_template()
    print("✅ Template created")
    
    print("🌐 Dashboard starting on http://localhost:5001")
    print("💡 Enter project descriptions and get Cursor prompts!")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")