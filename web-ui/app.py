#!/usr/bin/env python3
import os
import tempfile
import subprocess
import shutil
import json
import uuid
import time
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from pathlib import Path

app = Flask(__name__)
GPTE_CMD = os.environ.get("GPTE_CMD", "gpte")
OUTPUT_ROOT = os.path.abspath(os.path.join(os.getcwd(), "web_outputs"))
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# Store for generated projects and sessions
PROJECTS = {}
SESSIONS = {}

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
    """Generate website using AI with DeepSeek/Qwen models"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        prompt = data.get('prompt', '')
        current_files = data.get('currentFiles', {})
        project_type = data.get('projectType', 'business')
        
        if not prompt.strip():
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Create session ID for tracking
        session_id = str(uuid.uuid4())[:8]
        
        # Create temporary directory for this generation
        project_dir = os.path.join(OUTPUT_ROOT, f'session_{session_id}')
        os.makedirs(project_dir, exist_ok=True)
        
        # Write current files to temp directory
        for filename, content in current_files.items():
            file_path = os.path.join(project_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create enhanced prompt for web development
        enhanced_prompt = create_web_prompt(prompt, project_type, current_files)
        
        # Write prompt file
        with open(os.path.join(project_dir, 'prompt'), 'w', encoding='utf-8') as f:
            f.write(enhanced_prompt)
        
        # Set environment variables for DeepSeek/Qwen models
        env = os.environ.copy()
        env['OPENROUTER_KEY'] = os.environ.get('OPENROUTER_KEY', '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')
        env['MODEL_NAME'] = 'deepseek/deepseek-r1-0528:free'
        env['LOCAL_MODEL'] = 'true'
        
        # Run the GPT Engineer CLI with improved mode if files exist
        mode_flag = '--improve' if current_files else ''
        
        try:
            completed = subprocess.run(
                [GPTE_CMD, project_dir, mode_flag, '--model', 'deepseek/deepseek-r1-0528:free', '--no_execution', '--lite'],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env
            )
        except subprocess.TimeoutExpired:
            shutil.rmtree(project_dir, ignore_errors=True)
            return jsonify({'error': 'Generation timed out. Please try with a simpler prompt.'}), 500
        except Exception as e:
            shutil.rmtree(project_dir, ignore_errors=True)
            return jsonify({'error': f'Generation failed: {str(e)}'}), 500
        
        # Read generated files
        generated_files = {}
        try:
            for file_path in Path(project_dir).rglob('*'):
                if file_path.is_file() and file_path.name != 'prompt':
                    relative_path = file_path.relative_to(project_dir)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            generated_files[str(relative_path)] = f.read()
                    except UnicodeDecodeError:
                        # Skip binary files
                        continue
        except Exception as e:
            print(f"Error reading generated files: {e}")
        
        # Store session info
        SESSIONS[session_id] = {
            'prompt': prompt,
            'files': generated_files,
            'project_type': project_type,
            'path': project_dir,
            'returncode': completed.returncode,
            'stdout': completed.stdout,
            'stderr': completed.stderr,
            'timestamp': time.time()
        }
        
        # Generate reasoning based on the prompt and changes
        reasoning = generate_reasoning(prompt, current_files, generated_files)
        
        # Estimate token usage (rough calculation)
        token_usage = estimate_token_usage(prompt, generated_files)
        
        result = {
            'sessionId': session_id,
            'files': generated_files,
            'reasoning': reasoning,
            'model_used': 'deepseek/deepseek-r1-0528:free',
            'token_usage': token_usage,
            'success': completed.returncode == 0,
            'stdout': completed.stdout,
            'stderr': completed.stderr
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-project', methods=['POST'])
def save_project():
    """Save project to persistent storage"""
    try:
        data = request.get_json()
        project = data.get('project', {})
        files = data.get('files', {})
        
        project_id = project.get('id', str(uuid.uuid4()))
        project_dir = os.path.join(OUTPUT_ROOT, f'project_{project_id}')
        os.makedirs(project_dir, exist_ok=True)
        
        # Save project metadata
        with open(os.path.join(project_dir, 'project.json'), 'w') as f:
            json.dump(project, f, indent=2)
        
        # Save files
        for filename, content in files.items():
            file_path = os.path.join(project_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        PROJECTS[project_id] = {
            'project': project,
            'files': files,
            'path': project_dir,
            'saved_at': time.time()
        }
        
        return jsonify({'success': True, 'project_id': project_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects')
def list_projects():
    """List all saved projects"""
    return jsonify({
        'projects': [
            {
                'id': pid,
                'name': info['project'].get('name', 'Untitled'),
                'description': info['project'].get('description', ''),
                'type': info['project'].get('type', 'business'),
                'saved_at': info['saved_at']
            }
            for pid, info in PROJECTS.items()
        ]
    })

@app.route('/preview/<session_id>')
def preview_session(session_id):
    """Preview a generated session"""
    if session_id not in SESSIONS:
        return "Session not found", 404
    
    files = SESSIONS[session_id]['files']
    
    # Look for index.html
    if 'index.html' in files:
        html_content = files['index.html']
        
        # Inject CSS and JS inline
        if 'style.css' in files:
            html_content = html_content.replace(
                '<link rel="stylesheet" href="style.css">',
                f'<style>{files["style.css"]}</style>'
            )
        
        if 'script.js' in files:
            html_content = html_content.replace(
                '<script src="script.js"></script>',
                f'<script>{files["script.js"]}</script>'
            )
        
        return html_content
    
    return "No index.html found", 404

def create_web_prompt(user_prompt, project_type, current_files):
    """Create an enhanced prompt for web development"""
    
    base_prompt = f"""
