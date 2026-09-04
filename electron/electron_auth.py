"""
PayForge Electron Authentication Handler
Manages communication with Electron login screen
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

class ElectronAuth:
    """Handle Electron-based authentication"""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.payforge_dir = self.home_dir / '.payforge'
        self.auth_db = self.payforge_dir / 'auth.json'
        self.session_file = self.payforge_dir / 'session.json'
        
        # Ensure directories exist
        self.payforge_dir.mkdir(exist_ok=True, mode=0o755)
    
    def launch_electron_login(self) -> Optional[Dict[str, Any]]:
        """Launch Electron login window and wait for authentication"""
        
        try:
            # Check if already authenticated
            if self.is_authenticated():
                session = self.get_session()
                if session:
                    return session
            
            # Launch Electron app
            electron_dir = Path('/opt/payforge/electron')
            
            if not electron_dir.exists():
                print("[!] Electron directory not found")
                return None
            
            # Start Electron process
            process = subprocess.Popen(
                ['npm', 'start'],
                cwd=str(electron_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for process to complete
            process.wait(timeout=300)  # 5 minute timeout
            
            # Check if authentication was successful
            session = self.get_session()
            return session
        
        except subprocess.TimeoutExpired:
            print("[!] Authentication timeout")
            return None
        except Exception as e:
            print(f"[!] Authentication error: {str(e)}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if user has valid session"""
        try:
            if not self.session_file.exists():
                return False
            
            session = json.loads(self.session_file.read_text())
            
            # Check if session token exists
            if 'token' not in session:
                return False
            
            return True
        
        except Exception:
            return False
    
    def get_session(self) -> Optional[Dict[str, Any]]:
        """Get current session data"""
        try:
            if self.session_file.exists():
                return json.loads(self.session_file.read_text())
            return None
        except Exception:
            return None
    
    def save_session(self, token: str, username: str) -> bool:
        """Save session data"""
        try:
            session_data = {
                'token': token,
                'username': username,
                'created_at': str(Path.ctime(self.session_file)) if self.session_file.exists() else ''
            }
            self.session_file.write_text(json.dumps(session_data, indent=2))
            return True
        except Exception as e:
            print(f"[!] Error saving session: {str(e)}")
            return False
    
    def clear_session(self) -> bool:
        """Clear session data (logout)"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            return True
        except Exception as e:
            print(f"[!] Error clearing session: {str(e)}")
            return False
