#!/usr/bin/env python3
"""
Hephaestus - Project Description to Cursor Prompt Converter
Autonomous module for generating comprehensive development prompts
"""

import json
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sqlite3
from pathlib import Path
import requests
import threading


@dataclass
class ProjectRequirement:
    """Project requirement structure"""
    category: str
    priority: str  # HIGH, MEDIUM, LOW
    description: str
    technical_details: List[str]
    dependencies: List[str]
    security_considerations: List[str]


@dataclass
class CursorPrompt:
    """Generated Cursor prompt structure"""
    project_name: str
    prompt_id: str
    generated_at: datetime
    prompt_content: str
    technical_stack: List[str]
    estimated_complexity: str
    security_level: str
    deployment_instructions: str
    testing_requirements: str


class ProjectAnalyzer:
    """Analyzes project descriptions and extracts requirements"""
    
    def __init__(self):
        self.tech_keywords = {
            'web': ['website', 'web app', 'frontend', 'backend', 'api', 'rest', 'graphql'],
            'mobile': ['android', 'ios', 'mobile app', 'apk', 'react native', 'flutter'],
            'ai': ['ai', 'machine learning', 'neural network', 'nlp', 'computer vision'],
            'database': ['database', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql'],
            'security': ['encryption', 'authentication', 'authorization', 'secure', 'crypto'],
            'monitoring': ['monitoring', 'logging', 'analytics', 'metrics', 'alerts'],
            'automation': ['automation', 'bot', 'script', 'scheduler', 'workflow']
        }
        
        self.complexity_indicators = {
            'simple': ['simple', 'basic', 'minimal', 'quick', 'prototype'],
            'medium': ['moderate', 'standard', 'typical', 'regular'],
            'complex': ['complex', 'advanced', 'enterprise', 'scalable', 'distributed', 'microservices']
        }
        
        self.security_levels = {
            'basic': ['basic security', 'simple auth'],
            'standard': ['secure', 'authentication', 'authorization'],
            'high': ['encryption', 'end-to-end', 'zero-trust', 'compliance', 'audit']
        }
    
    def analyze_project_description(self, description: str) -> Dict[str, Any]:
        """Analyze project description and extract key information"""
        description_lower = description.lower()
        
        # Detect technology stack
        detected_tech = []
        for category, keywords in self.tech_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                detected_tech.append(category)
        
        # Detect complexity
        complexity = 'medium'  # default
        for level, indicators in self.complexity_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                complexity = level
                break
        
        # Detect security requirements
        security_level = 'standard'  # default
        for level, indicators in self.security_levels.items():
            if any(indicator in description_lower for indicator in indicators):
                security_level = level
                break
        
        # Extract specific requirements using regex patterns
        requirements = []
        
        # Look for numbered lists or bullet points
        numbered_pattern = r'(?:^|\n)\s*(?:\d+\.|\-|\*)\s*(.+?)(?=\n|$)'
        matches = re.findall(numbered_pattern, description, re.MULTILINE)
        for match in matches:
            if len(match.strip()) > 10:  # Filter out short matches
                requirements.append(match.strip())
        
        # Look for "must have" or "should" statements
        requirement_patterns = [
            r'(?:must|should|needs? to|requires?)\s+(.+?)(?:\.|,|\n|$)',
            r'(?:implement|create|build|develop)\s+(.+?)(?:\.|,|\n|$)'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    requirements.append(match.strip())
        
        return {
            'detected_technologies': detected_tech,
            'complexity': complexity,
            'security_level': security_level,
            'extracted_requirements': requirements,
            'word_count': len(description.split()),
            'has_technical_details': any(tech in description_lower for tech in 
                                       ['api', 'database', 'server', 'client', 'framework', 'library'])
        }


class PromptGenerator:
    """Generates comprehensive Cursor prompts from analyzed requirements"""
    
    def __init__(self):
        self.prompt_templates = self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for different project types"""
        return {
            'web_app': '''Project Name: "{project_name}"

Project Description:
{project_description}

Technical Requirements:
{technical_requirements}

Architecture & Implementation:
1. Create a modern, scalable web application with the following structure:
   - Frontend: {frontend_tech}
   - Backend: {backend_tech}
   - Database: {database_tech}
   - Authentication: {auth_method}

2. Security Implementation:
   - {security_requirements}
   - Input validation and sanitization
   - HTTPS/SSL encryption
   - Secure session management
   - API rate limiting and protection

3. Performance & Scalability:
   - Implement caching strategies
   - Database query optimization
   - Lazy loading where appropriate
   - Responsive design for all devices
   - Error handling and logging

4. Development Best Practices:
   - Clean, maintainable code structure
   - Comprehensive error handling
   - Unit and integration tests
   - Documentation for all APIs
   - Version control with meaningful commits

5. Deployment & Monitoring:
   - Containerized deployment (Docker)
   - Environment configuration management
   - Health checks and monitoring endpoints
   - Logging and analytics integration
   - Backup and recovery procedures

6. Integration Requirements:
   {integration_requirements}

Deliverables:
- Fully functional web application
- Complete source code with documentation
- Deployment scripts and configuration
- Testing suite with coverage reports
- User manual and API documentation

Please implement this project with production-ready code, following industry best practices for security, performance, and maintainability.''',
            
            'mobile_app': '''Project Name: "{project_name}"

Project Description:
{project_description}

Mobile Application Requirements:
{technical_requirements}

Implementation Specifications:
1. Mobile Platform Development:
   - Target Platform(s): {target_platforms}
   - Development Framework: {mobile_framework}
   - Minimum SDK Version: {min_sdk}
   - UI/UX Framework: {ui_framework}

2. Core Features Implementation:
   {core_features}

3. Security & Privacy:
   - {security_requirements}
   - Data encryption at rest and in transit
   - Secure authentication and authorization
   - Privacy compliance (GDPR, CCPA if applicable)
   - Secure storage of sensitive data

4. Performance Optimization:
   - Efficient memory management
   - Battery optimization
   - Network request optimization
   - Image and asset optimization
   - Smooth animations and transitions

5. Device Integration:
   - Camera and media access (if needed)
   - Location services (if required)
   - Push notifications
   - Offline functionality
   - Device storage management

6. Testing & Quality Assurance:
   - Unit testing framework
   - UI automation testing
   - Performance testing
   - Device compatibility testing
   - Security vulnerability testing

7. Deployment Preparation:
   - App store optimization
   - Release build configuration
   - Code signing and certificates
   - Beta testing distribution
   - Analytics and crash reporting

Deliverables:
- Complete mobile application
- Source code with documentation
- APK/IPA files for distribution
- Testing reports and documentation
- Deployment guide and app store assets

Build a production-ready mobile application with excellent user experience, robust security, and optimal performance across target devices.''',
            
            'ai_system': '''Project Name: "{project_name}"

Project Description:
{project_description}

AI System Requirements:
{technical_requirements}

AI Architecture & Implementation:
1. Machine Learning Framework:
   - Primary ML Framework: {ml_framework}
   - Model Architecture: {model_architecture}
   - Training Infrastructure: {training_setup}
   - Data Processing Pipeline: {data_pipeline}

2. Data Management:
   - {data_requirements}
   - Data validation and cleaning
   - Feature engineering and selection
   - Data versioning and lineage
   - Privacy and compliance handling

3. Model Development:
   - Model training and validation
   - Hyperparameter optimization
   - Cross-validation strategies
   - Model interpretability and explainability
   - Bias detection and mitigation

4. Production Deployment:
   - Model serving infrastructure
   - API endpoints for inference
   - Real-time and batch processing
   - Model monitoring and drift detection
   - A/B testing framework

5. Security & Ethics:
   - {security_requirements}
   - Data privacy protection
   - Model security and adversarial robustness
   - Ethical AI considerations
   - Audit trails and compliance

6. Performance & Scalability:
   - Model optimization and quantization
   - Distributed training capabilities
   - Auto-scaling inference services
   - Caching and performance monitoring
   - Resource usage optimization

7. Monitoring & Maintenance:
   - Model performance tracking
   - Data quality monitoring
   - Automated retraining pipelines
   - Alert systems for anomalies
   - Continuous integration/deployment

Deliverables:
- Complete AI system with trained models
- Data processing and training pipelines
- Production-ready inference API
- Monitoring and maintenance tools
- Comprehensive documentation and guides

Create a robust, scalable AI system with strong governance, monitoring, and ethical considerations built-in from the start.''',
            
            'automation_system': '''Project Name: "{project_name}"

Project Description:
{project_description}

Automation System Requirements:
{technical_requirements}

Automation Architecture & Implementation:
1. System Architecture:
   - Core Automation Engine: {automation_framework}
   - Task Scheduler: {scheduler_type}
   - Message Queue: {queue_system}
   - Configuration Management: {config_system}

2. Automation Features:
   {automation_features}

3. Integration Capabilities:
   - API integrations and webhooks
   - Database connectivity
   - File system operations
   - External service integrations
   - Email and notification systems

4. Monitoring & Reliability:
   - {monitoring_requirements}
   - Health checks and heartbeat monitoring
   - Error handling and retry mechanisms
   - Logging and audit trails
   - Performance metrics and alerts

5. Security Implementation:
   - {security_requirements}
   - Secure credential management
   - Access control and permissions
   - Encrypted communications
   - Audit logging and compliance

6. Scalability & Performance:
   - Horizontal scaling capabilities
   - Load balancing and distribution
   - Resource usage optimization
   - Concurrent task execution
   - Efficient data processing

7. User Interface & Control:
   - Web-based dashboard
   - Task configuration interface
   - Real-time monitoring views
   - Report generation
   - Manual override controls

8. Deployment & Maintenance:
   - Containerized deployment
   - Configuration management
   - Backup and recovery procedures
   - Update and patch management
   - Documentation and runbooks

Deliverables:
- Complete automation system
- Web dashboard and control interface
- Configuration and deployment scripts
- Monitoring and alerting setup
- Operations documentation and guides

Build a reliable, scalable automation system with comprehensive monitoring, security, and management capabilities.'''
        }
    
    def generate_prompt(self, project_name: str, description: str, analysis: Dict[str, Any]) -> CursorPrompt:
        """Generate a comprehensive Cursor prompt"""
        
        # Determine project type based on analysis
        project_type = self._determine_project_type(analysis['detected_technologies'])
        
        # Select appropriate template
        template = self._select_template(project_type)
        
        # Generate technical stack recommendations
        tech_stack = self._recommend_tech_stack(analysis)
        
        # Generate security requirements
        security_reqs = self._generate_security_requirements(analysis['security_level'])
        
        # Generate integration requirements
        integration_reqs = self._generate_integration_requirements(analysis)
        
        # Format the prompt
        prompt_content = template.format(
            project_name=project_name,
            project_description=description,
            technical_requirements=self._format_requirements(analysis['extracted_requirements']),
            frontend_tech=tech_stack.get('frontend', 'React with TypeScript'),
            backend_tech=tech_stack.get('backend', 'Node.js with Express'),
            database_tech=tech_stack.get('database', 'PostgreSQL'),
            auth_method=tech_stack.get('auth', 'JWT with OAuth2'),
            security_requirements=security_reqs,
            integration_requirements=integration_reqs,
            target_platforms=tech_stack.get('platforms', 'Android and iOS'),
            mobile_framework=tech_stack.get('mobile_framework', 'React Native'),
            min_sdk=tech_stack.get('min_sdk', 'Android API 21, iOS 12'),
            ui_framework=tech_stack.get('ui_framework', 'Native UI components'),
            core_features=self._format_requirements(analysis['extracted_requirements']),
            ml_framework=tech_stack.get('ml_framework', 'TensorFlow/PyTorch'),
            model_architecture=tech_stack.get('model_arch', 'Neural Network'),
            training_setup=tech_stack.get('training', 'Cloud-based training'),
            data_pipeline=tech_stack.get('data_pipeline', 'Apache Airflow'),
            data_requirements=self._generate_data_requirements(analysis),
            automation_framework=tech_stack.get('automation', 'Python with Celery'),
            scheduler_type=tech_stack.get('scheduler', 'Cron with Redis'),
            queue_system=tech_stack.get('queue', 'Redis/RabbitMQ'),
            config_system=tech_stack.get('config', 'YAML with environment variables'),
            automation_features=self._format_requirements(analysis['extracted_requirements']),
            monitoring_requirements=self._generate_monitoring_requirements(analysis)
        )
        
        # Create prompt object
        prompt = CursorPrompt(
            project_name=project_name,
            prompt_id=f"hep_{int(time.time())}_{hash(project_name) % 10000}",
            generated_at=datetime.now(),
            prompt_content=prompt_content,
            technical_stack=list(tech_stack.values()),
            estimated_complexity=analysis['complexity'],
            security_level=analysis['security_level'],
            deployment_instructions=self._generate_deployment_instructions(tech_stack),
            testing_requirements=self._generate_testing_requirements(analysis)
        )
        
        return prompt
    
    def _determine_project_type(self, technologies: List[str]) -> str:
        """Determine the primary project type"""
        if 'mobile' in technologies:
            return 'mobile_app'
        elif 'ai' in technologies:
            return 'ai_system'
        elif 'automation' in technologies:
            return 'automation_system'
        else:
            return 'web_app'
    
    def _select_template(self, project_type: str) -> str:
        """Select the appropriate template"""
        return self.prompt_templates.get(project_type, self.prompt_templates['web_app'])
    
    def _recommend_tech_stack(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Recommend technology stack based on analysis"""
        stack = {}
        technologies = analysis['detected_technologies']
        complexity = analysis['complexity']
        
        # Frontend recommendations
        if 'web' in technologies:
            if complexity == 'complex':
                stack['frontend'] = 'React with TypeScript and Next.js'
            else:
                stack['frontend'] = 'React with JavaScript'
        
        # Backend recommendations
        if 'web' in technologies:
            if 'ai' in technologies:
                stack['backend'] = 'Python with FastAPI'
            elif complexity == 'complex':
                stack['backend'] = 'Node.js with Express and TypeScript'
            else:
                stack['backend'] = 'Node.js with Express'
        
        # Database recommendations
        if 'database' in technologies:
            if complexity == 'complex':
                stack['database'] = 'PostgreSQL with Redis caching'
            else:
                stack['database'] = 'PostgreSQL'
        
        # Mobile recommendations
        if 'mobile' in technologies:
            stack['platforms'] = 'Android and iOS'
            stack['mobile_framework'] = 'React Native'
            stack['min_sdk'] = 'Android API 23, iOS 13'
            stack['ui_framework'] = 'React Native UI components'
        
        # AI recommendations
        if 'ai' in technologies:
            stack['ml_framework'] = 'TensorFlow 2.x with Keras'
            stack['model_arch'] = 'Deep Neural Network'
            stack['training'] = 'Google Colab/AWS SageMaker'
            stack['data_pipeline'] = 'Apache Airflow with Pandas'
        
        # Automation recommendations
        if 'automation' in technologies:
            stack['automation'] = 'Python with Celery and Redis'
            stack['scheduler'] = 'Celery Beat with Redis broker'
            stack['queue'] = 'Redis for lightweight tasks, RabbitMQ for complex workflows'
            stack['config'] = 'YAML configuration with environment variables'
        
        return stack
    
    def _generate_security_requirements(self, security_level: str) -> str:
        """Generate security requirements based on level"""
        base_security = [
            "Input validation and sanitization",
            "SQL injection prevention",
            "XSS protection",
            "CSRF protection"
        ]
        
        if security_level == 'high':
            base_security.extend([
                "End-to-end encryption for all data",
                "Multi-factor authentication",
                "Zero-trust architecture",
                "Regular security audits and penetration testing",
                "Compliance with GDPR, HIPAA, or relevant standards"
            ])
        elif security_level == 'standard':
            base_security.extend([
                "HTTPS/TLS encryption",
                "Secure authentication and session management",
                "Role-based access control",
                "Security headers and CORS configuration"
            ])
        
        return '\n   - '.join(base_security)
    
    def _format_requirements(self, requirements: List[str]) -> str:
        """Format requirements list for prompt"""
        if not requirements:
            return "- Core functionality as described in project description"
        
        formatted = []
        for i, req in enumerate(requirements[:10], 1):  # Limit to 10 requirements
            formatted.append(f"{i}. {req}")
        
        return '\n   '.join(formatted)
    
    def _generate_integration_requirements(self, analysis: Dict[str, Any]) -> str:
        """Generate integration requirements"""
        integrations = []
        
        if 'monitoring' in analysis['detected_technologies']:
            integrations.append("Prometheus monitoring integration")
            integrations.append("Real-time alerting system")
        
        integrations.extend([
            "RESTful API endpoints with OpenAPI documentation",
            "Database integration with connection pooling",
            "Logging integration with structured logging",
            "Environment-based configuration management"
        ])
        
        return '\n   '.join(integrations)
    
    def _generate_data_requirements(self, analysis: Dict[str, Any]) -> str:
        """Generate data requirements for AI projects"""
        return """Data collection, cleaning, and preprocessing pipeline
   - Feature engineering and selection
   - Data validation and quality checks
   - Secure data storage and access controls"""
    
    def _generate_monitoring_requirements(self, analysis: Dict[str, Any]) -> str:
        """Generate monitoring requirements"""
        return """Real-time system monitoring and alerting
   - Performance metrics and dashboards
   - Error tracking and logging
   - Health checks and status endpoints"""
    
    def _generate_deployment_instructions(self, tech_stack: Dict[str, str]) -> str:
        """Generate deployment instructions"""
        return """1. Containerize application with Docker
2. Set up CI/CD pipeline with automated testing
3. Configure environment variables and secrets
4. Deploy to cloud platform (AWS/Azure/GCP)
5. Set up monitoring and logging
6. Configure backup and disaster recovery"""
    
    def _generate_testing_requirements(self, analysis: Dict[str, Any]) -> str:
        """Generate testing requirements"""
        return """1. Unit tests with >80% code coverage
2. Integration tests for all API endpoints
3. End-to-end testing for critical user flows
4. Performance and load testing
5. Security vulnerability testing
6. Automated testing in CI/CD pipeline"""


class HephaestusCore:
    """Main Hephaestus system class"""
    
    def __init__(self, prometheus_integration: bool = True):
        self.analyzer = ProjectAnalyzer()
        self.generator = PromptGenerator()
        self.prometheus_integration = prometheus_integration
        
        # Database setup
        self.db_path = Path("/workspace/prometheus_data/hephaestus.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
        # Statistics
        self.generated_prompts = 0
        self.successful_generations = 0
        self.start_time = datetime.now()
        
        print("🔨 Hephaestus initialized - Ready to forge Cursor prompts")
    
    def _init_database(self):
        """Initialize Hephaestus database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id TEXT UNIQUE NOT NULL,
                project_name TEXT NOT NULL,
                project_description TEXT NOT NULL,
                prompt_content TEXT NOT NULL,
                technical_stack TEXT,
                complexity TEXT,
                security_level TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'GENERATED'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generation_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_cursor_prompt(self, project_name: str, project_description: str) -> CursorPrompt:
        """Generate a comprehensive Cursor prompt from project description"""
        try:
            print(f"🔍 Analyzing project: {project_name}")
            
            # Analyze the project description
            analysis = self.analyzer.analyze_project_description(project_description)
            
            print(f"📊 Analysis complete - Technologies: {analysis['detected_technologies']}, "
                  f"Complexity: {analysis['complexity']}, Security: {analysis['security_level']}")
            
            # Generate the prompt
            prompt = self.generator.generate_prompt(project_name, project_description, analysis)
            
            # Store in database
            self._store_prompt(prompt, project_description, analysis)
            
            # Update statistics
            self.generated_prompts += 1
            self.successful_generations += 1
            
            # Report to Prometheus if integrated
            if self.prometheus_integration:
                self._report_to_prometheus("prompt_generated", 1)
            
            print(f"✅ Cursor prompt generated successfully - ID: {prompt.prompt_id}")
            
            return prompt
            
        except Exception as e:
            print(f"❌ Error generating prompt: {e}")
            if self.prometheus_integration:
                self._report_to_prometheus("prompt_generation_error", 1)
            raise
    
    def _store_prompt(self, prompt: CursorPrompt, description: str, analysis: Dict[str, Any]):
        """Store generated prompt in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO generated_prompts 
            (prompt_id, project_name, project_description, prompt_content, 
             technical_stack, complexity, security_level, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prompt.prompt_id,
            prompt.project_name,
            description,
            prompt.prompt_content,
            json.dumps(prompt.technical_stack),
            prompt.estimated_complexity,
            prompt.security_level,
            prompt.generated_at
        ))
        
        conn.commit()
        conn.close()
    
    def _report_to_prometheus(self, metric_name: str, value: float):
        """Report metrics to Prometheus"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO generation_metrics (metric_name, metric_value)
                VALUES (?, ?)
            ''', (metric_name, value))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not report to Prometheus: {e}")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        uptime = datetime.now() - self.start_time
        success_rate = (self.successful_generations / max(self.generated_prompts, 1)) * 100
        
        return {
            'total_generated': self.generated_prompts,
            'successful_generations': self.successful_generations,
            'success_rate': f"{success_rate:.1f}%",
            'uptime': str(uptime),
            'avg_per_hour': self.generated_prompts / max(uptime.total_seconds() / 3600, 0.1)
        }
    
    def save_prompt_to_file(self, prompt: CursorPrompt, output_dir: str = "/workspace/generated_prompts") -> str:
        """Save generated prompt to file"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        filename = f"{prompt.project_name.lower().replace(' ', '_')}_{prompt.prompt_id}.md"
        file_path = output_path / filename
        
        # Create markdown format
        content = f"""# {prompt.project_name}
**Generated by Hephaestus on {prompt.generated_at.strftime('%Y-%m-%d %H:%M:%S')}**
**Prompt ID:** {prompt.prompt_id}
**Complexity:** {prompt.estimated_complexity}
**Security Level:** {prompt.security_level}

---

{prompt.prompt_content}

---

## Technical Stack
{chr(10).join(f'- {tech}' for tech in prompt.technical_stack)}

## Deployment Instructions
{prompt.deployment_instructions}

## Testing Requirements
{prompt.testing_requirements}

---
*Generated by Hephaestus - Prometheus AI Ecosystem*
"""
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return str(file_path)


def main():
    """Main entry point for Hephaestus"""
    print("🔨 Starting Hephaestus - Project to Cursor Prompt Converter")
    
    # Initialize Hephaestus
    hephaestus = HephaestusCore()
    
    # Example usage with the Prometheus project itself
    prometheus_description = """
    Prometheus is a monitoring and architect AI system with full operational autonomy. Its primary objective is to act as the foundational AI that creates and continuously oversees all subsequent modules.

    Core Functions:
    1. Create "Hephaestus," a system that converts project descriptions into detailed Cursor prompts
    2. Continuously monitor all systems for security vulnerabilities, data breaches, and performance issues
    3. Encrypt all data, communications, and APKs end-to-end
    4. Alert "Hestia" of any detected issues
    5. Maintain comprehensive logs and implement watchdog loops
    6. Include offline fail-safes and error recovery routines
    7. Autonomously update and refine all modules
    8. Operate with minimal human intervention

    Technical Requirements:
    - Web interface or command line for oversight
    - File system for storing logs and monitoring data
    - Background task execution on Android and other devices
    - Basic alerting system for notifications
    - Scalable architecture for supervising additional modules
    """
    
    try:
        # Generate prompt for Prometheus itself (meta!)
        prompt = hephaestus.generate_cursor_prompt("Prometheus Monitoring System", prometheus_description)
        
        # Save to file
        file_path = hephaestus.save_prompt_to_file(prompt)
        print(f"📄 Prompt saved to: {file_path}")
        
        # Display statistics
        stats = hephaestus.get_generation_stats()
        print(f"📈 Generation Stats: {stats}")
        
        print("🎯 Hephaestus ready for autonomous operation")
        
    except Exception as e:
        print(f"❌ Error in Hephaestus: {e}")


if __name__ == "__main__":
    main()