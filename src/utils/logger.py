"""
PayForge Logger
Colorized logging system for all framework components
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

class Logger:
    """Colorized logger for PayForge"""
    
    # Color codes
    COLORS = {
        'RESET': '\033[0m',
        'BOLD': '\033[1m',
        'DIM': '\033[2m',
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m'
    }
    
    def __init__(self, name: str, log_file: str = None):
        """Initialize logger"""
        self.name = name
        self.log_file = log_file or f"/opt/payforge/logs/{name}.log"
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _format(self, level: str, message: str, color: str) -> str:
        """Format log message with color"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{color}[{timestamp}] [{level}] {message}{self.COLORS['RESET']}"
    
    def info(self, message: str):
        """Log info message"""
        formatted = self._format("*", message, self.COLORS['CYAN'])
        print(formatted)
        self.logger.info(message)
    
    def success(self, message: str):
        """Log success message"""
        formatted = self._format("✓", message, self.COLORS['GREEN'])
        print(formatted)
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        formatted = self._format("!", message, self.COLORS['YELLOW'])
        print(formatted)
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        formatted = self._format("✗", message, self.COLORS['RED'])
        print(formatted)
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message"""
        formatted = self._format("DEBUG", message, self.COLORS['DIM'])
        print(formatted)
        self.logger.debug(message)
    
    def critical(self, message: str):
        """Log critical message"""
        formatted = self._format("CRITICAL", message, f"{self.COLORS['BOLD']}{self.COLORS['RED']}")
        print(formatted)
        self.logger.critical(message)

# Global logger instances
_loggers = {}

def get_logger(name: str) -> Logger:
    """Get or create logger"""
    if name not in _loggers:
        _loggers[name] = Logger(name)
    return _loggers[name]