Create a modern, professional {project_type} website based on this request:

{user_prompt}

REQUIREMENTS:
- Use modern HTML5, CSS3, and JavaScript
- Make it fully responsive for all devices
- Include proper semantic HTML structure
- Use CSS Grid and Flexbox for layouts
- Add smooth animations and hover effects
- Ensure accessibility with proper ARIA labels
- Include meta tags for SEO
- Create clean, maintainable code
- Use modern web fonts and design principles
- Make it production-ready

CURRENT FILES:
"""
    
    if current_files:
        base_prompt += "\nExisting files to modify or reference:\n"
        for filename, content in current_files.items():
            base_prompt += f"\n{filename}:\n```\n{content[:500]}{'...' if len(content) > 500 else ''}\n```\n"
    else:
        base_prompt += "\nNo existing files - create a complete website from scratch.\n"
    
    base_prompt += """
INSTRUCTIONS:
- If modifying existing files, use the improve/diff format
- If creating new files, provide complete file content
- Ensure all files work together seamlessly
- Include index.html, style.css, and script.js at minimum
- Add additional pages/files as needed
- Use placeholder content that matches the theme
- Make the design modern and visually appealing

Please create all necessary files for a complete, functional website.
"""
    
    return base_prompt

def generate_reasoning(prompt, current_files, generated_files):
    """Generate reasoning explanation for the AI's actions"""
    
    reasoning = f"🎯 **Analysis**: {prompt}\n\n"
    
    if current_files:
        reasoning += f"📁 **Existing Files**: Found {len(current_files)} files to work with\n"
        reasoning += f"🔄 **Action**: Improving and modifying existing website\n\n"
    else:
        reasoning += f"🆕 **Action**: Creating new website from scratch\n\n"
    
    reasoning += f"📝 **Generated**: {len(generated_files)} files\n"
    
    for filename in generated_files.keys():
        file_type = filename.split('.')[-1].upper() if '.' in filename else 'FILE'
        reasoning += f"   • {filename} ({file_type})\n"
    
    reasoning += f"\n✅ **Result**: Modern, responsive website ready for preview"
    
    return reasoning

def estimate_token_usage(prompt, files):
    """Rough estimation of token usage"""
    total_chars = len(prompt)
    for content in files.values():
        total_chars += len(content)
    
    # Rough estimation: ~4 characters per token
    return min(total_chars // 4, 1800)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Starting Multiverse AI Web Builder on port {port}")
    print("🤖 Using DeepSeek and Qwen models via OpenRouter")
    print("🌐 Open your browser to see the web builder interface")
    
    # For Bolt preview, bind to 0.0.0.0
    app.run(host='0.0.0.0', port=port, debug=True)