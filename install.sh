#!/usr/bin/env bash
set -euo pipefail

# PayForge Installation Script for Debian-based systems (Kali)
# Handles common PEP 668 externally-managed-environment issues by using a venv.

echo "[*] PayForge Installation Started..."
echo ""

# Check if running as root
if [[ "${EUID:-}" -ne 0 ]]; then
   echo "[!] This script must be run as root (sudo)"
   exit 1
fi

# Paths and variables
INSTALL_DIR="/opt/payforge"
BINARY_PATH="/usr/local/bin/payforge"
ELECTRON_PATH="/usr/local/bin/payforge-login"
VENV_DIR="$INSTALL_DIR/venv"

# Helper to install packages non-interactively
apt_install() {
    PKG="$1"
    if ! dpkg -s "$PKG" >/dev/null 2>&1; then
        apt-get install -y "$PKG"
    fi
}

echo "[+] Checking system requirements..."

# Ensure apt cache is up-to-date once
apt-get update -y

# Check and install git
if ! command -v git &>/dev/null; then
    echo "[!] Git not found. Installing git..."
    apt_install git
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 is not installed. Installing python3 and venv support..."
    apt_install python3
    apt_install python3-venv
    apt_install python3-pip
fi

# Check if Node.js/npm is installed (used for Electron)
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "[!] Node.js/npm not found. Installing nodejs and npm..."
    apt_install nodejs
    apt_install npm
fi

echo "[+] System requirements check complete"
echo ""

# Reinstall prompt if INSTALL_DIR exists
if [ -d "$INSTALL_DIR" ]; then
    echo "[!] Installation directory already exists: $INSTALL_DIR"
    read -p "[?] Do you want to reinstall (this removes $INSTALL_DIR)? (y/N) " -r
    echo
    if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
        echo "[*] Installation cancelled"
        exit 0
    fi
    echo "[+] Removing old installation..."
    rm -rf "$INSTALL_DIR"
fi

echo "[+] Creating installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "[+] Cloning PayForge repository..."
if ! git clone https://github.com/Obito-root/payforge.git . ; then
    echo "[!] Could not clone repository https://github.com/Obito-root/payforge.git"
    echo "[+] Please ensure git and internet connection are available, and the repo URL is correct."
    exit 1
fi

echo "[+] Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

echo "[+] Activating virtual environment..."
# Use venv interpreter explicitly for installs; do NOT rely on `source` for non-interactive pip.
VENV_PY="$VENV_DIR/bin/python"
if [ ! -x "$VENV_PY" ]; then
    echo "[!] Virtualenv python not found at $VENV_PY"
    exit 1
fi

echo "[+] Upgrading pip, setuptools, and wheel in venv..."
"$VENV_PY" -m pip install --upgrade pip setuptools wheel

echo "[+] Installing Python dependencies..."
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    "$VENV_PY" -m pip install -r "$INSTALL_DIR/requirements.txt"
else
    echo "[!] requirements.txt not found, installing minimal dependencies..."
    "$VENV_PY" -m pip install requests dnspython rich typer
fi

echo "[+] Installing Node.js dependencies for Electron (if present)..."
if [ -d "$INSTALL_DIR/electron" ]; then
    pushd "$INSTALL_DIR/electron" >/dev/null
    npm install || { echo "[!] npm install failed in $INSTALL_DIR/electron"; popd >/dev/null; }
    popd >/dev/null
else
    echo "[!] Electron directory not found at $INSTALL_DIR/electron — skipping."
fi

echo "[+] Creating PayForge runtime directories..."
mkdir -p "$INSTALL_DIR/logs" \
         "$INSTALL_DIR/database" \
         "$INSTALL_DIR/payloads" \
         "$INSTALL_DIR/reports" \
         "$INSTALL_DIR/config"

# Ensure config directory exists before writing files
mkdir -p "$INSTALL_DIR/config"

echo "[+] Creating CLI wrapper script..."
cat > "$BINARY_PATH" <<'EOF'
#!/usr/bin/env bash
# PayForge CLI Wrapper - launches framework using the embedded venv

INSTALL_DIR="/opt/payforge"
VENV_DIR="$INSTALL_DIR/venv"
VENV_PY="$VENV_DIR/bin/python"

if [ ! -x "$VENV_PY" ]; then
  echo "[!] PayForge virtualenv not found. Please reinstall or run install.sh"
  exit 1
fi

# Run PayForge main entrypoint using venv python
exec "$VENV_PY" "$INSTALL_DIR/src/main.py" "$@"
EOF

chmod +x "$BINARY_PATH"

echo "[+] Creating Electron login launcher..."
cat > "$ELECTRON_PATH" <<'EOF'
#!/usr/bin/env bash
# PayForge Electron Login Launcher

INSTALL_DIR="/opt/payforge"
ELECTRON_DIR="$INSTALL_DIR/electron"
VENV_DIR="$INSTALL_DIR/venv"
VENV_PY="$VENV_DIR/bin/python"

if [ ! -d "$ELECTRON_DIR" ]; then
    echo "[!] Electron directory not found at $ELECTRON_DIR"
    exit 1
fi

# Use npm from system
cd "$ELECTRON_DIR" || exit 1
exec npm start
EOF

chmod +x "$ELECTRON_PATH"

echo "[+] Creating Kali Linux desktop entry..."
cat > "/usr/share/applications/payforge.desktop" <<'EOF'
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

echo "[+] Creating shell aliases (system-wide)..."
# Append aliases to system-wide bashrc if not present
if ! grep -q "alias payforge=" /etc/bash.bashrc 2>/dev/null; then
    cat >> /etc/bash.bashrc <<'ALIAS'

# PayForge Aliases
alias payforge='/usr/local/bin/payforge'
alias payforge-login='/usr/local/bin/payforge-login'
alias pf-console='payforge console'
alias pf-scan='payforge scan'
ALIAS
fi

echo "[+] Writing default configuration file..."
cat > "$INSTALL_DIR/config/payforge.conf" <<'EOF'
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

echo "[+] Creating user's local .payforge directory..."
HOME_DIR=$(eval echo "~${SUDO_USER:-$(whoami)}")
mkdir -p "$HOME_DIR/.payforge"
chmod 755 "$HOME_DIR/.payforge"

echo "[+] Setting file permissions..."
# Keep ownership at root for system-wide install
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"
chmod 644 "/usr/share/applications/payforge.desktop" || true

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
echo "[✓] Installation complete!"
