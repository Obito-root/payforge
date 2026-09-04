"""
PayForge Core Framework
Main initialization and framework orchestration
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import core modules
from utils.logger import Logger
from database.db_handler import DatabaseHandler
from auth.electron_auth import ElectronAuth
from console.cli import PayForgeConsole
from modules.scanner import SecurityScanner
from modules.executor import ModuleExecutor

class PayForgeCore:
    """Main PayForge Framework Core"""
    
    def __init__(self):
        """Initialize PayForge core components"""
        self.logger = Logger("PayForgeCore")
        self.db = DatabaseHandler()
        self.auth = ElectronAuth()
        self.console = PayForgeConsole()
        self.scanner = SecurityScanner()
        self.executor = ModuleExecutor()
        
        # Configuration
        self.config = self._load_config()
        self.session_id = None
        self.user_data = None
        self.active_modules = []
        self.scan_results = {}
        
        self.logger.info("PayForge Core initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from files"""
        config_path = Path("/opt/payforge/config/payforge.conf")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
                return self._default_config()
        
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "version": "1.0.0",
            "framework": "PayForge",
            "edition": "Professional",
            "debug": False,
            "log_level": "INFO",
            "database": {
                "type": "sqlite",
                "path": "/opt/payforge/database/payforge.db"
            },
            "modules": {
                "auto_load": True,
                "path": "/opt/payforge/modules"
            },
            "output": {
                "reports": "/opt/payforge/reports",
                "logs": "/opt/payforge/logs"
            },
            "security": {
                "encryption": True,
                "auth_required": True,
                "session_timeout": 3600
            }
        }
    
    def create_session(self, user_data: Dict) -> str:
        """Create new framework session"""
        self.user_data = user_data
        self.session_id = self.db.create_session({
            "username": user_data.get('username'),
            "email": user_data.get('email'),
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        })
        
        self.logger.success(f"Session created: {self.session_id}")
        return self.session_id
    
    def load_module(self, module_name: str) -> bool:
        """Load a security module"""
        try:
            self.logger.info(f"Loading module: {module_name}")
            module = self.executor.load_module(module_name)
            
            if module:
                self.active_modules.append(module_name)
                self.logger.success(f"Module loaded: {module_name}")
                return True
            else:
                self.logger.error(f"Failed to load module: {module_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading module {module_name}: {e}")
            return False
    
    def get_available_modules(self) -> List[str]:
        """Get list of available modules"""
        return self.executor.get_available_modules()
    
    def start_scan(self, target: str, scan_type: str = "full", 
                  modules: Optional[List[str]] = None) -> Dict:
        """Start security scan"""
        scan_id = self.db.create_scan({
            "session_id": self.session_id,
            "target": target,
            "type": scan_type,
            "modules": modules or [],
            "status": "running",
            "started_at": datetime.now().isoformat()
        })
        
        self.logger.info(f"Scan {scan_id} started on {target}")
        
        try:
            # Execute scan
            results = self.scanner.run_scan(target, scan_type, modules)
            
            # Store results
            self.scan_results[scan_id] = results
            self.db.update_scan(scan_id, {
                "status": "completed",
                "results": results,
                "completed_at": datetime.now().isoformat()
            })
            
            self.logger.success(f"Scan completed: {scan_id}")
            return {
                "scan_id": scan_id,
                "status": "completed",
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            self.db.update_scan(scan_id, {"status": "failed", "error": str(e)})
            return {"scan_id": scan_id, "status": "failed", "error": str(e)}
    
    def execute_module(self, module_name: str, target: str, 
                      options: Optional[Dict] = None) -> Dict:
        """Execute specific module"""
        self.logger.info(f"Executing module: {module_name} on {target}")
        
        try:
            result = self.executor.execute_module(module_name, target, options or {})
            
            # Log execution
            self.db.log_module_execution({
                "session_id": self.session_id,
                "module": module_name,
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Module execution failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_report(self, scan_id: str, format_type: str = "json") -> str:
        """Generate scan report"""
        self.logger.info(f"Generating {format_type} report for scan {scan_id}")
        
        try:
            scan_data = self.db.get_scan(scan_id)
            
            if not scan_data:
                self.logger.error(f"Scan not found: {scan_id}")
                return None
            
            # Generate report based on format
            if format_type == "json":
                report = self._generate_json_report(scan_data)
            elif format_type == "html":
                report = self._generate_html_report(scan_data)
            elif format_type == "pdf":
                report = self._generate_pdf_report(scan_data)
            else:
                report = self._generate_json_report(scan_data)
            
            # Save report
            report_path = self._save_report(scan_id, report, format_type)
            self.logger.success(f"Report generated: {report_path}")
            
            return report_path
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return None
    
    def _generate_json_report(self, scan_data: Dict) -> str:
        """Generate JSON report"""
        report = {
            "framework": "PayForge",
            "version": self.config.get("version"),
            "scan": scan_data,
            "generated_at": datetime.now().isoformat(),
            "generated_by": self.user_data.get('username') if self.user_data else "system"
        }
        return json.dumps(report, indent=2)
    
    def _generate_html_report(self, scan_data: Dict) -> str:
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>PayForge Security Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .scan-info {{ background: #ecf0f1; padding: 10px; margin: 10px 0; }}
        .results {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PayForge Security Report</h1>
        <p>Generated: {datetime.now().isoformat()}</p>
    </div>
    <div class="scan-info">
        <h2>Scan Information</h2>
        <p><strong>Target:</strong> {scan_data.get('target')}</p>
        <p><strong>Type:</strong> {scan_data.get('type')}</p>
        <p><strong>Status:</strong> {scan_data.get('status')}</p>
    </div>
    <div class="results">
        <h2>Results</h2>
        <pre>{json.dumps(scan_data.get('results', {}), indent=2)}</pre>
    </div>
</body>
</html>
        """
        return html
    
    def _generate_pdf_report(self, scan_data: Dict) -> str:
        """Generate PDF report (placeholder)"""
        return self._generate_html_report(scan_data)
    
    def _save_report(self, scan_id: str, report: str, format_type: str) -> str:
        """Save report to file"""
        reports_dir = Path(self.config['output']['reports'])
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        extension = format_type if format_type != "json" else "json"
        report_path = reports_dir / f"report_{scan_id}.{extension}"
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        return str(report_path)
    
    def get_session_history(self) -> List[Dict]:
        """Get current session history"""
        if not self.session_id:
            return []
        
        return self.db.get_session_history(self.session_id)
    
    def close_session(self):
        """Close current session"""
        if self.session_id:
            self.db.update_session(self.session_id, {"status": "closed"})
            self.logger.info(f"Session closed: {self.session_id}")
            self.session_id = None
    
    def get_framework_info(self) -> Dict:
        """Get framework information"""
        return {
            "name": "PayForge",
            "version": self.config.get("version"),
            "edition": self.config.get("edition"),
            "modules": self.get_available_modules(),
            "active_modules": self.active_modules,
            "session_id": self.session_id,
            "user": self.user_data.get('username') if self.user_data else None
        }

# Global instance
_core_instance = None

def get_core() -> PayForgeCore:
    """Get or create core instance"""
    global _core_instance
    if _core_instance is None:
        _core_instance = PayForgeCore()
    return _core_instance

if __name__ == "__main__":
    core = get_core()
    print(core.get_framework_info())
