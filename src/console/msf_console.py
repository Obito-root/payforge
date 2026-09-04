"""
PayForge Interactive Console
Metasploit-like console interface for penetration testing
"""

import cmd
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from modules.module_loader import ModuleLoader
from database.db_handler import DatabaseHandler
from utils.logger import Logger

class PayForgeConsole(cmd.Cmd):
    """Interactive console for PayForge framework"""
    
    intro = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              PayForge Interactive Security Console               ║
║                     Version 1.0.0                                ║
║                                                                  ║
║  Type 'help' for available commands                             ║
║  Type 'exit' or 'quit' to exit                                  ║
║                                                                  ║
║  ⚠️  AUTHORIZED TESTING ONLY - Ethical Use Required             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    
    prompt = "payforge> "
    
    def __init__(self):
        super().__init__()
        self.logger = Logger("PayForgeConsole")
        self.module_loader = ModuleLoader()
        self.db = DatabaseHandler()
        self.current_target = None
        self.current_module = None
        self.module_options = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Load all modules on startup
        self.module_loader.load_all_modules()
    
    def do_help(self, arg):
        """Show help information"""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║              PayForge Console Commands                         ║
╚════════════════════════════════════════════════════════════════╝

TARGET MANAGEMENT:
  set-target <target>       Set target IP/Domain
  show-target              Show current target
  clear-target             Clear current target

MODULE MANAGEMENT:
  modules                  List all available modules
  search <keyword>         Search modules
  use <module>            Load a specific module
  info <module>           Show module information
  options                 Show module options
  set <option> <value>    Set module option
  check                   Check if target is vulnerable
  run                     Execute current module
  exploit                 Execute and show results
  
DATABASE:
  show-sessions           Show all sessions
  show-results            Show scan results
  save-result <name>      Save current result

UTILITY:
  background              Background current session
  sessions                List active sessions
  history                 Show command history
  clear                   Clear screen
  banner                  Show banner

SYSTEM:
  exit / quit             Exit PayForge
  help                    Show this help message

