# Discover all modules
loader = ModuleLoader()
modules = loader.discover_modules()

# Load a specific module
loader.load_module("nmap_scanner")

# Execute a module
result = loader.execute_module("nmap_scanner", "192.168.1.1")

# List all modules with metadata
all_modules = loader.list_modules()

# Get modules by category
recon_modules = loader.get_modules_by_category("reconnaissance")

# Validate dependencies
is_valid, missing = loader.validate_dependencies("module_name")
