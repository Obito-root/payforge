#!/bin/bash

# PayForge Installation Script
# For Kali Linux / Debian-based systems

set -e

echo "[*] PayForge Installation Started..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "[!] This script must be run as root (sudo)"
   exit 1
fi

# Define installation directory
INSTALL_DIR="/opt/payforge"
BINARY_PATH="/usr/local/bin/payforge"
ELECTRON_PATH="/usr/local/bin/payforge-login"

echo "[+] Creating installation directory..."
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

echo "[+] Cloning PayForge repository..."
git clone https://github.com/Obito-root/payforge.git $INSTALL_DIR || echo "[!] Repository may already exist"

echo "[+] Installing Python dependencies..."
pip3 install -r $INSTALL_DIR/requirements.txt

echo "[+] Installing Node.js dependencies for Electron..."
cd $INSTALL_DIR/electron
npm install

echo "[+] Creating system-wide binary links..."
cp $INSTALL_DIR/payforge $BINARY_PATH
chmod +x $BINARY_PATH

cp $INSTALL_DIR/payforge-gui $ELECTRON_PATH
chmod +x $ELECTRON_PATH

echo "[+] Creating PayForge directory in /opt..."
mkdir -p /opt/payforge/{logs,database,payloads}

echo "[+] Setting permissions..."
chown -R root:root $INSTALL_DIR
chmod -R 755 $INSTALL_DIR

echo "[+] Creating symbolic link for easy access..."
ln -sf $INSTALL_DIR /opt/payforge

echo ""
echo "=========================================="
echo "[✓] PayForge Installed Successfully!"
echo "=========================================="
echo ""
echo "Usage:"
echo "  payforge --help              # Show help menu"
echo "  payforge console             # Start interactive console"
echo "  payforge-login               # Launch Electron login screen"
echo "  payforge scan -t <target>    # Run security scan"
echo ""
echo "Configuration: /opt/payforge/config/payforge.conf"
echo "Logs: /opt/payforge/logs/"
echo ""
echo "[*] Start with: payforge-login"
echo "=========================================="