EXAMPLES:
  payforge> set-target 192.168.1.1
  payforge> search nmap
  payforge> use nmap_scanner
  payforge> set threads 20
  payforge> run
  payforge> exploit
        """
        print(help_text)
    
    def do_set_target(self, arg):
        """Set the target IP or domain"""
        if not arg:
            print("[-] Usage: set-target <IP/Domain>")
            return
        
        self.current_target = arg
        self.logger.success(f"Target set to: {self.current_target}")
    
    def do_show_target(self, arg):
        """Show current target"""
        if self.current_target:
            print(f"[+] Current Target: {self.current_target}")
        else:
            print("[-] No target set. Use 'set-target <target>'")
    
    def do_clear_target(self, arg):
        """Clear current target"""
        self.current_target = None
        self.logger.info("Target cleared")
    
    def do_modules(self, arg):
        """List all available modules"""
        modules = self.module_loader.list_modules()
        
        if not modules:
            print("[-] No modules found")
            return
        
        print("\n" + "="*80)
        print(f"{'Module':<30} {'Category':<20} {'Risk':<10} {'Status':<10}")
        print("="*80)
        
        for mod in modules:
            status = "[LOADED]" if mod.get('loaded') else "[UNLOADED]"
            category = mod.get('category', 'unknown')
            risk = mod.get('risk_level', 'medium')
            print(f"{mod['name']:<30} {category:<20} {risk:<10} {status:<10}")
        
        print("="*80)
        print(f"\nTotal Modules: {len(modules)}")
    
    def do_search(self, arg):
        """Search for modules"""
        if not arg:
            print("[-] Usage: search <keyword>")
            return
        
        modules = self.module_loader.list_modules()
        keyword = arg.lower()
        results = []
        
        for mod in modules:
            if keyword in mod['name'].lower() or keyword in mod.get('description', '').lower():
                results.append(mod)
        
        if not results:
            print(f"[-] No modules found for '{keyword}'")
            return
        
        print(f"\n[+] Found {len(results)} module(s):\n")
        for mod in results:
            print(f"  {mod['name']:<40} - {mod.get('description', 'N/A')}")
    
    def do_use(self, arg):
        """Load a specific module"""
        if not arg:
            print("[-] Usage: use <module_name>")
            return
        
        if self.module_loader.load_module(arg):
            self.current_module = arg
            self.module_options = {}
            self.logger.success(f"Module loaded: {arg}")
            print(f"\n[+] Type 'info' to see module details")
            print(f"[+] Type 'options' to see available options")
        else:
            self.logger.error(f"Failed to load module: {arg}")
    
    def do_info(self, arg):
        """Show module information"""
        module_name = arg if arg else self.current_module
        
        if not module_name:
            print("[-] Please specify a module or use a module first")
            return
        
        info = self.module_loader.get_module_info(module_name)
        
        if 'error' in info:
            print(f"[-] {info['error']}")
            return
        
        print(f"\n{'='*60}")
        print(f"Module: {info['name']}")
        print(f"{'='*60}")
        print(f"Version:      {info['version']}")
        print(f"Author:       {info['author']}")
        print(f"Category:     {info['category']}")
        print(f"Risk Level:   {info['risk_level']}")
        print(f"Requires Auth: {info['requires_auth']}")
        print(f"\nDescription:")
        print(f"  {info['description']}")
        print(f"\nDependencies: {', '.join(info['dependencies'])}")
        print(f"{'='*60}\n")
    
    def do_options(self, arg):
        """Show module options"""
        if not self.current_module:
            print("[-] No module loaded. Use 'use <module>'")
            return
        
        print(f"\n[+] Options for {self.current_module}:\n")
        
        if not self.module_options:
            print("  No options set")
        else:
            for key, value in self.module_options.items():
                print(f"  {key:<20} => {value}")
        
        print()
    
    def do_set(self, arg):
        """Set module option"""
        parts = arg.split(maxsplit=1)
        
        if len(parts) != 2:
            print("[-] Usage: set <option> <value>")
            return
        
        option, value = parts
        self.module_options[option] = value
        self.logger.success(f"Set {option} = {value}")
    
    def do_run(self, arg):
        """Execute current module"""
        if not self.current_module:
            print("[-] No module loaded. Use 'use <module>'")
            return
        
        if not self.current_target:
            print("[-] No target set. Use 'set-target <target>'")
            return
        
        self.logger.info(f"Executing {self.current_module} on {self.current_target}...")
        result = self.module_loader.execute_module(
            self.current_module,
            self.current_target,
            self.module_options
        )
        
        if result['success']:
            self.logger.success(f"Module executed successfully")
            print(json.dumps(result['data'], indent=2))
        else:
            self.logger.error(f"Module execution failed: {result['error']}")
    
    def do_exploit(self, arg):
        """Execute exploit and show detailed results"""
        if not self.current_module:
            print("[-] No module loaded")
            return
        
        if not self.current_target:
            print("[-] No target set")
            return
        
        print(f"\n[*] Exploiting {self.current_target} with {self.current_module}...\n")
        result = self.module_loader.execute_module(
            self.current_module,
            self.current_target,
            self.module_options
        )
        
        # Save to database
        exploit_record = {
            "session_id": self.session_id,
            "module": self.current_module,
            "target": self.current_target,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        self.db.save_exploit_result(exploit_record)
        
        if result['success']:
            print(json.dumps(result['data'], indent=2))
            self.logger.success("Exploit completed successfully")
        else:
            self.logger.error(f"Exploit failed: {result['error']}")
    
    def do_show_sessions(self, arg):
        """Show all sessions"""
        sessions = self.db.get_all_sessions()
        
        if not sessions:
            print("[-] No sessions found")
            return
        
        print("\n" + "="*80)
        print(f"{'Session ID':<20} {'Module':<25} {'Target':<25}")
        print("="*80)
        
        for session in sessions:
            print(f"{session['session_id']:<20} {session['module']:<25} {session['target']:<25}")
        
        print("="*80)
    
    def do_exit(self, arg):
        """Exit PayForge"""
        print("\n[*] Exiting PayForge...")
        return True
    
    def do_quit(self, arg):
        """Exit PayForge"""
        return self.do_exit(arg)
    
    def do_banner(self, arg):
        """Show banner"""
        print(self.intro)
    
    def do_clear(self, arg):
        """Clear screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
