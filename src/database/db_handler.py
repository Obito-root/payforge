"""
PayForge Database Handler
SQLite database management for scans and results
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class DatabaseHandler:
    """SQLite database management"""
    
    def __init__(self):
        self.db_dir = Path('/opt/payforge/database')
        self.db_dir.mkdir(exist_ok=True, parents=True)
        self.db_file = self.db_dir / 'payforge.db'
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Scans table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT UNIQUE NOT NULL,
                    target TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    duration INTEGER,
                    results TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Vulnerabilities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL,
                    vuln_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    payload TEXT,
                    remediation TEXT,
                    cwe TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
                )
            ''')
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT
                )
            ''')
            
            # Exploit results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exploit_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    module TEXT NOT NULL,
                    target TEXT NOT NULL,
                    result TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            ''')
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            print(f"[!] Error initializing database: {str(e)}")
    
    def save_scan(self, scan_config: Dict[str, Any]) -> bool:
        """Save scan configuration"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scans (scan_id, target, scan_type, status, timestamp, results)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                scan_config.get('scan_id', ''),
                scan_config.get('target', ''),
                scan_config.get('type', ''),
                scan_config.get('status', 'pending'),
                scan_config.get('timestamp', datetime.now().isoformat()),
                json.dumps(scan_config)
            ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"[!] Error saving scan: {str(e)}")
            return False
    
    def save_exploit_result(self, result: Dict[str, Any]) -> bool:
        """Save exploit execution result"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO exploit_results (session_id, module, target, result)
                VALUES (?, ?, ?, ?)
            ''', (
                result.get('session_id', ''),
                result.get('module', ''),
                result.get('target', ''),
                json.dumps(result.get('result', {}))
            ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"[!] Error saving exploit result: {str(e)}")
            return False
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM sessions ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        
        except Exception as e:
            print(f"[!] Error retrieving sessions: {str(e)}")
            return []
    
    def get_scan_results(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan results"""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM scans WHERE scan_id = ?', (scan_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        
        except Exception as e:
            print(f"[!] Error retrieving scan: {str(e)}")
            return None
    
    def save_vulnerability(self, vuln: Dict[str, Any]) -> bool:
        """Save vulnerability finding"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO vulnerabilities 
                (scan_id, vuln_type, severity, description, payload, remediation, cwe)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                vuln.get('scan_id', ''),
                vuln.get('type', ''),
                vuln.get('severity', 'Medium'),
                vuln.get('description', ''),
                vuln.get('payload', ''),
                vuln.get('remediation', ''),
                vuln.get('cwe', '')
            ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"[!] Error saving vulnerability: {str(e)}")
            return False
