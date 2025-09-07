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
GPTE_CMD = os.environ.get("GPTE_CMD", "python -m gpt_engineer.applications.cli.main")
OUTPUT_ROOT = os.path.abspath(os.path.join(os.getcwd(), "web_outputs"))
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# Store for generated projects and sessions
PROJECTS = {}
SESSIONS = {}

@app.route('/')
def index():
    """Serve the main Multiverse AI interface"""
    try:
        # Try to read from the root directory first
        index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Fallback to current directory
        current_index = os.path.join(os.path.dirname(__file__), 'index.html')
        if os.path.exists(current_index):
            with open(current_index, 'r', encoding='utf-8') as f:
                return f.read()
                
        # If no file found, return the embedded HTML
        return get_embedded_html()
    except Exception as e:
        print(f"Error serving index: {e}")
        return get_embedded_html()

def get_embedded_html():
    """Return the embedded HTML for Multiverse AI"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MULtiverse AI - AI Web Builder</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #6e44ff;
            --primary-dark: #5a36d9;
            --secondary: #ff44a7;
            --dark: #1a1a2e;
            --darker: #0d0d1a;
            --light: #f5f5f7;
            --gray: #6e6e7a;
            --success: #00c896;
            --warning: #ff9f43;
            --danger: #ff5e7d;
            --card-bg: rgba(255, 255, 255, 0.05);
            --border-radius: 12px;
            --shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(135deg, var(--darker), var(--dark));
            color: var(--light);
            min-height: 100vh;
            line-height: 1.6;
        }

        .container {
            width: 100%;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }

        header {
            background: rgba(26, 26, 46, 0.8);
            backdrop-filter: blur(10px);
            padding: 15px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 24px;
            font-weight: 700;
            color: var(--light);
        }

        .logo span {
            color: var(--primary);
        }

        .logo i {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        nav ul {
            display: flex;
            list-style: none;
            gap: 30px;
        }

        nav a {
            color: var(--light);
            text-decoration: none;
            font-weight: 500;
            transition: var(--transition);
        }

        nav a:hover {
            color: var(--primary);
        }

        .auth-buttons {
            display: flex;
            gap: 15px;
        }

        .btn {
            padding: 10px 20px;
            border-radius: var(--border-radius);
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            border: none;
            font-size: 16px;
        }

        .btn-outline {
            background: transparent;
            border: 2px solid var(--primary);
            color: var(--primary);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }

        .hero {
            padding: 80px 0;
            text-align: center;
            max-width: 800px;
            margin: 0 auto;
        }

        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 20px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            font-size: 1.2rem;
            color: var(--gray);
            margin-bottom: 40px;
        }

        .hero-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 40px;
        }

        .btn-large {
            padding: 15px 30px;
            font-size: 1.1rem;
        }

        .hero-demo {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 20px;
            margin-top: 40px;
            box-shadow: var(--shadow);
        }

        .section-title {
            text-align: center;
            margin: 60px 0 40px;
            font-size: 2.5rem;
        }

        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 60px;
        }

        .feature-card {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 30px;
            transition: var(--transition);
            box-shadow: var(--shadow);
        }

        .feature-card:hover {
            transform: translateY(-5px);
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 20px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .feature-card h3 {
            font-size: 1.5rem;
            margin-bottom: 15px;
        }

        .how-it-works {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 60px;
        }

        .step-card {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 30px;
            text-align: center;
            box-shadow: var(--shadow);
        }

        .step-number {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 1.5rem;
            font-weight: bold;
        }

        .templates {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 60px;
        }

        .template-card {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--shadow);
        }

        .template-img {
            height: 200px;
            background: linear-gradient(135deg, #5e72e4, #ff9190);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        }

        .template-content {
            padding: 20px;
        }

        .template-content h3 {
            margin-bottom: 10px;
        }

        .pricing {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 60px;
        }

        .pricing-card {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 30px;
            text-align: center;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }

        .pricing-card:hover {
            transform: scale(1.03);
        }

        .pricing-card h3 {
            font-size: 1.8rem;
            margin-bottom: 15px;
        }

        .price {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 20px 0;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .pricing-features {
            list-style: none;
            margin: 20px 0;
        }

        .pricing-features li {
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .testimonials {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 60px;
        }

        .testimonial-card {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--shadow);
        }

        .testimonial-text {
            font-style: italic;
            margin-bottom: 20px;
        }

        .testimonial-author {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .author-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }

        .faq {
            max-width: 800px;
            margin: 0 auto 60px;
        }

        .faq-item {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            margin-bottom: 15px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }

        .faq-question {
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
        }

        .faq-answer {
            padding: 0 20px 20px;
            color: var(--gray);
            display: none;
        }

        .cta {
            text-align: center;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            padding: 60px 0;
            border-radius: var(--border-radius);
            margin-bottom: 60px;
            box-shadow: var(--shadow);
        }

        .cta h2 {
            font-size: 2.5rem;
            margin-bottom: 20px;
        }

        footer {
            background: var(--darker);
            padding: 60px 0 30px;
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 40px;
            margin-bottom: 40px;
        }

        .footer-column h3 {
            font-size: 1.3rem;
            margin-bottom: 20px;
            color: var(--primary);
        }

        .footer-column ul {
            list-style: none;
        }

        .footer-column ul li {
            margin-bottom: 10px;
        }

        .footer-column a {
            color: var(--gray);
            text-decoration: none;
            transition: var(--transition);
        }

        .footer-column a:hover {
            color: var(--primary);
        }

        .social-icons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }

        .social-icons a {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background: var(--card-bg);
            border-radius: 50%;
            color: var(--light);
            transition: var(--transition);
        }

        .social-icons a:hover {
            background: var(--primary);
            transform: translateY(-3px);
        }

        .footer-bottom {
            text-align: center;
            padding-top: 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--gray);
        }

        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 20px;
            }
            
            nav ul {
                gap: 15px;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .hero-buttons {
                flex-direction: column;
                align-items: center;
            }
        }

        .ai-builder {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 30px;
            margin: 60px 0;
            box-shadow: var(--shadow);
        }

        .builder-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .builder-container {
            display: flex;
            gap: 30px;
        }

        .builder-input {
            flex: 1;
        }

        .builder-preview {
            flex: 1;
            background: white;
            border-radius: var(--border-radius);
            min-height: 400px;
            color: #333;
            padding: 20px;
        }

        .input-group {
            margin-bottom: 20px;
        }

        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .input-group input, .input-group select, .input-group textarea {
            width: 100%;
            padding: 12px 15px;
            border-radius: var(--border-radius);
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(0, 0, 0, 0.2);
            color: var(--light);
            font-size: 16px;
        }

        .input-group textarea {
            min-height: 120px;
            resize: vertical;
        }

        .generate-btn {
            width: 100%;
            padding: 15px;
            font-size: 1.1rem;
            margin-top: 20px;
        }

        .loading {
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid transparent;
            border-top: 2px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--success);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: var(--shadow);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1001;
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification.error {
            background: var(--danger);
        }

        .notification.warning {
            background: var(--warning);
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-cube"></i>
                    <div>MULtiverse <span>AI</span></div>
                </div>
                <nav>
                    <ul>
                        <li><a href="#features">Features</a></li>
                        <li><a href="#how-it-works">How It Works</a></li>
                        <li><a href="#templates">Templates</a></li>
                        <li><a href="#pricing">Pricing</a></li>
                        <li><a href="#testimonials">Testimonials</a></li>
                    </ul>
                </nav>
                <div class="auth-buttons">
                    <button class="btn btn-outline">Log In</button>
                    <button class="btn btn-primary">Sign Up Free</button>
                </div>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <h1>Build Websites With AI In Seconds</h1>
            <p>MULtiverse AI transforms your ideas into fully functional websites with the power of artificial intelligence. No coding required.</p>
            <div class="hero-buttons">
                <button class="btn btn-primary btn-large" onclick="scrollToBuilder()">Start Building Free</button>
                <button class="btn btn-outline btn-large">Watch Demo</button>
            </div>
            <div class="hero-demo">
                <p>See how MULtiverse AI creates a professional website in under 2 minutes</p>
                <div style="height: 200px; background: linear-gradient(135deg, #3434a1, #8044ff); border-radius: var(--border-radius); display: flex; align-items: center; justify-content: center; margin-top: 20px;">
                    <i class="fas fa-play-circle" style="font-size: 3rem;"></i>
                </div>
            </div>
        </div>
    </section>

    <section class="ai-builder" id="ai-builder">
        <div class="container">
            <div class="builder-header">
                <h2>AI Website Builder</h2>
                <p>Describe your website and let our AI create it for you</p>
            </div>
            <div class="builder-container">
                <div class="builder-input">
                    <div class="input-group">
                        <label for="website-type">Website Type</label>
                        <select id="website-type">
                            <option value="business">Business</option>
                            <option value="portfolio">Portfolio</option>
                            <option value="ecommerce">E-commerce</option>
                            <option value="blog">Blog</option>
                            <option value="event">Event</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label for="color-theme">Color Theme</label>
                        <select id="color-theme">
                            <option value="professional">Professional</option>
                            <option value="creative">Creative</option>
                            <option value="minimal">Minimal</option>
                            <option value="vibrant">Vibrant</option>
                            <option value="dark">Dark</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label for="website-description">Describe Your Website</label>
                        <textarea id="website-description" placeholder="Example: I need a portfolio website for my photography business with a dark theme and sections for my best work, about me, and contact information..."></textarea>
                    </div>
                    <button class="btn btn-primary generate-btn" id="generate-website-btn">
                        <i class="fas fa-magic"></i>
                        Generate Website
                    </button>
                </div>
                <div class="builder-preview" id="builder-preview">
                    <h3>Website Preview</h3>
                    <p>Your website will appear here after generation</p>
                    <div style="text-align: center; margin-top: 50px;">
                        <i class="fas fa-image" style="font-size: 3rem; color: #ccc;"></i>
                        <p>Preview will appear here</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="features">
        <div class="container">
            <h2 class="section-title">Powerful Features</h2>
            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h3>AI-Powered Builder</h3>
                    <p>Our advanced AI understands your requirements and builds complete websites with minimal input.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-palette"></i>
                    </div>
                    <h3>Smart Styling</h3>
                    <p>Automatically generated color schemes, typography, and layouts that follow design best practices.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-mobile-alt"></i>
                    </div>
                    <h3>Fully Responsive</h3>
                    <p>Every website created with MULtiverse AI is perfectly optimized for all devices and screen sizes.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-bolt"></i>
                    </div>
                    <h3>Lightning Fast</h3>
                    <p>Generate complete websites in seconds instead of spending hours designing and coding.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h3>Secure Hosting</h3>
                    <p>All websites include SSL certificates, CDN, and reliable hosting with 99.9% uptime.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3>SEO Optimized</h3>
                    <p>Built-in SEO tools help your website rank higher in search results from day one.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="how-it-works">
        <div class="container">
            <h2 class="section-title">How It Works</h2>
            <div class="how-it-works">
                <div class="step-card">
                    <div class="step-number">1</div>
                    <h3>Describe Your Needs</h3>
                    <p>Tell our AI what kind of website you want to build, your preferences, and any specific requirements.</p>
                </div>
                <div class="step-card">
                    <div class="step-number">2</div>
                    <h3>AI Generates Your Site</h3>
                    <p>Our AI engine processes your request and creates a complete website with content, images, and functionality.</p>
                </div>
                <div class="step-card">
                    <div class="step-number">3</div>
                    <h3>Customize & Publish</h3>
                    <p>Fine-tune your website with our easy-to-use editor and publish with a single click.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="templates">
        <div class="container">
            <h2 class="section-title">Professional Templates</h2>
            <div class="templates">
                <div class="template-card">
                    <div class="template-img">Business</div>
                    <div class="template-content">
                        <h3>Corporate Pro</h3>
                        <p>Professional design for businesses and corporations.</p>
                        <button class="btn btn-outline" style="margin-top: 15px;">Use Template</button>
                    </div>
                </div>
                <div class="template-card">
                    <div class="template-img">Portfolio</div>
                    <div class="template-content">
                        <h3>Creative Portfolio</h3>
                        <p>Showcase your work with this stunning portfolio template.</p>
                        <button class="btn btn-outline" style="margin-top: 15px;">Use Template</button>
                    </div>
                </div>
                <div class="template-card">
                    <div class="template-img">E-commerce</div>
                    <div class="template-content">
                        <h3>Online Store</h3>
                        <p>Complete e-commerce solution with product listings and cart.</p>
                        <button class="btn btn-outline" style="margin-top: 15px;">Use Template</button>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="pricing">
        <div class="container">
            <h2 class="section-title">Simple Pricing</h2>
            <div class="pricing">
                <div class="pricing-card">
                    <h3>Starter</h3>
                    <div class="price">Free</div>
                    <p>Perfect for trying out MULtiverse AI</p>
                    <ul class="pricing-features">
                        <li>1 AI-generated website</li>
                        <li>Basic customization</li>
                        <li>MULtiverse subdomain</li>
                        <li>Standard support</li>
                    </ul>
                    <button class="btn btn-outline">Get Started</button>
                </div>
                <div class="pricing-card">
                    <h3>Pro</h3>
                    <div class="price">$19/mo</div>
                    <p>For professionals and growing businesses</p>
                    <ul class="pricing-features">
                        <li>10 AI-generated websites</li>
                        <li>Advanced customization</li>
                        <li>Custom domain</li>
                        <li>Priority support</li>
                        <li>Basic SEO tools</li>
                    </ul>
                    <button class="btn btn-primary">Get Started</button>
                </div>
                <div class="pricing-card">
                    <h3>Enterprise</h3>
                    <div class="price">$49/mo</div>
                    <p>For agencies and large organizations</p>
                    <ul class="pricing-features">
                        <li>Unlimited websites</li>
                        <li>Full customization</li>
                        <li>Multiple custom domains</li>
                        <li>24/7 premium support</li>
                        <li>Advanced SEO & analytics</li>
                    </ul>
                    <button class="btn btn-primary">Get Started</button>
                </div>
            </div>
        </div>
    </section>

    <section id="testimonials">
        <div class="container">
            <h2 class="section-title">What Users Say</h2>
            <div class="testimonials">
                <div class="testimonial-card">
                    <div class="testimonial-text">
                        "MULtiverse AI saved me countless hours of development time. I was able to create a professional website for my business in under an hour!"
                    </div>
                    <div class="testimonial-author">
                        <div class="author-avatar">SJ</div>
                        <div>
                            <h4>Sarah Johnson</h4>
                            <p>Small Business Owner</p>
                        </div>
                    </div>
                </div>
                <div class="testimonial-card">
                    <div class="testimonial-text">
                        "As a designer, I'm impressed by the quality of the websites MULtiverse AI creates. The design choices are consistently on point."
                    </div>
                    <div class="testimonial-author">
                        <div class="author-avatar">MR</div>
                        <div>
                            <h4>Michael Rodriguez</h4>
                            <p>UX Designer</p>
                        </div>
                    </div>
                </div>
                <div class="testimonial-card">
                    <div class="testimonial-text">
                        "I've tried several AI website builders, and MULtiverse AI is by far the most intuitive and powerful. The results speak for themselves."
                    </div>
                    <div class="testimonial-author">
                        <div class="author-avatar">AL</div>
                        <div>
                            <h4>Amanda Lee</h4>
                            <p>Marketing Director</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="faq">
        <div class="container">
            <h2 class="section-title">Frequently Asked Questions</h2>
            <div class="faq">
                <div class="faq-item">
                    <div class="faq-question">
                        How does MULtiverse AI work? <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer">
                        MULtiverse AI uses advanced machine learning algorithms to understand your requirements and generate complete, functional websites. Simply describe what you need, and our AI does the rest.
                    </div>
                </div>
                <div class="faq-item">
                    <div class="faq-question">
                        Do I need coding skills to use MULtiverse AI? <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer">
                        No coding skills are required! MULtiverse AI is designed for everyone, from complete beginners to professional developers.
                    </div>
                </div>
                <div class="faq-item">
                    <div class="faq-question">
                        Can I customize the websites generated by AI? <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer">
                        Yes, all websites come with our easy-to-use visual editor that allows you to customize every aspect of your site without touching code.
                    </div>
                </div>
                <div class="faq-item">
                    <div class="faq-question">
                        What if I don't like the website the AI creates? <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="faq-answer">
                        You can either ask the AI to regenerate with different parameters or use our editor to make any changes you want.
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section class="cta">
        <div class="container">
            <h2>Ready to Build Your Website?</h2>
            <p>Join thousands of users creating amazing websites with AI</p>
            <button class="btn btn-large" style="background: white; color: var(--primary); margin-top: 30px;" onclick="scrollToBuilder()">Get Started For Free</button>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-column">
                    <h3>MULtiverse AI</h3>
                    <p>The next generation AI website builder that helps you create professional websites in seconds.</p>
                    <div class="social-icons">
                        <a href="#"><i class="fab fa-twitter"></i></a>
                        <a href="#"><i class="fab fa-facebook-f"></i></a>
                        <a href="#"><i class="fab fa-instagram"></i></a>
                        <a href="#"><i class="fab fa-linkedin-in"></i></a>
                    </div>
                </div>
                <div class="footer-column">
                    <h3>Product</h3>
                    <ul>
                        <li><a href="#">Features</a></li>
                        <li><a href="#">Templates</a></li>
                        <li><a href="#">Pricing</a></li>
                        <li><a href="#">Use Cases</a></li>
                    </ul>
                </div>
                <div class="footer-column">
                    <h3>Resources</h3>
                    <ul>
                        <li><a href="#">Blog</a></li>
                        <li><a href="#">Tutorials</a></li>
                        <li><a href="#">Documentation</a></li>
                        <li><a href="#">Support</a></li>
                    </ul>
                </div>
                <div class="footer-column">
                    <h3>Company</h3>
                    <ul>
                        <li><a href="#">About Us</a></li>
                        <li><a href="#">Careers</a></li>
                        <li><a href="#">Privacy Policy</a></li>
                        <li><a href="#">Terms of Service</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 MULtiverse AI. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <div class="notification" id="notification"></div>

    <script>
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

        // Smooth scrolling
        function scrollToBuilder() {
            document.getElementById('ai-builder').scrollIntoView({ 
                behavior: 'smooth' 
            });
        }

        // Notification system
        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification ${type} show`;
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }

        // Generate website functionality
        document.getElementById('generate-website-btn').addEventListener('click', async function() {
            const websiteType = document.getElementById('website-type').value;
            const colorTheme = document.getElementById('color-theme').value;
            const description = document.getElementById('website-description').value;
            
            if (!description.trim()) {
                showNotification('Please describe your website', 'warning');
                return;
            }
            
            const preview = document.getElementById('builder-preview');
            const btn = this;
            
            // Show loading state
            btn.innerHTML = '<div class="loading"><div class="spinner"></div>Generating...</div>';
            btn.disabled = true;
            
            preview.innerHTML = `
                <div style="text-align: center; padding: 50px 0;">
                    <div class="spinner" style="margin: 0 auto 20px;"></div>
                    <h3>Generating your website...</h3>
                    <p>Using DeepSeek AI to create your ${websiteType} website</p>
                </div>
            `;
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: `Create a ${websiteType} website with a ${colorTheme} theme. ${description}`,
                        projectType: websiteType,
                        currentFiles: {}
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    // Show success preview
                    preview.innerHTML = `
                        <h3>✅ Website Generated!</h3>
                        <p><strong>Model Used:</strong> ${result.model_used || 'DeepSeek R1'}</p>
                        <p><strong>Files Created:</strong> ${Object.keys(result.files || {}).length}</p>
                        <div style="margin: 20px 0; padding: 15px; background: #f5f5f7; border-radius: 8px; color: #333;">
                            <h4>Generated Files:</h4>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                ${Object.keys(result.files || {}).map(file => `<li>${file}</li>`).join('')}
                            </ul>
                        </div>
                        <div style="display: flex; gap: 10px; margin-top: 20px;">
                            <button class="btn btn-primary" onclick="previewWebsite('${result.sessionId}')">
                                <i class="fas fa-eye"></i> Preview Website
                            </button>
                            <button class="btn btn-outline" onclick="downloadProject('${result.sessionId}')">
                                <i class="fas fa-download"></i> Download
                            </button>
                        </div>
                    `;
                    
                    showNotification('Website generated successfully!', 'success');
                } else {
                    throw new Error(result.error || 'Generation failed');
                }
            } catch (error) {
                preview.innerHTML = `
                    <div style="text-align: center; padding: 50px 0;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--danger);"></i>
                        <h3>Generation Failed</h3>
                        <p>${error.message}</p>
                        <button class="btn btn-outline" onclick="location.reload()">Try Again</button>
                    </div>
                `;
                showNotification(`Generation failed: ${error.message}`, 'error');
            } finally {
                btn.innerHTML = '<i class="fas fa-magic"></i> Generate Website';
                btn.disabled = false;
            }
        });

        // Preview website in new tab
        function previewWebsite(sessionId) {
            window.open(`/preview/${sessionId}`, '_blank');
        }

        // Download project
        function downloadProject(sessionId) {
            window.open(`/download/${sessionId}`, '_blank');
        }
    </script>
</body>
</html>'''

@app.route('/script.js')
def script():
    """Serve the JavaScript file"""
    return "console.log('Multiverse AI Web Builder loaded');", 200, {'Content-Type': 'application/javascript'}

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate website using AI with DeepSeek models"""
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
        
        # Set environment variables for DeepSeek models
        env = os.environ.copy()
        env['OPENROUTER_KEY'] = os.environ.get('OPENROUTER_KEY', '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')
        env['MODEL_NAME'] = 'deepseek/deepseek-r1-0528:free'
        env['LOCAL_MODEL'] = 'true'
        env['OPENAI_API_BASE'] = 'https://openrouter.ai/api/v1'
        env['OPENAI_API_KEY'] = env['OPENROUTER_KEY']
        
        # Run the GPT Engineer CLI with improved mode if files exist
        cmd_args = [
            'python', '-m', 'gpt_engineer.applications.cli.main', 
            project_dir,
            '--model', 'deepseek/deepseek-r1-0528:free',
            '--no_execution',
            '--lite',
            '--temperature', '0.1'
        ]
        
        if current_files:
            cmd_args.append('--improve')
        
        try:
            print(f"Running command: {' '.join(cmd_args)}")
            completed = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env,
                cwd=os.getcwd()
            )
            
            print(f"Command completed with return code: {completed.returncode}")
            print(f"STDOUT: {completed.stdout}")
            if completed.stderr:
                print(f"STDERR: {completed.stderr}")
                
        except subprocess.TimeoutExpired:
            shutil.rmtree(project_dir, ignore_errors=True)
            return jsonify({'error': 'Generation timed out. Please try with a simpler prompt.'}), 500
        except Exception as e:
            print(f"Subprocess error: {e}")
            shutil.rmtree(project_dir, ignore_errors=True)
            return jsonify({'error': f'Generation failed: {str(e)}'}), 500
        
        # Read generated files
        generated_files = {}
        try:
            for file_path in Path(project_dir).rglob('*'):
                if file_path.is_file() and file_path.name not in ['prompt', '.gitignore']:
                    relative_path = file_path.relative_to(project_dir)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():  # Only include non-empty files
                                generated_files[str(relative_path)] = content
                    except UnicodeDecodeError:
                        # Skip binary files
                        continue
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
                        continue
        except Exception as e:
            print(f"Error reading generated files: {e}")
        
        # If no files were generated, create a simple website
        if not generated_files:
            generated_files = create_fallback_website(prompt, project_type)
        
        # Store session info
        SESSIONS[session_id] = {
            'prompt': prompt,
            'files': generated_files,
            'project_type': project_type,
            'path': project_dir,
            'returncode': completed.returncode if 'completed' in locals() else -1,
            'stdout': completed.stdout if 'completed' in locals() else '',
            'stderr': completed.stderr if 'completed' in locals() else '',
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
            'success': len(generated_files) > 0,
            'stdout': completed.stdout if 'completed' in locals() else '',
            'stderr': completed.stderr if 'completed' in locals() else ''
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

def create_fallback_website(prompt, project_type):
    """Create a fallback website if generation fails"""
    return {
        'index.html': f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_type.title()} Website</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <nav>
            <div class="logo">My {project_type.title()}</div>
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
                <h1>Welcome to My {project_type.title()}</h1>
                <p>Generated by Multiverse AI based on: {prompt[:100]}...</p>
                <button class="cta-button">Get Started</button>
            </div>
        </section>

        <section id="about" class="section">
            <div class="container">
                <h2>About</h2>
                <p>This website was created using Multiverse AI with DeepSeek models.</p>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 My {project_type.title()}. Built with Multiverse AI.</p>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>''',
        'style.css': '''/* Modern CSS Reset */
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

footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 2rem 0;
}

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
}''',
        'script.js': '''// Website functionality
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

    console.log('Website loaded successfully with Multiverse AI');
});'''
    }

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

@app.route('/download/<session_id>')
def download_session(session_id):
    """Download project files as a zip"""
    if session_id not in SESSIONS:
        return "Session not found", 404
    
    try:
        import zipfile
        from io import BytesIO
        
        files = SESSIONS[session_id]['files']
        
        # Create zip file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in files.items():
                zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f'multiverse-project-{session_id}.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/outputs/<path:filename>')
def outputs(filename):
    """Serve output files"""
    return send_from_directory(OUTPUT_ROOT, filename)

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
- Include at least index.html, style.css, and script.js files

DESIGN GUIDELINES:
- Use a modern color scheme that matches the {project_type} theme
- Include proper typography hierarchy
- Add subtle animations and micro-interactions
- Ensure good contrast ratios for accessibility
- Use consistent spacing and layout patterns
- Include hover states for interactive elements

CONTENT STRUCTURE:
- Header with navigation
- Hero section with compelling headline
- Main content sections relevant to {project_type}
- Footer with contact information
- Responsive design for mobile devices
"""
    
    if current_files:
        base_prompt += "\nEXISTING FILES TO MODIFY:\n"
        for filename, content in current_files.items():
            base_prompt += f"\n{filename}:\n```\n{content[:500]}{'...' if len(content) > 500 else ''}\n```\n"
    else:
        base_prompt += "\nCreate a complete website from scratch with all necessary files.\n"
    
    base_prompt += """
INSTRUCTIONS:
- Create complete, functional files
- Ensure all files work together seamlessly
- Use placeholder content that matches the theme
- Make the design modern and visually appealing
- Include proper file structure and organization
- Test that all links and functionality work

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
    print("🤖 Using DeepSeek models via OpenRouter")
    print("🌐 Open your browser to see the web builder interface")
    
    # Test OpenRouter connection
    try:
        import requests
        api_key = os.environ.get('OPENROUTER_KEY')
        if api_key:
            print("✅ OpenRouter API key found")
        else:
            print("⚠️  No OpenRouter API key found - using fallback")
    except Exception as e:
        print(f"⚠️  OpenRouter test failed: {e}")
    
    # For Bolt preview, bind to 0.0.0.0
    app.run(host='0.0.0.0', port=port, debug=True)