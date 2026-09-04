"""
PayForge Logging System
Colorized logging with Rich
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console

class Logger:
    """Custom logger with Rich formatting"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        self.console = Console()
        
        # Create logs directory
        log_dir = Path('/opt/payforge/logs')
        log_dir.mkdir(exist_ok=True, parents=True)
        self.log_file = log_dir / 'payforge.log'
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging handlers"""
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Set logger level
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler with Rich
        console_handler = RichHandler(
            console=self.console,
            rich_tracebacks=True,
            show_time=True,
            show_level=True,
            show_path=False
        )
        console_handler.setLevel(logging.INFO)
        
        # File handler
        try:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"[!] Error setting up file logging: {str(e)}")
        
        # Add console handler
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(f"⚠️  {message}")
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(f"❌ {message}")
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(f"🔴 {message}")
    
    def success(self, message: str):
        """Log success message"""
        self.console.print(f"[green]✓ {message}[/green]")
        self.logger.info(f"✓ {message}")
        
