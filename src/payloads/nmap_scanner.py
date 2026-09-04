"""
PayForge Nmap Scanner Module
Network reconnaissance and port scanning
"""

import subprocess
import json
from typing import Dict, Any

MODULE_METADATA = {
    'name': 'Nmap Port Scanner',
    'version': '1.0.0',
    'author': 'PayForge Team',
    'description': 'Advanced network scanning with Nmap for service discovery',
    'category': 'reconnaissance',
    'dependencies': ['nmap'],
    'requires_auth': True,
    'risk_level': 'low'
}

def execute(target: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Nmap scan on target
    
    Args:
        target: IP address or domain to scan
        options: Dictionary of options
            - ports: Port range (default: 1-1000)
            - scan_type: Type of scan (default: sS)
            - timeout: Scan timeout (default: 300)
    
    Returns:
        Dictionary with scan results
    """
    
    try:
        ports = options.get('ports', '1-1000')
        scan_type = options.get('scan_type', 'sS')
        timeout = options.get('timeout', '300')
        
        # Build Nmap command
        cmd = [
            'nmap',
            f'-p{ports}',
            f'-{scan_type}',
            '--open',
            '-sV',
            '--script=banner',
            target
        ]
        
        # Execute Nmap
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=int(timeout)
        )
        
        if result.returncode == 0:
            open_ports = parse_nmap_output(result.stdout)
            
            return {
                'status': 'success',
                'target': target,
                'scan_type': 'nmap',
                'open_ports': open_ports,
                'raw_output': result.stdout,
                'services_found': len(open_ports)
            }
        else:
            return {
                'status': 'failed',
                'error': result.stderr,
                'target': target
            }
    
    except subprocess.TimeoutExpired:
        return {
            'status': 'timeout',
            'error': 'Nmap scan timed out',
            'target': target
        }
    
    except FileNotFoundError:
        return {
            'status': 'error',
            'error': 'Nmap not installed. Install with: sudo apt-get install nmap',
            'target': target
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'target': target
        }

def parse_nmap_output(output: str) -> list:
    """Parse Nmap output and extract open ports"""
    open_ports = []
    
    for line in output.split('\n'):
        if '/tcp' in line and 'open' in line:
            parts = line.strip().split()
            if len(parts) >= 3:
                port_info = parts[0].split('/')
                if len(port_info) >= 2:
                    open_ports.append({
                        'port': int(port_info[0]),
                        'protocol': port_info[1],
                        'state': parts[1],
                        'service': ' '.join(parts[2:]) if len(parts) > 2 else 'unknown'
                    })
    
    return open_ports
