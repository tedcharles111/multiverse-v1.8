#!/usr/bin/env python3
import os
import tempfile
import subprocess
import shutil
import json
import uuid
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from pathlib import Path

app = Flask(__name__)
GPTE_CMD = os.environ.get("GPTE_CMD", "gpte")
OUTPUT_ROOT = os.path.abspath(os.path.join(os.getcwd(), "web_outputs"))
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# Store for generated projects
PROJECTS = {}

@app.route('/')
def index():
    """Serve the main Multiverse AI interface"""
    try:
        with open('../index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Multiverse AI Web Builder</h1>
        <p>Frontend files not found. Please ensure index.html is in the parent directory.</p>
        <p>Use the <code>/api/generate</code> endpoint (POST) with JSON {"websiteType": "...", "colorTheme": "...", "description": "..."}</p>
        """

@app.route('/script.js')
def script():
    """Serve the JavaScript file"""
    try:
        with open('../script.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "console.log('Script not found');", 200, {'Content-Type': 'application/javascript'}

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate a website using the GPT Engineer CLI with DeepSeek models"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        website_type = data.get('websiteType', 'business')
        color_theme = data.get('colorTheme', 'professional')
        description = data.get('description', '')
        
        if not description.strip():
            return jsonify({'error': 'Description is required'}), 400
        
        # Create a unique project ID
        project_id = str(uuid.uuid4())[:8]
        
        # Create temporary directory for this project
        project_dir = os.path.join(OUTPUT_ROOT, f'project_{project_id}')
        os.makedirs(project_dir, exist_ok=True)
        
        # Create enhanced prompt for web development
        enhanced_prompt = f"""
Create a complete {website_type} website with a {color_theme} design theme.

Requirements:
{description}

Technical specifications:
- Use modern HTML5, CSS3, and JavaScript
- Make it fully responsive for all devices
- Include proper semantic HTML structure
- Use CSS Grid and Flexbox for layouts
- Add smooth animations and hover effects
- Ensure accessibility with proper ARIA labels
- Include meta tags for SEO
- Use a {color_theme} color scheme
- Create multiple pages if needed (index.html, about.html, contact.html, etc.)
- Include a navigation menu
- Add placeholder content that matches the theme
- Use modern web fonts
- Include favicon and proper meta tags
- Make it production-ready

Please create all necessary files including HTML, CSS, JavaScript, and any assets needed.
"""
        
        # Write prompt file
        with open(os.path.join(project_dir, 'prompt'), 'w', encoding='utf-8') as f:
            f.write(enhanced_prompt)
        
        # Set environment variables for DeepSeek models
        env = os.environ.copy()
        env['OPENROUTER_KEY'] = os.environ.get('OPENROUTER_KEY', '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')
        env['MODEL_NAME'] = 'deepseek/deepseek-r1-0528:free'
        
        # Run the GPT Engineer CLI
        try:
            completed = subprocess.run(
                [GPTE_CMD, project_dir, '--no_execution', '--model', 'deepseek/deepseek-r1-0528:free'],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env
            )
        except subprocess.TimeoutExpired:
            shutil.rmtree(project_dir, ignore_errors=True)
            return jsonify({'error': 'Generation timed out. Please try with a simpler description.'}), 500
        except Exception as e:
            shutil.rmtree(project_dir, ignore_errors=True)
            return jsonify({'error': f'Generation failed: {str(e)}'}), 500
        
        # Store project info
        PROJECTS[project_id] = {
            'type': website_type,
            'theme': color_theme,
            'description': description,
            'path': project_dir,
            'returncode': completed.returncode,
            'stdout': completed.stdout,
            'stderr': completed.stderr
        }
        
        result = {
            'projectId': project_id,
            'returncode': completed.returncode,
            'stdout': completed.stdout,
            'stderr': completed.stderr,
            'success': completed.returncode == 0
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<project_id>')
def preview_project(project_id):
    """Preview a generated project"""
    if project_id not in PROJECTS:
        return "Project not found", 404
    
    project_path = PROJECTS[project_id]['path']
    
    # Look for index.html or main HTML file
    html_files = list(Path(project_path).glob('*.html'))
    if not html_files:
        return f"No HTML files found in project {project_id}", 404
    
    # Serve the main HTML file
    main_html = html_files[0]
    try:
        with open(main_html, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading HTML file: {str(e)}", 500

@app.route('/download/<project_id>')
def download_project(project_id):
    """Download project files as a zip"""
    if project_id not in PROJECTS:
        return "Project not found", 404
    
    project_path = PROJECTS[project_id]['path']
    
    # Create a zip file
    zip_path = f"{project_path}.zip"
    shutil.make_archive(project_path, 'zip', project_path)
    
    return send_from_directory(
        os.path.dirname(zip_path),
        os.path.basename(zip_path),
        as_attachment=True,
        download_name=f"multiverse_project_{project_id}.zip"
    )

@app.route('/api/projects')
def list_projects():
    """List all generated projects"""
    return jsonify({
        'projects': [
            {
                'id': pid,
                'type': info['type'],
                'theme': info['theme'],
                'description': info['description'][:100] + ('...' if len(info['description']) > 100 else '')
            }
            for pid, info in PROJECTS.items()
        ]
    })

@app.route('/outputs/<path:filename>')
def outputs(filename):
    """Serve output files"""
    return send_from_directory(OUTPUT_ROOT, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"Starting Multiverse AI Web Builder on port {port}")
    print("Using DeepSeek models via OpenRouter")
    # For Bolt preview, bind to 0.0.0.0
    app.run(host='0.0.0.0', port=port, debug=True)