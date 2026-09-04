"""
PayForge Module Loader System
Dynamically loads and manages security testing modules
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Any
from utils.logger import Logger

class ModuleMetadata:
    """Module metadata container"""
    def __init__(self, name, version, author, description, category, dependencies, requires_auth, risk_level):
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.category = category
        self.dependencies = dependencies
        self.requires_auth = requires_auth
        self.risk_level = risk_level  # low, medium, high, critical

class ModuleLoader:
    """Dynamically load and execute security modules"""
    
    def __init__(self):
        self.logger = Logger("ModuleLoader")
        self.modules = {}
        self.metadata = {}
        self.module_dir = Path(__file__).parent.parent / "payloads"
        self.loaded_modules = set()
        
    def discover_modules(self) -> List[str]:
        """Discover all available modules"""
        modules = []
        
        if not self.module_dir.exists():
            self.logger.warning(f"Module directory not found: {self.module_dir}")
            return modules
        
        for module_file in self.module_dir.glob("*.py"):
            if not module_file.name.startswith("_"):
                module_name = module_file.stem
                modules.append(module_name)
        
        self.logger.info(f"Discovered {len(modules)} modules")
        return modules
    
    def load_module(self, module_name: str) -> bool:
        """Load a specific module"""
        try:
            if module_name in self.loaded_modules:
                self.logger.info(f"Module already loaded: {module_name}")
                return True
            
            module_path = self.module_dir / f"{module_name}.py"
            
            if not module_path.exists():
                self.logger.error(f"Module not found: {module_name}")
                return False
            
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract metadata
            if hasattr(module, 'MODULE_METADATA'):
                meta = module.MODULE_METADATA
                self.metadata[module_name] = ModuleMetadata(
                    meta.get('name'),
                    meta.get('version'),
                    meta.get('author'),
                    meta.get('description'),
                    meta.get('category'),
                    meta.get('dependencies', []),
                    meta.get('requires_auth', False),
                    meta.get('risk_level', 'medium')
                )
            
            self.modules[module_name] = module
            self.loaded_modules.add(module_name)
            
            self.logger.success(f"Loaded module: {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load module {module_name}: {str(e)}")
            return False
    
    def load_all_modules(self) -> int:
        """Load all available modules"""
        modules = self.discover_modules()
        loaded_count = 0
        
        for module_name in modules:
            if self.load_module(module_name):
                loaded_count += 1
        
        self.logger.info(f"Loaded {loaded_count}/{len(modules)} modules")
        return loaded_count
    
    def execute_module(self, module_name: str, target: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a specific module"""
        try:
            if module_name not in self.modules:
                self.load_module(module_name)
            
            if module_name not in self.modules:
                return {"success": False, "error": f"Module not found: {module_name}"}
            
            module = self.modules[module_name]
            
            if not hasattr(module, 'execute'):
                return {"success": False, "error": f"Module has no execute function"}
            
            self.logger.info(f"Executing module: {module_name} on {target}")
            result = module.execute(target, options or {})
            
            return {"success": True, "data": result, "module": module_name}
            
        except Exception as e:
            self.logger.error(f"Module execution failed: {str(e)}")
            return {"success": False, "error": str(e), "module": module_name}
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """List all available modules with metadata"""
        modules_list = []
        
        for module_name in self.discover_modules():
            metadata = self.metadata.get(module_name)
            
            module_info = {
                "name": module_name,
                "loaded": module_name in self.loaded_modules
            }
            
            if metadata:
                module_info.update({
                    "version": metadata.version,
                    "author": metadata.author,
                    "description": metadata.description,
                    "category": metadata.category,
                    "risk_level": metadata.risk_level,
                    "requires_auth": metadata.requires_auth
                })
            
            modules_list.append(module_info)
        
        return modules_list
    
    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """Get detailed information about a module"""
        if module_name not in self.metadata:
            self.load_module(module_name)
        
        if module_name not in self.metadata:
            return {"error": f"Module not found: {module_name}"}
        
        metadata = self.metadata[module_name]
        return {
            "name": module_name,
            "version": metadata.version,
            "author": metadata.author,
            "description": metadata.description,
            "category": metadata.category,
            "dependencies": metadata.dependencies,
            "requires_auth": metadata.requires_auth,
            "risk_level": metadata.risk_level
        }
    
    def validate_dependencies(self, module_name: str):
        """Check if all dependencies are installed"""
        if module_name not in self.metadata:
            return False, ["Module not found"]
        
        metadata = self.metadata[module_name]
        missing = []
        
        for dep in metadata.dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        return len(missing) == 0, missing
    
    def unload_module(self, module_name: str) -> bool:
        """Unload a module from memory"""
        if module_name in self.modules:
            del self.modules[module_name]
            self.loaded_modules.discard(module_name)
            self.logger.info(f"Unloaded module: {module_name}")
            return True
        return False
    
    def get_modules_by_category(self, category: str) -> List[str]:
        """Get all modules in a specific category"""
        modules = []
        for module_name, metadata in self.metadata.items():
            if metadata.category.lower() == category.lower():
                modules.append(module_name)
        return modules
    
    def export_modules_manifest(self) -> Dict[str, Any]:
        """Export all modules as manifest"""
        manifest = {
            "total_modules": len(self.discover_modules()),
            "loaded_modules": len(self.loaded_modules),
            "modules": self.list_modules()
        }
        return manifest
