// FAQ toggle functionality
document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', () => {
        const answer = question.nextElementSibling;
        answer.style.display = answer.style.display === 'block' ? 'none' : 'block';
        const icon = question.querySelector('i');
        icon.classList.toggle('fa-chevron-down');
        icon.classList.toggle('fa-chevron-up');
    });
});

// Generate website button functionality
document.querySelector('.generate-btn').addEventListener('click', async function() {
    const websiteType = document.getElementById('website-type').value;
    const colorTheme = document.getElementById('color-theme').value;
    const description = document.getElementById('website-description').value;
    
    if (!description.trim()) {
        alert('Please describe your website before generating.');
        return;
    }
    
    const preview = document.querySelector('.builder-preview');
    
    // Show loading state
    preview.innerHTML = `
        <div style="text-align: center; padding: 50px 0;">
            <i class="fas fa-spinner fa-spin" style="font-size: 3rem; color: #6e44ff;"></i>
            <p style="margin-top: 20px;">Generating your website with DeepSeek AI...</p>
            <p style="color: #6e6e7a; font-size: 14px;">This may take a few moments</p>
        </div>
    `;
    
    try {
        // Call the backend API
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                websiteType,
                colorTheme,
                description
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Show success preview
            preview.innerHTML = `
                <h3>Website Generated Successfully!</h3>
                <p>Your ${websiteType} website with ${colorTheme} theme has been created.</p>
                <div style="margin-top: 20px; padding: 15px; background: #f5f5f7; border-radius: 8px; color: #333;">
                    <h4>Preview</h4>
                    <p><strong>Type:</strong> ${websiteType}</p>
                    <p><strong>Theme:</strong> ${colorTheme}</p>
                    <p><strong>Description:</strong> "${description.substring(0, 100)}${description.length > 100 ? '...' : ''}"</p>
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <div style="width: 30%; height: 80px; background: #6e44ff; border-radius: 4px;"></div>
                        <div style="width: 70%; height: 80px; background: #ff44a7; border-radius: 4px;"></div>
                    </div>
                    <div style="height: 120px; background: linear-gradient(135deg, #6e44ff, #ff44a7); margin-top: 15px; display: flex; align-items: center; justify-content: center; color: white; border-radius: 4px;">
                        Generated Content Area
                    </div>
                </div>
                <div style="margin-top: 20px;">
                    <button class="btn btn-primary" style="width: 100%; margin-bottom: 10px;" onclick="openGeneratedSite('${result.projectId}')">
                        <i class="fas fa-external-link-alt"></i> Open Generated Website
                    </button>
                    <button class="btn btn-outline" style="width: 100%;" onclick="downloadProject('${result.projectId}')">
                        <i class="fas fa-download"></i> Download Project Files
                    </button>
                </div>
            `;
        } else {
            throw new Error(result.error || 'Generation failed');
        }
    } catch (error) {
        // Show error state
        preview.innerHTML = `
            <div style="text-align: center; padding: 50px 0;">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #ff5e7d;"></i>
                <p style="margin-top: 20px; color: #ff5e7d;">Generation Failed</p>
                <p style="color: #6e6e7a; font-size: 14px; margin-top: 10px;">${error.message}</p>
                <button class="btn btn-outline" style="margin-top: 20px;" onclick="location.reload()">
                    Try Again
                </button>
            </div>
        `;
    }
});

// Helper functions for generated website actions
function openGeneratedSite(projectId) {
    window.open(`/preview/${projectId}`, '_blank');
}

function downloadProject(projectId) {
    window.open(`/download/${projectId}`, '_blank');
}

// Smooth scrolling for navigation links
document.querySelectorAll('nav a[href^="#"]').forEach(anchor => {
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

// Hero buttons functionality
document.querySelectorAll('.hero-buttons .btn').forEach(btn => {
    btn.addEventListener('click', function() {
        if (this.textContent.includes('Start Building')) {
            document.querySelector('.ai-builder').scrollIntoView({
                behavior: 'smooth'
            });
        } else if (this.textContent.includes('Watch Demo')) {
            // Demo functionality
            alert('Demo video would play here');
        }
    });
});

// CTA button functionality
document.querySelector('.cta .btn').addEventListener('click', function() {
    document.querySelector('.ai-builder').scrollIntoView({
        behavior: 'smooth'
    });
});

// Add some interactive animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate feature cards on scroll
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

    // Observe all cards
    document.querySelectorAll('.feature-card, .step-card, .template-card, .pricing-card, .testimonial-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});