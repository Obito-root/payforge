"""
PayForge Database Handler
SQLite database management for scans, sessions, and modules
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

class DatabaseHandler:
    """SQLite database handler for PayForge"""
    
    def __init__(self, db_path: str = "/opt/payforge/database/payforge.db"):
        """Initialize database connection"""
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT,
                status TEXT DEFAULT "active",
                created_at TEXT,
                closed_at TEXT
            )
        ''')
        
        # Scans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                target TEXT NOT NULL,
                type TEXT,
                status TEXT DEFAULT "running",
                results TEXT,
                started_at TEXT,
                completed_at TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Module executions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                module TEXT NOT NULL,
                target TEXT,
                result TEXT,
                timestamp TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Payloads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payloads (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                payload_code TEXT,
                description TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_data: Dict) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (id, username, email, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            session_data.get('username'),
            session_data.get('email'),
            session_data.get('status', 'active'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return session_id
    
    def update_session(self, session_id: str, updates: Dict):
        """Update session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [session_id]
        
        cursor.execute(f'UPDATE sessions SET {set_clause} WHERE id=?', values)
        conn.commit()
        conn.close()
    
    def create_scan(self, scan_data: Dict) -> str:
        """Create new scan record"""
        scan_id = str(uuid.uuid4())[:8]
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scans (id, session_id, target, type, status, started_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            scan_id,
            scan_data.get('session_id'),
            scan_data.get('target'),
            scan_data.get('type'),
            scan_data.get('status', 'running'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return scan_id
    
    def update_scan(self, scan_id: str, updates: Dict):
        """Update scan record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if 'results' in updates:
            updates['results'] = json.dumps(updates['results'])
        
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [scan_id]
        
        cursor.execute(f'UPDATE scans SET {set_clause} WHERE id=?', values)
        conn.commit()
        conn.close()
    
    def get_scan(self, scan_id: str) -> Optional[Dict]:
        """Get scan by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scans WHERE id=?', (scan_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'session_id': row[1],
                'target': row[2],
                'type': row[3],
                'status': row[4],
                'results': json.loads(row[5]) if row[5] else None,
                'started_at': row[6],
                'completed_at': row[7]
            }
        return None
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get session scan history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scans WHERE session_id=? ORDER BY created_at DESC', (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'target': row[2],
                'type': row[3],
                'status': row[4],
                'started_at': row[6]
            }
            for row in rows
        ]
    
    def log_module_execution(self, execution_data: Dict):
        """Log module execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO module_executions (session_id, module, target, result, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            execution_data.get('session_id'),
            execution_data.get('module'),
            execution_data.get('target'),
            json.dumps(execution_data.get('result', {})),
            execution_data.get('timestamp', datetime.now().isoformat())
        ))
        
        conn.commit()
        conn.close()
    
    def save_payload(self, payload_data: Dict) -> str:
        """Save payload to database"""
        payload_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO payloads (id, name, category, payload_code, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            payload_id,
            payload_data.get('name'),
            payload_data.get('category'),
            payload_data.get('payload_code'),
            payload_data.get('description'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return payload_id
    
    def get_payloads(self, category: Optional[str] = None) -> List[Dict]:
        """Get payloads by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT * FROM payloads WHERE category=?', (category,))
        else:
            cursor.execute('SELECT * FROM payloads')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'payload_code': row[3],
                'description': row[4],
                'created_at': row[5]
            }
            for row in rows
        ]
