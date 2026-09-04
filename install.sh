#!/bin/bash

# PayForge Installation Script for Kali Linux
# Handles PEP 668 externally-managed-environment issues

set -e

echo "[*] PayForge Installation Started..."
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "[!] This script must be run as root (sudo)"
   exit 1
fi

# Define installation directory
INSTALL_DIR="/opt/payforge"
BINARY_PATH="/usr/local/bin/payforge"
ELECTRON_PATH="/usr/local/bin/payforge-login"
VENV_DIR="$INSTALL_DIR/venv"

echo "[+] Checking system requirements..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 is not installed"
    echo "[+] Installing Python 3..."
    apt-get update
    apt-get install -y python3 python3-full python3-pip python3-venv
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[!] Node.js is not installed"
    echo "[+] Installing Node.js..."
    apt-get update
    apt-get install -y nodejs npm
fi

echo "[+] System requirements check complete"
echo ""

# Clean up if directory exists
if [ -d "$INSTALL_DIR" ]; then
    echo "[!] Installation directory already exists"
    read -p "[?] Do you want to reinstall? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "[+] Removing old installation..."
        rm -rf "$INSTALL_DIR"
    else
        echo "[*] Installation cancelled"
        exit 0
    fi
fi

echo "[+] Creating installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "[+] Cloning PayForge repository..."
git clone https://github.com/Obito-root/payforge.git . 2>/dev/null || {
    echo "[!] Could not clone from GitHub"
    echo "[+] Please ensure you have git and internet connection"
    exit 1
}

echo "[+] Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

echo "[+] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "[+] Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "[+] Installing Python dependencies..."
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    pip install -r "$INSTALL_DIR/requirements.txt"
else
    echo "[!] requirements.txt not found"
    echo "[+] Installing minimal requirements..."
    pip install requests dnspython rich typer
fi

echo "[+] Installing Node.js dependencies for Electron..."
if [ -d "$INSTALL_DIR/electron" ]; then
    cd "$INSTALL_DIR/electron"
    npm install
    cd "$INSTALL_DIR"
else
    echo "[!] Electron directory not found"
fi

echo "[+] Creating PayForge directories..."
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/database"
mkdir -p "$INSTALL_DIR/payloads"
mkdir -p "$INSTALL_DIR/reports"

echo "[+] Creating CLI wrapper script..."
cat > "$BINARY_PATH" << 'EOF'
#!/bin/bash
# PayForge CLI Wrapper

INSTALL_DIR="/opt/payforge"
VENV_DIR="$INSTALL_DIR/venv"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run PayForge
python3 "$INSTALL_DIR/src/main.py" "$@"
EOF

chmod +x "$BINARY_PATH"

echo "[+] Creating Electron login launcher..."
cat > "$ELECTRON_PATH" << 'EOF'
#!/bin/bash
# PayForge Electron Login Launcher

INSTALL_DIR="/opt/payforge"
ELECTRON_DIR="$INSTALL_DIR/electron"
VENV_DIR="$INSTALL_DIR/venv"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check if Electron app exists
if [ ! -d "$ELECTRON_DIR" ]; then
    echo "[!] Electron directory not found at $ELECTRON_DIR"
    exit 1
fi

# Run Electron app
cd "$ELECTRON_DIR"
npm start
EOF

chmod +x "$ELECTRON_PATH"

echo "[+] Creating Kali Linux desktop entry..."
cat > "/usr/share/applications/payforge.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=PayForge
Comment=Professional Security Testing Framework
Exec=/usr/local/bin/payforge-login
Icon=application-x-executable
Categories=Security;Utility;
Terminal=false
EOF

echo "[+] Creating shell aliases..."
if ! grep -q "alias payforge=" /etc/bash.bashrc; then
    cat >> /etc/bash.bashrc << 'EOF'

# PayForge Aliases
alias payforge='/usr/local/bin/payforge'
alias payforge-login='/usr/local/bin/payforge-login'
alias pf-console='payforge console'
alias pf-scan='payforge scan'
EOF
fi

echo "[+] Setting permissions..."
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"
chmod 644 "/usr/share/applications/payforge.desktop"

echo "[+] Creating PayForge configuration..."
cat > "$INSTALL_DIR/config/payforge.conf" << 'EOF'
{
  "general": {
    "framework_name": "PayForge",
    "version": "1.0.0",
    "timeout": 300
  },
  "auth": {
    "login_required": true,
    "session_timeout": 1800,
    "max_attempts": 3
  },
  "modules": {
    "auto_load": true,
    "search_paths": ["src/payloads"]
  },
  "logging": {
    "level": "INFO",
    "file": "/opt/payforge/logs/payforge.log",
    "format": "%(asctime)s - %(levelname)s - %(message)s"
  },
  "database": {
    "type": "sqlite",
    "location": "/opt/payforge/database/payforge.db"
  }
}
EOF

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         PayForge Installation Completed Successfully!          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Installation Directory: $INSTALL_DIR"
echo "🐍 Virtual Environment: $VENV_DIR"
echo "📝 Configuration: $INSTALL_DIR/config/payforge.conf"
echo "📊 Database: $INSTALL_DIR/database/payforge.db"
echo "📋 Logs: $INSTALL_DIR/logs/payforge.log"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "1. Start PayForge with Electron login:"
echo "   $ payforge-login"
echo ""
echo "2. Or launch interactive console:"
echo "   $ payforge console"
echo ""
echo "3. View available commands:"
echo "   $ payforge --help"
echo ""
echo "4. List available modules:"
echo "   $ payforge modules"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Only use PayForge on authorized systems"
echo "   - Read ethical guidelines: cat $INSTALL_DIR/config/ethical_guidelines.md"
echo "   - All activities are logged to: $INSTALL_DIR/logs/payforge.log"
echo ""
echo "📚 Documentation: https://github.com/Obito-root/payforge"
echo "🐛 Report issues: https://github.com/Obito-root/payforge/issues"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "[✓] Installation complete!"
echo "[*] Run 'payforge-login' to start PayForge"
