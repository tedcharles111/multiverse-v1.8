// Multiverse AI Web Builder - Main JavaScript
class MultiverseAI {
    constructor() {
        this.currentProject = null;
        this.currentFile = null;
        this.files = new Map();
        this.editors = new Map();
        this.activeEditor = null;
        this.isGenerating = false;
        this.tokenUsage = 0;
        this.maxTokens = 1800;
        this.currentModel = 'deepseek-r1';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCodeMirror();
        this.createDefaultProject();
        this.updateUI();
    }

    setupEventListeners() {
        // Header controls
        document.getElementById('save-project').addEventListener('click', () => this.saveProject());
        document.getElementById('new-project').addEventListener('click', () => this.showNewProjectModal());
        document.getElementById('preview-new-tab').addEventListener('click', () => this.openPreviewInNewTab());

        // View toggle
        document.getElementById('code-toggle').addEventListener('click', () => this.switchToCodeView());
        document.getElementById('preview-toggle').addEventListener('click', () => this.switchToPreviewView());

        // AI Generation
        document.getElementById('generate-btn').addEventListener('click', () => this.generateWithAI());
        document.getElementById('prompt-input').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.generateWithAI();
            }
        });

        // File management
        document.getElementById('add-file-btn').addEventListener('click', () => this.showNewFileModal());

        // Modals
        document.getElementById('close-new-file-modal').addEventListener('click', () => this.hideModal('new-file-modal'));
        document.getElementById('close-new-project-modal').addEventListener('click', () => this.hideModal('new-project-modal'));
        document.getElementById('create-file-btn').addEventListener('click', () => this.createNewFile());
        document.getElementById('create-project-btn').addEventListener('click', () => this.createNewProject());

        // Format code
        document.getElementById('format-code').addEventListener('click', () => this.formatCurrentFile());

        // Click outside modal to close
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal(e.target.id);
            }
        });
    }

    initializeCodeMirror() {
        const textarea = document.getElementById('code-textarea');
        this.mainEditor = CodeMirror.fromTextArea(textarea, {
            theme: 'monokai',
            lineNumbers: true,
            mode: 'htmlmixed',
            autoCloseBrackets: true,
            matchBrackets: true,
            indentUnit: 2,
            tabSize: 2,
            lineWrapping: true,
            extraKeys: {
                'Ctrl-S': () => this.saveCurrentFile(),
                'Ctrl-/': 'toggleComment',
                'Ctrl-D': 'deleteLine',
                'Ctrl-Enter': () => this.generateWithAI()
            }
        });

        this.mainEditor.on('change', () => {
            if (this.currentFile) {
                this.files.set(this.currentFile, this.mainEditor.getValue());
                this.updatePreview();
                this.updateCursorPosition();
            }
        });

        this.mainEditor.on('cursorActivity', () => {
            this.updateCursorPosition();
        });
    }

    createDefaultProject() {
        this.currentProject = {
            id: 'default-project',
            name: 'My Website',
            description: 'AI-generated website',
            type: 'business',
            created: new Date().toISOString()
        };

        // Create default files
        this.files.set('index.html', this.getDefaultHTML());
        this.files.set('style.css', this.getDefaultCSS());
        this.files.set('script.js', this.getDefaultJS());

        this.currentFile = 'index.html';
    }

    getDefaultHTML() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to My Website</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <nav>
            <div class="logo">My Website</div>
            <ul class="nav-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#services">Services</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section id="home" class="hero">
            <div class="hero-content">
                <h1>Welcome to the Future</h1>
                <p>Built with Multiverse AI - where ideas become reality</p>
                <button class="cta-button">Get Started</button>
            </div>
        </section>

        <section id="about" class="section">
            <div class="container">
                <h2>About Us</h2>
                <p>We create amazing experiences with the power of AI.</p>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 My Website. Built with Multiverse AI.</p>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>`;
    }

    getDefaultCSS() {
        return `/* Modern CSS Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
}

/* Header */
header {
    background: #fff;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 1000;
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: #6e44ff;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-links a {
    text-decoration: none;
    color: #333;
    font-weight: 500;
    transition: color 0.3s ease;
}

.nav-links a:hover {
    color: #6e44ff;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #6e44ff, #ff44a7);
    color: white;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding-top: 80px;
}

.hero-content h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    animation: fadeInUp 1s ease;
}

.hero-content p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    animation: fadeInUp 1s ease 0.2s both;
}

.cta-button {
    background: white;
    color: #6e44ff;
    padding: 1rem 2rem;
    border: none;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.3s ease;
    animation: fadeInUp 1s ease 0.4s both;
}

.cta-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

