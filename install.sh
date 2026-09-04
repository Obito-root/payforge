#!/bin/bash

###############################################################################
# PayForge - Professional Security Testing Framework
# Installation Script for Kali Linux & Debian-based Systems
# 
# This script installs PayForge to /opt/payforge with system-wide access
# Usage: sudo bash install.sh
###############################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
INSTALL_PATH="/opt/payforge"
BIN_PATH="/usr/local/bin/payforge"
LOG_FILE="/var/log/payforge_install.log"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          PayForge Security Testing Framework                ║${NC}"
echo -e "${BLUE}║             System-wide Installation Script                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[!] This script must be run as root (use: sudo bash install.sh)${NC}"
   exit 1
fi

echo -e "${YELLOW}[*] Checking system requirements...${NC}"

# Update package lists
echo "[*] Updating package lists..."
apt-get update >> "$LOG_FILE" 2>&1

# Check and install dependencies
DEPENDENCIES=(
    "python3"
    "python3-pip"
    "python3-venv"
    "git"
    "nodejs"
    "npm"
    "curl"
    "wget"
    "libssl-dev"
    "libffi-dev"
    "python3-dev"
)

for dep in "${DEPENDENCIES[@]}"; do
    if ! command -v "$dep" &> /dev/null && ! dpkg -l | grep -q "^ii.*$dep"; then
        echo "[+] Installing $dep..."
        apt-get install -y "$dep" >> "$LOG_FILE" 2>&1
    else
        echo "[✓] $dep is already installed"
    fi
done

# Check for Electron (optional but recommended for GUI)
if ! command -v electron &> /dev/null; then
    echo -e "${YELLOW}[*] Installing Electron for GUI login screen...${NC}"
    npm install -g electron >> "$LOG_FILE" 2>&1 || echo "[!] Electron installation optional"
fi

# Create installation directory
echo -e "${YELLOW}[*] Creating installation directory...${NC}"
if [ -d "$INSTALL_PATH" ]; then
    echo "[!] PayForge already exists at $INSTALL_PATH"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
    rm -rf "$INSTALL_PATH"
fi

mkdir -p "$INSTALL_PATH"
mkdir -p "$INSTALL_PATH/modules"
mkdir -p "$INSTALL_PATH/payloads"
mkdir -p "$INSTALL_PATH/exploits"
mkdir -p "$INSTALL_PATH/encoders"
mkdir -p "$INSTALL_PATH/reports"
mkdir -p "$INSTALL_PATH/logs"
mkdir -p "$INSTALL_PATH/config"
mkdir -p "$INSTALL_PATH/gui"
mkdir -p "$INSTALL_PATH/database"

echo -e "${GREEN}[+] Directory structure created${NC}"

# Copy PayForge files (from repository)
echo -e "${YELLOW}[*] Installing PayForge framework...${NC}"
cp -r . "$INSTALL_PATH/" 2>/dev/null || true

# Create Python virtual environment
echo -e "${YELLOW}[*] Setting up Python virtual environment...${NC}"
python3 -m venv "$INSTALL_PATH/venv" >> "$LOG_FILE" 2>&1

# Activate venv and install Python dependencies
source "$INSTALL_PATH/venv/bin/activate"
pip install --upgrade pip >> "$LOG_FILE" 2>&1
pip install -r "$INSTALL_PATH/requirements.txt" >> "$LOG_FILE" 2>&1 || echo "[!] requirements.txt not found, skipping pip packages"

# Create system-wide binary wrapper
echo -e "${YELLOW}[*] Creating system-wide binary wrapper...${NC}"
cat > "$BIN_PATH" << 'EOF'
#!/bin/bash

# PayForge CLI Wrapper
PAYFORGE_PATH="/opt/payforge"
PAYFORGE_VENV="$PAYFORGE_PATH/venv"

# Activate virtual environment
source "$PAYFORGE_VENV/bin/activate"

# Run PayForge
cd "$PAYFORGE_PATH"
python3 "$PAYFORGE_PATH/payforge.py" "$@"
EOF

chmod +x "$BIN_PATH"
chmod +x "$INSTALL_PATH/payforge.py"

echo -e "${GREEN}[+] System-wide binary created at $BIN_PATH${NC}"

# Create payforge command alias for easy access
echo -e "${YELLOW}[*] Installing command aliases...${NC}"
if ! grep -q "alias payforge" /etc/bash.bashrc; then
    echo "alias payforge='$BIN_PATH'" >> /etc/bash.bashrc
fi

# Set proper permissions
echo -e "${YELLOW}[*] Setting permissions...${NC}"
chmod -R 755 "$INSTALL_PATH"
chmod 755 "$INSTALL_PATH/venv/bin/python3"

# Create configuration directory in user home
USER_CONFIG="$HOME/.payforge"
if [ ! -d "$USER_CONFIG" ]; then
    mkdir -p "$USER_CONFIG"
    mkdir -p "$USER_CONFIG/sessions"
    mkdir -p "$USER_CONFIG/reports"
fi

# Log installation
echo "[$(date '+%Y-%m-%d %H:%M:%S')] PayForge installed successfully at $INSTALL_PATH" >> "$LOG_FILE"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          PayForge Installation Complete!                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Installation Details:${NC}"
echo "  Installation Path: $INSTALL_PATH"
echo "  Command Alias:     payforge"
echo "  Binary Path:       $BIN_PATH"
echo "  Log File:          $LOG_FILE"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo "  1. Start PayForge:       ${YELLOW}payforge${NC}"
echo "  2. Show help:            ${YELLOW}payforge --help${NC}"
echo "  3. Start console:        ${YELLOW}payforge console${NC}"
echo "  4. List modules:         ${YELLOW}payforge modules list${NC}"
echo "  5. Start GUI:            ${YELLOW}payforge gui${NC}"
echo ""
echo -e "${YELLOW}[!] ETHICAL NOTICE:${NC}"
echo "    PayForge is designed for authorized security testing only."
echo "    Unauthorized access to computer systems is illegal."
echo "    Use this tool responsibly and ethically."
echo ""
echo -e "${GREEN}[+] Installation logged to: $LOG_FILE${NC}"
echo ""
