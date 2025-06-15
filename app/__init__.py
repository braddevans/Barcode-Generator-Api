import os
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

# Disable Flask's default logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Import our custom logging setup
from .app_logging import logger, SimpleLogger, Colors, log, get_client_ip

# Create a module-level logger
logger = SimpleLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    import logging
    
    # Disable Flask's default request logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('werkzeug').disabled = True
    
    # Completely disable ASGI/UVICORN logging
    logging.getLogger('uvicorn').handlers = []
    logging.getLogger('uvicorn').propagate = False
    logging.getLogger('uvicorn.access').handlers = []
    logging.getLogger('uvicorn.access').propagate = False
    logging.getLogger('uvicorn.error').handlers = []
    logging.getLogger('uvicorn.error').propagate = False
    
    # Disable Flask's default logger
    app.logger.disabled = True
    
    # Disable other noisy loggers
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('hpack').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    # Import and register blueprints
    from .blueprints import barcode

    # Register blueprints
    app.register_blueprint(barcode.bp, url_prefix='/')
    
    # Add request logging
    @app.before_request
    def log_request():
        request.start_time = time.time()
        # Skip logging for static files
        if request.path.startswith('/static/'):
            return
            
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        # Color the HTTP method and path
        method_color = {
            'GET': Colors.GREEN,
            'POST': Colors.BLUE,
            'PUT': Colors.YELLOW,
            'DELETE': Colors.RED,
            'PATCH': Colors.CYAN
        }.get(request.method, Colors.RESET)
        
        logger.info(
            f"→ {method_color}{request.method}{Colors.RESET} "
            f"{Colors.BOLD}{request.path}{Colors.RESET} "
            f"from {Colors.HEADER}{client_ip}{Colors.RESET}"
        )

    @app.after_request
    def log_response(response):
        # Skip logging for static files
        if request.path.startswith('/static/'):
            return response
            
        duration = (time.time() - request.start_time) * 1000
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Color code the status
        status_code = response.status_code
        if 200 <= status_code < 300:
            status_color = Colors.GREEN
        elif 300 <= status_code < 400:
            status_color = Colors.BLUE
        elif 400 <= status_code < 500:
            status_color = Colors.YELLOW
        else:
            status_color = Colors.RED
        
        # Get response size in appropriate units
        size = response.content_length or 0
        if size < 1024:
            size_str = f"{size}b"
        elif size < 1024 * 1024:
            size_str = f"{size/1024:.1f}KB"
        else:
            size_str = f"{size/(1024*1024):.1f}MB"
            
        # Format the duration with appropriate units
        if duration < 1:
            duration_str = f"{duration*1000:.0f}µs"
        elif duration < 1000:
            duration_str = f"{duration:.2f}ms"
        else:
            duration_str = f"{duration/1000:.2f}s"
            
        logger.info(
            f"← {Colors.BOLD}{request.method} {request.path}{Colors.RESET} "
            f"{status_color}{status_code}{Colors.RESET} in {Colors.DURATION}{duration_str}{Colors.RESET} "
            f"({Colors.SIZE}{size_str}{Colors.RESET})",
            extra={
                'method': request.method,
                'path': request.path,
                'status': status_code,
                'duration': duration_str,
                'ip': client_ip,
                'response_size': size
            }
        )
        return response

    # Root route with HTML response
    @app.route('/')
    def index():
        routes = [
            {
                "method": "GET",
                "path": "/",
                "description": "API status and documentation"
            },
            {
                "method": "GET",
                "path": "/barcode?data=<data>&type=<type>&raw=<true/false>",
                "description": "Generate a barcode image. Types: code128, ean8, ean13, etc."
            }
        ]

        # Return JSON response
        return {
            "status": "success",
            "message": "Barcode Generator API is running!",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": routes
        }

    return app