/* Sections */
.section {
    padding: 4rem 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

.section h2 {
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    color: #333;
}

/* Footer */
footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 2rem 0;
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Responsive */
@media (max-width: 768px) {
    .nav-links {
        display: none;
    }
    
    .hero-content h1 {
        font-size: 2rem;
    }
    
    nav {
        padding: 1rem;
    }
}`;
    }

    getDefaultJS() {
        return `// Website functionality
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // CTA button interaction
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
        ctaButton.addEventListener('click', function() {
            alert('Welcome to Multiverse AI! This website was generated by AI.');
        });
    }

    // Add some interactive animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe sections for animation
    document.querySelectorAll('.section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
});`;
    }

    updateUI() {
        this.updateProjectInfo();
        this.updateFileList();
        this.updateEditorTabs();
        this.updateTokenUsage();
        
        if (this.currentFile) {
            this.openFile(this.currentFile);
        }
    }

    updateProjectInfo() {
        document.getElementById('project-name').textContent = this.currentProject.name;
        document.getElementById('project-description').textContent = this.currentProject.description;
    }

    updateFileList() {
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';

        for (const [filename] of this.files) {
            const li = document.createElement('li');
            li.className = `file-item ${filename === this.currentFile ? 'active' : ''}`;
            
            const icon = this.getFileIcon(filename);
            
            li.innerHTML = `
                <div class="file-name">
                    <i class="${icon}"></i>
                    <span>${filename}</span>
                </div>
                <div class="file-actions">
                    <button class="file-action" onclick="multiverseAI.deleteFile('${filename}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            li.addEventListener('click', (e) => {
                if (!e.target.closest('.file-actions')) {
                    this.openFile(filename);
                }
            });
            
            fileList.appendChild(li);
        }
    }

    updateEditorTabs() {
        const tabsContainer = document.getElementById('editor-tabs');
        tabsContainer.innerHTML = '';

        for (const [filename] of this.files) {
            const tab = document.createElement('button');
            tab.className = `editor-tab ${filename === this.currentFile ? 'active' : ''}`;
            tab.innerHTML = `
                <i class="${this.getFileIcon(filename)}"></i>
                <span>${filename}</span>
                <span class="tab-close" onclick="multiverseAI.closeFile('${filename}')">&times;</span>
            `;
            
            tab.addEventListener('click', (e) => {
                if (!e.target.classList.contains('tab-close')) {
                    this.openFile(filename);
                }
            });
            
            tabsContainer.appendChild(tab);
        }
    }

    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'html': 'fab fa-html5',
            'css': 'fab fa-css3-alt',
            'js': 'fab fa-js-square',
            'json': 'fas fa-code',
            'md': 'fab fa-markdown',
            'txt': 'fas fa-file-alt'
        };
        return icons[ext] || 'fas fa-file';
    }

    openFile(filename) {
        if (!this.files.has(filename)) return;

        this.currentFile = filename;
        const content = this.files.get(filename);
        
        // Update editor mode based on file type
        const mode = this.getEditorMode(filename);
        this.mainEditor.setOption('mode', mode);
        this.mainEditor.setValue(content);
        
        // Update UI
        this.updateFileList();
        this.updateEditorTabs();
        document.getElementById('current-file').textContent = filename;
        
        // Update preview if in preview mode
        if (document.getElementById('preview-toggle').classList.contains('active')) {
            this.updatePreview();
        }
    }

    getEditorMode(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const modes = {
            'html': 'htmlmixed',
            'css': 'css',
            'js': 'javascript',
            'json': 'application/json',
            'md': 'markdown'
        };
        return modes[ext] || 'text/plain';
    }

    closeFile(filename) {
        if (this.files.size <= 1) {
            this.showNotification('Cannot close the last file', 'warning');
            return;
        }

        this.files.delete(filename);
        
        if (this.currentFile === filename) {
            // Switch to another file
            const remainingFiles = Array.from(this.files.keys());
            this.openFile(remainingFiles[0]);
        }
        
        this.updateUI();
    }

    deleteFile(filename) {
        if (this.files.size <= 1) {
            this.showNotification('Cannot delete the last file', 'warning');
            return;
        }

        if (confirm(`Are you sure you want to delete ${filename}?`)) {
            this.closeFile(filename);
            this.showNotification(`Deleted ${filename}`, 'success');
        }
    }

    switchToCodeView() {
        document.getElementById('code-toggle').classList.add('active');
        document.getElementById('preview-toggle').classList.remove('active');
        document.getElementById('code-editor').style.display = 'flex';
        document.getElementById('preview-container').classList.remove('active');
        this.mainEditor.refresh();
    }

    switchToPreviewView() {
        document.getElementById('preview-toggle').classList.add('active');
        document.getElementById('code-toggle').classList.remove('active');
        document.getElementById('code-editor').style.display = 'none';
        document.getElementById('preview-container').classList.add('active');
        this.updatePreview();
    }

    updatePreview() {
        const iframe = document.getElementById('preview-iframe');
        const htmlContent = this.files.get('index.html') || '';
        const cssContent = this.files.get('style.css') || '';
        const jsContent = this.files.get('script.js') || '';

        const fullHTML = htmlContent.replace(
            '<link rel="stylesheet" href="style.css">',
            `<style>${cssContent}</style>`
        ).replace(
            '<script src="script.js"></script>',
            `<script>${jsContent}</script>`
        );

        const blob = new Blob([fullHTML], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        iframe.src = url;

        // Clean up previous URL
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    openPreviewInNewTab() {
        const htmlContent = this.files.get('index.html') || '';
        const cssContent = this.files.get('style.css') || '';
        const jsContent = this.files.get('script.js') || '';

        const fullHTML = htmlContent.replace(
            '<link rel="stylesheet" href="style.css">',
            `<style>${cssContent}</style>`
        ).replace(
            '<script src="script.js"></script>',
            `<script>${jsContent}</script>`
        );

        const newWindow = window.open();
        newWindow.document.write(fullHTML);
        newWindow.document.close();
    }

    async generateWithAI() {
        const prompt = document.getElementById('prompt-input').value.trim();
        if (!prompt) {
            this.showNotification('Please enter a prompt', 'warning');
            return;
        }

        if (this.isGenerating) {
            this.showNotification('Generation already in progress', 'warning');
            return;
        }

        this.isGenerating = true;
        this.updateGenerateButton(true);
        
        try {
            // Show reasoning
            this.updateReasoning('🤖 Analyzing your request...');
            
            // Call the backend API
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    currentFiles: Object.fromEntries(this.files),
                    projectType: this.currentProject.type
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.handleGenerationSuccess(result);
            } else {
                throw new Error(result.error || 'Generation failed');
            }
        } catch (error) {
            this.handleGenerationError(error);
        } finally {
            this.isGenerating = false;
            this.updateGenerateButton(false);
        }
    }

    handleGenerationSuccess(result) {
        // Update reasoning
        this.updateReasoning(result.reasoning || '✅ Successfully generated your website!');
        
        // Update files
        if (result.files) {
            for (const [filename, content] of Object.entries(result.files)) {
                this.files.set(filename, content);
            }
        }

        // Update model indicator
        this.updateModelIndicator(result.model_used);
        
        // Update token usage
        this.tokenUsage = result.token_usage || 0;
        this.updateTokenUsage();

        // Refresh UI
        this.updateUI();
        
        // Clear prompt
        document.getElementById('prompt-input').value = '';
        
        this.showNotification('Website generated successfully!', 'success');
    }

    handleGenerationError(error) {
        this.updateReasoning(`❌ Error: ${error.message}`);
        this.showNotification(`Generation failed: ${error.message}`, 'error');
    }

    updateReasoning(content) {
        document.getElementById('reasoning-content').innerHTML = content;
    }

    updateGenerateButton(loading) {
        const btn = document.getElementById('generate-btn');
        if (loading) {
            btn.innerHTML = '<div class="loading"><div class="spinner"></div>Generating...</div>';
            btn.disabled = true;
        } else {
            btn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Generate with AI';
            btn.disabled = false;
        }
    }

    updateModelIndicator(modelUsed) {
        const indicator = document.getElementById('model-indicator');
        const modelName = document.getElementById('model-name');
        
        if (modelUsed && modelUsed.includes('fallback')) {
            indicator.classList.add('fallback');
            modelName.textContent = 'Qwen Fallback';
        } else {
            indicator.classList.remove('fallback');
            modelName.textContent = 'DeepSeek R1';
        }
    }

    updateTokenUsage() {
        document.getElementById('token-usage').textContent = `Tokens: ${this.tokenUsage}/${this.maxTokens}`;
    }

    updateCursorPosition() {
        const cursor = this.mainEditor.getCursor();
        document.getElementById('cursor-position').textContent = `Ln ${cursor.line + 1}, Col ${cursor.ch + 1}`;
    }

    showNewFileModal() {
        this.showModal('new-file-modal');
        document.getElementById('new-file-name').focus();
    }

    showNewProjectModal() {
        this.showModal('new-project-modal');
        document.getElementById('new-project-name').focus();
    }

    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    }

    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
        // Clear form inputs
        const modal = document.getElementById(modalId);
        modal.querySelectorAll('input, textarea, select').forEach(input => {
            input.value = '';
        });
    }

    createNewFile() {
        const name = document.getElementById('new-file-name').value.trim();
        const type = document.getElementById('new-file-type').value;

        if (!name) {
            this.showNotification('Please enter a file name', 'warning');
            return;
        }

        // Add extension if not provided
        let filename = name;
        if (!filename.includes('.')) {
            filename += `.${type}`;
        }

        if (this.files.has(filename)) {
            this.showNotification('File already exists', 'warning');
            return;
        }

        // Create file with template content
        const template = this.getFileTemplate(filename);
        this.files.set(filename, template);
        
        this.hideModal('new-file-modal');
        this.openFile(filename);
        this.updateUI();
        
        this.showNotification(`Created ${filename}`, 'success');
    }

    getFileTemplate(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const templates = {
            'html': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>New Page</title>\n</head>\n<body>\n    <h1>New Page</h1>\n</body>\n</html>',
            'css': '/* New stylesheet */\nbody {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}',
            'js': '// New JavaScript file\ndocument.addEventListener(\'DOMContentLoaded\', function() {\n    console.log(\'Script loaded\');\n});',
            'json': '{\n    "name": "config",\n    "version": "1.0.0"\n}'
        };
        return templates[ext] || '';
    }

    createNewProject() {
        const name = document.getElementById('new-project-name').value.trim();
        const type = document.getElementById('new-project-type').value;
        const description = document.getElementById('new-project-description').value.trim();

        if (!name) {
            this.showNotification('Please enter a project name', 'warning');
            return;
        }

        this.currentProject = {
            id: Date.now().toString(),
            name: name,
            description: description || 'New project',
            type: type,
            created: new Date().toISOString()
        };

        // Reset files
        this.files.clear();
        this.createDefaultProject();
        
        this.hideModal('new-project-modal');
        this.updateUI();
        
        this.showNotification(`Created project: ${name}`, 'success');
    }

    async saveProject() {
        try {
            const projectData = {
                project: this.currentProject,
                files: Object.fromEntries(this.files)
            };

            const response = await fetch('/api/save-project', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projectData)
            });

            if (response.ok) {
                this.showNotification('Project saved successfully!', 'success');
            } else {
                throw new Error('Failed to save project');
            }
        } catch (error) {
            this.showNotification(`Save failed: ${error.message}`, 'error');
        }
    }

    saveCurrentFile() {
        if (this.currentFile && this.mainEditor) {
            this.files.set(this.currentFile, this.mainEditor.getValue());
            this.showNotification(`Saved ${this.currentFile}`, 'success');
        }
    }

    formatCurrentFile() {
        if (!this.currentFile || !this.mainEditor) return;

        const content = this.mainEditor.getValue();
        const ext = this.currentFile.split('.').pop().toLowerCase();

        // Simple formatting for different file types
        let formatted = content;
        
        if (ext === 'html') {
            // Basic HTML formatting
            formatted = this.formatHTML(content);
        } else if (ext === 'css') {
            // Basic CSS formatting
            formatted = this.formatCSS(content);
        } else if (ext === 'js') {
            // Basic JS formatting
            formatted = this.formatJS(content);
        }

        this.mainEditor.setValue(formatted);
        this.showNotification('Code formatted', 'success');
    }

    formatHTML(html) {
        // Simple HTML formatting
        return html
            .replace(/></g, '>\n<')
            .replace(/^\s+|\s+$/gm, '')
            .split('\n')
            .map((line, index, array) => {
                const trimmed = line.trim();
                if (!trimmed) return '';
                
                const indent = this.getHTMLIndent(trimmed, index, array);
                return '    '.repeat(indent) + trimmed;
            })
            .filter(line => line.trim())
            .join('\n');
    }

    getHTMLIndent(line, index, array) {
        let indent = 0;
        for (let i = 0; i < index; i++) {
            const prevLine = array[i].trim();
            if (prevLine.match(/<[^\/][^>]*[^\/]>$/)) {
                indent++;
            }
            if (prevLine.match(/<\/[^>]+>$/)) {
                indent--;
            }
        }
        if (line.match(/^<\/[^>]+>$/)) {
            indent--;
        }
        return Math.max(0, indent);
    }

    formatCSS(css) {
        return css
            .replace(/\{/g, ' {\n')
            .replace(/\}/g, '\n}\n')
            .replace(/;/g, ';\n')
            .split('\n')
            .map(line => {
                const trimmed = line.trim();
                if (!trimmed) return '';
                if (trimmed.includes('{') || trimmed.includes('}')) {
                    return trimmed;
                }
                return '    ' + trimmed;
            })
            .filter(line => line.trim())
            .join('\n');
    }

    formatJS(js) {
        // Basic JS formatting
        return js
            .replace(/\{/g, ' {\n')
            .replace(/\}/g, '\n}\n')
            .replace(/;/g, ';\n')
            .split('\n')
            .map(line => line.trim())
            .filter(line => line)
            .join('\n');
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type} show`;
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
}

// Initialize the application
const multiverseAI = new MultiverseAI();

// Global functions for event handlers
window.multiverseAI = multiverseAI;