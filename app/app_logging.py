"""
Custom logging module for the Barcode Generator API.

This module provides a custom logger with color support, class name detection,
and request/response logging capabilities.
"""

import sys
import re
import os
import inspect
from datetime import datetime
from flask import request

class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Special colors
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    
    # Custom colors
    NUMBER = '\033[93m'  # Yellow for numbers
    SIZE = '\033[96m'    # Cyan for sizes
    DURATION = '\033[95m' # Magenta for durations
    GRAY = '\033[90m'    # Gray for less important info
    BG_GRAY = '\033[100m' # Gray background for extra data

def colorize(message, level="INFO"):
    """
    Add color to log messages based on log level.
    
    Args:
        message: The log message to colorize
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        str: Colorized message
    """
    color_map = {
        'DEBUG': Colors.BLUE,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD
    }
    color = color_map.get(level.upper(), Colors.RESET)
    
    # Colorize HTTP status codes
    if isinstance(message, str):
        # Color HTTP status codes
        if '200' in message:
            message = message.replace('200', f'{Colors.GREEN}200{color}')
        elif '201' in message:
            message = message.replace('201', f'{Colors.GREEN}201{color}')
        elif '204' in message:
            message = message.replace('204', f'{Colors.GREEN}204{color}')
        elif '304' in message:
            message = message.replace('304', f'{Colors.BLUE}304{color}')
        elif '400' in message or '404' in message or '403' in message:
            message = re.sub(r'(4\d{2})', f'{Colors.YELLOW}\\1{color}', message)
        elif '500' in message or '502' in message or '503' in message:
            message = re.sub(r'(5\d{2})', f'{Colors.RED}\\1{color}', message)
        
        # Color durations (e.g., "in 1.23ms")
        message = re.sub(
            r'(\d+\.\d+)(ms|s|µs)', 
            lambda m: f'{Colors.DURATION}{m.group(1)}{m.group(2)}{color}', 
            message
        )
        
        # Color sizes (e.g., "1.5KB")
        message = re.sub(
            r'(\d+(\.\d+)?[KMG]?B)', 
            lambda m: f'{Colors.SIZE}{m.group(1)}{color}', 
            message
        )
    
    # Color numbers differently from text
    def colorize_number(match):
        num = match.group(0)
        # Skip if it's part of a size or duration (already colored)
        if (match.start() > 0 and message[match.start()-1] in ' (') or \
           (match.end() < len(message) and message[match.end()] == 'b'):
            return f"{Colors.SIZE}{num}{Colors.RESET}{color}"
        # Default number coloring
        return f"{Colors.NUMBER}{num}{Colors.RESET}{color}"
    
    # Apply number coloring
    message = re.sub(r'\b\d+(\.\d+)?\b', colorize_number, message)
    
    return f"{color}{message}{Colors.RESET}"

def get_client_ip():
    """Get the client's IP address, handling proxy headers."""
    if request:
        return request.headers.get('X-Forwarded-For', request.remote_addr)
    return '0.0.0.0'

def log(message, level="INFO", **kwargs):
    """
    Custom logging function with color support.
    
    Args:
        message: The log message
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        **kwargs: Additional arguments (extra is used for structured logging)
    """
    # Remove 'extra' from kwargs to prevent passing it to print()
    extra = kwargs.pop('extra', {})
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client_ip = get_client_ip()
    
    # Format the log message with colors
    log_parts = [
        f"{Colors.BLUE}{timestamp}{Colors.RESET}",
        f"{Colors.HEADER}{client_ip:15}{Colors.RESET}",
        colorize(level, f"{level:8}"),
        message
    ]
    
    # Print to stderr for errors, stdout for everything else
    output = sys.stderr if level in ('ERROR', 'CRITICAL') else sys.stdout
    
    # Print the formatted message
    print(" ".join(log_parts), file=output, **kwargs)
    
    # # If we have extra data and not in a request context (to avoid recursion)
    # if extra and 'request' not in extra:
    #     import json
    #     import textwrap
    #     # Convert extra data to pretty-printed JSON
    #     extra_json = json.dumps(extra, indent=2, default=str)
    #     # Indent and color the extra data
    #     formatted_extra = textwrap.indent(extra_json, '  ')
    #     print(f"{Colors.BG_GRAY}{formatted_extra}{Colors.RESET}", file=output)
    #
    # Flush to ensure logs appear immediately
    output.flush()

class SimpleLogger:
    """A simple logger that includes class names in log messages."""
    
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__
        
    def _get_caller_class(self):
        try:
            # Get the current frame and go up the call stack
            frame = inspect.currentframe()
            
            # Skip the logger's internal frames
            # 1. _get_caller_class (current)
            # 2. _log_with_class
            # 3. debug/info/warning/error/critical
            # 4. The actual caller we're interested in
            for _ in range(4):
                if not frame:
                    return self.name or 'Unknown'
                frame = frame.f_back
            
            if not frame:
                return self.name or 'Unknown'
            
            # Get the frame info for the calling code
            frame_info = inspect.getframeinfo(frame)
            
            # Get the module name from the filename
            module_name = os.path.splitext(os.path.basename(frame_info.filename))[0]
            
            # Try to get the class name from the frame's code
            code = frame.f_code
            if code.co_name == '<module>':
                # Module-level code
                return module_name or 'Unknown'
                
            # Try to get the class name from the code's qualified name
            if hasattr(code, 'co_qualname'):
                qualname = code.co_qualname
                # Check if it's a method (contains '.')
                if '.' in qualname:
                    return qualname.split('.')[-2]  # Return the class name
                return qualname
                
            # Try to get 'self' from the frame's locals
            if 'self' in frame.f_locals:
                self_obj = frame.f_locals['self']
                if hasattr(self_obj, '__class__'):
                    return self_obj.__class__.__name__
            
            # Try to find a class in the frame's locals
            for name, obj in frame.f_locals.items():
                if obj is self:
                    continue
                if hasattr(obj, '__class__') and not isinstance(obj, type):
                    return obj.__class__.__name__
                if isinstance(obj, type):
                    return obj.__name__
            
            # Try to parse the class name from the code
            if hasattr(frame, 'f_back') and frame.f_back:
                # Look for class definition in the code
                lines = inspect.getsourcelines(frame.f_back)[0]
                for line in lines[:frame.f_back.f_lineno]:
                    if 'class ' in line and ':' in line:
                        class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                        if class_name:
                            return class_name
            
            return module_name or 'Unknown'
            
        except Exception as e:
            # If anything goes wrong, return a default
            return self.name or 'Unknown'
            
        finally:
            # Clean up frame references to avoid reference cycles
            if 'frame' in locals() and frame:
                del frame
    
    def _log_with_class(self, level, message, *args, **kwargs):
        class_name = self._get_caller_class()
        log(f"[{class_name}] {message}", level, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        self._log_with_class("DEBUG", message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        self._log_with_class("INFO", message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        self._log_with_class("WARNING", message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        self._log_with_class("ERROR", message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        self._log_with_class("CRITICAL", message, *args, **kwargs)

# Create a default logger instance
logger = SimpleLogger("BarcodeApp")
