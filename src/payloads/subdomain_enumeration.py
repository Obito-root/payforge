"""
PayForge Subdomain Enumeration Module
Discovers subdomains and related hosts
"""

import socket
import dns.resolver
from typing import Dict, Any, List

MODULE_METADATA = {
    'name': 'Subdomain Enumerator',
    'version': '1.0.0',
    'author': 'PayForge Team',
    'description': 'Discovers subdomains using wordlist and DNS queries',
    'category': 'reconnaissance',
    'dependencies': ['dnspython'],
    'requires_auth': True,
    'risk_level': 'low'
}

def execute(target: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enumerate subdomains for target domain
    
    Args:
        target: Domain name to enumerate
        options: Dictionary of options
            - wordlist_size: Size of wordlist (small, medium, large)
            - threads: Number of threads (default: 10)
            - timeout: DNS timeout (default: 5)
    
    Returns:
        Dictionary with discovered subdomains
    """
    
    try:
        wordlist_size = options.get('wordlist_size', 'medium')
        timeout = int(options.get('timeout', 5))
        
        # Get appropriate wordlist based on size
        wordlist = get_wordlist(wordlist_size)
        
        subdomains = []
        dns_records = []
        
        # Test each subdomain
        for subdomain in wordlist:
            full_domain = f"{subdomain}.{target}"
            
            try:
                # Try DNS resolution
                ip = socket.gethostbyname(full_domain)
                subdomains.append({
                    'subdomain': full_domain,
                    'ip': ip,
                    'method': 'DNS resolution'
                })
            
            except socket.gaierror:
                pass
            except:
                pass
        
        # Try DNS record enumeration
        try:
            for record_type in ['A', 'AAAA', 'MX', 'NS', 'TXT']:
                try:
                    records = dns.resolver.resolve(target, record_type)
                    for rdata in records:
                        dns_records.append({
                            'type': record_type,
                            'value': str(rdata)
                        })
                except:
                    pass
        except:
            pass
        
        return {
            'status': 'success',
            'target': target,
            'subdomains_found': len(subdomains),
            'subdomains': subdomains,
            'dns_records': dns_records,
            'total_checks': len(wordlist)
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'target': target
        }

def get_wordlist(size: str = 'medium') -> List[str]:
    """Get subdomain wordlist based on size"""
    
    small = ['www', 'mail', 'ftp', 'admin', 'test', 'dev']
    
    medium = small + [
        'api', 'cdn', 'staging', 'blog', 'shop', 'portal',
        'backup', 'database', 'app', 'mobile', 'webmail'
    ]
    
    large = medium + [
        'git', 'svn', 'jenkins', 'jira', 'confluence',
        'wiki', 'vpn', 'proxy', 'cloud', 'analytics',
        'crm', 'erp', 'mail2', 'old', 'legacy'
    ]
    
    return {
        'small': small,
        'medium': medium,
        'large': large
    }.get(size.lower(), medium)
