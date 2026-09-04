
<p align="center">
  <img src="https://img.shields.io/badge/PayForge-v1.0.0-6366f1?style=for-the-badge&logo=python&logoColor=white" alt="PayForge v1.0.0">
  <br/>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Platform-Kali%20Linux-557C94?style=for-the-badge&logo=linux&logoColor=white" alt="Kali Linux">
  <img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Status-Active-27ae60?style=for-the-badge" alt="Active">
</p>

---

# 🔥 PayForge - Professional Security Testing Framework

**PayForge** is a comprehensive, modular security testing framework designed for penetration testers, security researchers, and ethical hackers. Built with an **Electron-based authentication system**, system-wide installation support, and an interactive Metasploit-like console.

> **Educational Framework for Authorized Security Testing Only**

⚠️ **DISCLAIMER:** PayForge is designed for authorized penetration testing, CTF competitions, and educational purposes only. Unauthorized access to computer systems is illegal. Users are solely responsible for ensuring compliance with all applicable laws and regulations.

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Commands](#-commands)
- [Modules](#-modules)
- [Architecture](#-architecture)
- [Electron Authentication](#-electron-authentication)
- [Module Development](#-module-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🎯 Core Capabilities

- ✅ **Interactive Console** - Metasploit-style command interface
- ✅ **Module System** - Dynamically load and execute security modules
- ✅ **Electron Login** - Secure authentication with ethical guidelines
- ✅ **System-wide Installation** - Install once, use from anywhere
- ✅ **Multiple Modules**:
  - Network Reconnaissance (Nmap)
  - Web Vulnerability Scanning
  - Subdomain Enumeration
  - Payload Generation (Educational)
  - Custom Module Support

### 🔐 Security Features

- ✅ **Electron-based Authentication** - GUI login screen with security measures
- ✅ **Ethical Guidelines** - Mandatory acknowledgment before use
- ✅ **Session Management** - Track all testing sessions
- ✅ **Logging & Auditing** - Complete audit trail of all activities
- ✅ **Database Storage** - Persistent results and session tracking

### 🛠️ Developer Features

- ✅ **Easy Module Creation** - Simple Python API for custom modules
- ✅ **Extensible Architecture** - Plugin system for new functionality
- ✅ **Rich CLI** - Colorized output and progress indicators
- ✅ **Configuration Management** - JSON-based settings
- ✅ **Module Metadata** - Version, author, risk level tracking

---

## 🚀 Installation

### Prerequisites

```bash
- Kali Linux 2024+ (or Debian-based Linux)
- Python 3.9 or higher
- Node.js 14+ (for Electron)
- Sudo privileges
- Internet connection
```

### Automated Installation

**Step 1:** Clone the repository

```bash
git clone https://github.com/Obito-root/payforge.git
cd payforge
```

**Step 2:** Run the installer

```bash
sudo bash install.sh
```

The installer will:
- ✅ Check system requirements
- ✅ Install Python dependencies
- ✅ Install Node.js dependencies (Electron)
- ✅ Create `/opt/payforge` installation directory
- ✅ Register `/usr/local/bin/payforge` binary
- ✅ Create Kali Linux desktop shortcuts
- ✅ Set up database and configuration

**Step 3:** Launch PayForge

```bash
payforge-login
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies for Electron
cd electron
npm install
cd ..

# Run PayForge
python3 src/main.py --console
```

---

## 🎯 Quick Start

### Launch with Electron Login

```bash
payforge-login
```
```username
admin
```
```passwd
admin123
```

This opens the Electron authentication screen where you must:
1. Agree to ethical guidelines
2. Enter username and password
3. Accept terms of service
4. Launch the main framework

### Start Interactive Console

```bash
payforge console
```

### Run a Quick Scan

```bash
payforge scan -t 192.168.1.1 --type quick
```

### List Available Modules

```bash
payforge modules
```

---

## 📖 Usage Guide

### Interactive Console Commands

#### **Target Management**

```bash
payforge> set-target 192.168.1.1
payforge> show-target
payforge> clear-target
```

#### **Module Management**

```bash
payforge> modules                    # List all modules
payforge> search nmap               # Search modules
payforge> use nmap_scanner          # Load module
payforge> info nmap_scanner         # Show module details
```

#### **Module Options**

```bash
payforge> options                   # Show current options
payforge> set threads 50            # Set option value
payforge> set ports 1-65535         # Set custom ports
```

#### **Execution**

```bash
payforge> run                       # Execute loaded module
payforge> exploit                   # Execute and show results
payforge> check                     # Check if target is vulnerable
```

#### **Session & Results**

```bash
payforge> show-sessions             # List all sessions
payforge> show-results              # Display scan results
payforge> save-result <name>        # Save current result
```

#### **Utility Commands**

```bash
payforge> background                # Background current session
payforge> history                   # Show command history
payforge> help                      # Show help menu
payforge> exit                      # Exit PayForge
```

---

## 🎮 Commands

### CLI Mode

```bash
# Show help
payforge --help

# Start interactive console
payforge console

# Launch with Electron login
payforge-login

# Run scan directly
payforge scan -t <target> --type <type>

# List modules
payforge modules

# Get module info
payforge info <module_name>

# Search modules
payforge search <keyword>

# Show configuration
payforge config --show-all

# Edit configuration
payforge config <setting> <value>
```

---

## 🧩 Modules

### Built-in Modules

#### **1. Nmap Port Scanner**
```
Category:      Reconnaissance
Risk Level:    Low
Description:   Advanced network scanning with Nmap
Dependencies:  nmap
```

**Usage:**
```bash
payforge> use nmap_scanner
payforge> set-target 192.168.1.1
payforge> set ports 1-1000
payforge> set scan_type sS
payforge> run
```

---

#### **2. Web Vulnerability Scanner**
```
Category:      Scanning
Risk Level:    Medium
Description:   Detects SQL injection, XSS, CSRF vulnerabilities
Dependencies:  requests
```

**Usage:**
```bash
payforge> use web_vulnerability_scanner
payforge> set-target https://target.com
payforge> set check_sqli True
payforge> set check_xss True
payforge> exploit
```

---

#### **3. Subdomain Enumeration**
```
Category:      Reconnaissance
Risk Level:    Low
Description:   Discovers subdomains and DNS records
Dependencies:  dnspython
```

**Usage:**
```bash
payforge> use subdomain_enumeration
payforge> set-target example.com
payforge> set wordlist_size large
payforge> run
```

---

#### **4. Payload Generator**
```
Category:      Exploitation
Risk Level:    High
Description:   Educational payload generation (simulation only)
Dependencies:  None
```

**Usage:**
```bash
payforge> use payload_generator
payforge> set-target 192.168.1.1
payforge> set payload_type web
payforge> set format base64
payforge> run
```

---

## 🏗️ Architecture

```
payforge/
├── payforge                          # Main CLI binary
├── payforge-gui                      # Electron login launcher
├── install.sh                        # Automated installer
├── requirements.txt                  # Python dependencies
│
├── src/
│   ├── main.py                      # Core framework
│   ├── console/
│   │   └── msf_console.py          # Interactive console
│   ├── modules/
│   │   ├── module_loader.py        # Module loading system
│   │   └── __init__.py
│   ├── payloads/                    # Exploitation modules
│   │   ├── nmap_scanner.py
│   │   ├── web_vulnerability_scanner.py
│   │   ├── subdomain_enumeration.py
│   │   ├── payload_generator.py
│   │   └── __init__.py
│   ├── database/
│   │   ├── db_handler.py           # Database management
│   │   └── __init__.py
│   ├── auth/
│   │   ├── electron_auth.py        # Electron login handler
│   │   └── __init__.py
│   └── utils/
│       ├── logger.py                # Logging system
│       └── __init__.py
│
├── electron/
│   ├── main.js                      # Electron main process
│   ├── preload.js
│   ├── package.json
│   └── src/
│       ├── login.html              # Login UI
│       ├── login.css               # Styling
│       └── login.js                # Login logic
│
├── config/
│   ├── payforge.conf               # Configuration file
│   └── ethical_guidelines.md       # Ethical guidelines
│
├── database/
│   └── payforge.db                 # SQLite database
│
├── README.md                        # This file
└── LICENSE                          # MIT License
```

---

## 🔐 Electron Authentication

### How It Works

1. **Launch**: `payforge-login` opens Electron window
2. **Ethics Agreement**: User must agree to ethical guidelines
3. **Authentication**: Username/password entry
4. **Verification**: Credentials validated against database
5. **Session Creation**: Creates secure session token
6. **Console Access**: Launch PayForge console with authenticated session

### Security Features

- ✅ Hashed password storage (SHA-256)
- ✅ Session token generation
- ✅ Timeout after inactivity (30 minutes)
- ✅ Activity logging and audit trail
- ✅ Ethical guidelines display

### Configuration

Edit `/opt/payforge/config/payforge.conf`:

```json
{
  "auth": {
    "timeout": 1800,
    "max_login_attempts": 3,
    "password_min_length": 8
  },
  "logging": {
    "level": "INFO",
    "file": "/opt/payforge/logs/payforge.log"
  }
}
```

---

## 🛠️ Module Development

### Create Custom Module

**File:** `src/payloads/my_module.py`

```python
"""
PayForge Custom Module Template
"""

MODULE_METADATA = {
    'name': 'My Custom Module',
    'version': '1.0.0',
    'author': 'Your Name',
    'description': 'Description of what module does',
    'category': 'reconnaissance',  # or scanning, exploitation, etc.
    'dependencies': ['requests'],  # Required packages
    'requires_auth': True,
    'risk_level': 'medium'         # low, medium, high, critical
}

def execute(target: str, options: dict) -> dict:
    """
    Main module execution function
    
    Args:
        target: Target IP/Domain
        options: Dictionary of options set by user
    
    Returns:
        Dictionary with results
    """
    try:
        # Your implementation here
        result = analyze_target(target, options)
        
        return {
            'status': 'success',
            'target': target,
            'module': 'my_module',
            'results': result
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'target': target
        }

def analyze_target(target: str, options: dict):
    """Helper function for analysis"""
    # Implementation details
    pass
```

### Load Custom Module

```bash
payforge> use my_module
payforge> info my_module
payforge> set-target <target>
payforge> set <option> <value>
payforge> run
```

---

## 🔧 Configuration

### Main Config File

Location: `/opt/payforge/config/payforge.conf`

```json
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
```

### Ethical Guidelines

Location: `/opt/payforge/config/ethical_guidelines.md`

```markdown
# PayForge Ethical Guidelines

1. **Authorization**
   - Only test systems you own or have explicit written permission to test
   - Obtain written approval before any security assessment
   - Respect scope and boundaries

2. **Confidentiality**
   - Treat all findings as confidential
   - Do not disclose vulnerabilities publicly without responsible disclosure
   - Keep assessment reports secure

3. **Responsible Disclosure**
   - Report vulnerabilities to affected parties
   - Allow reasonable time for patching
   - Coordinate public disclosure

4. **Legal Compliance**
   - Follow all applicable laws and regulations
   - Comply with data protection regulations (GDPR, etc.)
   - Maintain audit trails

5. **Professional Conduct**
   - Use framework responsibly
   - Do not cause harm or damage
   - Maintain professional integrity
```

---

## 📊 Example Workflows

### Workflow 1: Quick Network Reconnaissance

```bash
$ payforge console

payforge> set-target example.com
payforge> use subdomain_enumeration
payforge> set wordlist_size large
payforge> run

payforge> use nmap_scanner
payforge> set-target 192.168.1.1
payforge> set ports 1-65535
payforge> run
```

### Workflow 2: Web Application Testing

```bash
payforge> set-target https://vulnerable-app.local
payforge> use web_vulnerability_scanner
payforge> set check_sqli True
payforge> set check_xss True
payforge> set check_csrf True
payforge> exploit

payforge> show-results
payforge> save-result web_app_assessment
```

### Workflow 3: Payload Generation

```bash
payforge> use payload_generator
payforge> set-target 192.168.1.100
payforge> set payload_type web
payforge> set platform linux
payforge> set format base64
payforge> run
```

---

## 🐛 Troubleshooting

### Issue: "Nmap not found"

**Solution:**
```bash
sudo apt-get update
sudo apt-get install nmap
```

### Issue: "Permission denied" during installation

**Solution:**
```bash
sudo bash install.sh
# Make sure you use sudo
```

### Issue: Electron window won't open

**Solution:**
```bash
cd electron
npm install
cd ..
payforge-login
```

### Issue: Module not loading

**Solution:**
```bash
# Check module syntax
python3 -m py_compile src/payloads/module_name.py

# Verify module metadata
cat src/payloads/module_name.py | grep MODULE_METADATA
```

### Issue: Database error

**Solution:**
```bash
# Reset database
rm /opt/payforge/database/payforge.db

# PayForge will recreate on next run
payforge console
```

---

## 📝 Logging

All activities are logged to: `/opt/payforge/logs/payforge.log`

### View Logs

```bash
tail -f /opt/payforge/logs/payforge.log
```

### Log Levels

- `DEBUG` - Detailed information for debugging
- `INFO` - General information messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

---

## 🔄 Uninstallation

```bash
sudo bash /opt/payforge/uninstall.sh
```

Or manually:

```bash
sudo rm -rf /opt/payforge
sudo rm /usr/local/bin/payforge
sudo rm /usr/local/bin/payforge-login
sudo rm /usr/share/applications/payforge.desktop
```

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Module Development Guide](docs/MODULES.md)
- [CLI Reference](docs/CLI.md)
- [API Documentation](docs/API.md)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for functions
- Add docstrings to all functions
- Test before submitting PR

---

## ⚖️ Legal Disclaimer

**IMPORTANT:** PayForge is provided for authorized security testing and educational purposes only. By using this framework, you agree to:

- ✅ Only test systems you own or have explicit written authorization to test
- ✅ Comply with all applicable laws and regulations
- ✅ Take full responsibility for your actions
- ✅ Not use PayForge for unauthorized access or malicious purposes
- ✅ Report vulnerabilities responsibly

**Unauthorized access to computer systems is illegal and may result in criminal charges.**

---

## 📄 License

PayForge is released under the **MIT License**. See [LICENSE](LICENSE) file for details.

---

## 👥 Authors & Contributors

**PayForge Team**
- Security Testing Framework Development
- Educational Framework for Authorized Testing
- Open Source Community Project

---

## 📞 Support & Contact

- **GitHub Issues**: [Report bugs](https://github.com/Obito-root/payforge/issues)
- **GitHub Discussions**: [Community forum](https://github.com/Obito-root/payforge/discussions)
- **Email**: security@payforge.dev (if applicable)
- **Documentation**: [Wiki](https://github.com/Obito-root/payforge/wiki)

---

## 🎯 Roadmap

### v1.1.0 (Planned)
- [ ] REST API server mode
- [ ] Webhook integrations
- [ ] Advanced reporting (PDF, DOCX)
- [ ] Team collaboration features
- [ ] Cloud integration

### v1.2.0 (Planned)
- [ ] Mobile app
- [ ] Machine learning vulnerability detection
- [ ] Custom plugin marketplace
- [ ] Advanced scheduling
- [ ] Multi-user support

---

## 🌟 Star History

If you find PayForge useful, please consider giving it a star ⭐

---

<div align="center">

**PayForge v1.0.0** · Professional Security Testing Framework

[🏠 Home](https://github.com/Obito-root/payforge) · [📖 Docs](https://github.com/Obito-root/payforge/wiki) · [🐛 Issues](https://github.com/Obito-root/payforge/issues) · [⭐ Star](https://github.com/Obito-root/payforge)

**Educational Framework for Authorized Security Testing Only**

⚠️ **Remember: Use responsibly. Unauthorized testing is illegal.**

</div>
```

---

## **That's it!** 🎉

Your **PayForge README.md** is now complete with:

✅ Feature overview  
✅ Installation instructions  
✅ Quick start guide  
✅ Complete usage documentation  
✅ Module descriptions  
✅ Architecture diagram  
✅ Configuration guide  
✅ Development guide  
✅ Troubleshooting section  
✅ Legal disclaimers  
✅ Contributing guidelines  
✅ Roadmap  

---

git push origin main
```

Your **PayForge repository is now complete!** 🚀
