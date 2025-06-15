"""
ASGI entry point for the Barcode Generator API.

This module serves as the ASGI entry point for running the application
using Uvicorn or other ASGI servers.
"""
import os
import socket
import platform
from typing import List, Tuple
from tabulate import tabulate

from uvicorn.middleware.wsgi import WSGIMiddleware
from wsgi import Colors, get_config, print_banner
from app import create_app

# Create WSGI app and wrap it with ASGI middleware
wsgi_app = create_app()
app = WSGIMiddleware(wsgi_app)


def get_system_info(host: str, port: int, debug: bool) -> List[Tuple[str, str]]:
    """
    Collect system and server information for ASGI.
    
    Args:
        host: The host address the server is running on
        port: The port number the server is running on
        debug: Whether the app is in debug mode
        
    Returns:
        List of tuples containing (setting_name, setting_value)
    """
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    return [
        ("Server", f"{Colors.GREEN}Uvicorn ASGI{Colors.RESET}"),
        ("Environment", f"{Colors.GREEN if debug else Colors.YELLOW}"
                      f"{'Development' if debug else 'Production'}{Colors.RESET}"),
        ("Host", f"{host}:{port}"),
        ("Local URL", f"{Colors.BLUE}http://127.0.0.1:{port}{Colors.RESET}"),
        ("Network URL", f"{Colors.BLUE}http://{ip_address}:{port}{Colors.RESET}"),
        ("Hostname", hostname),
        ("IP Address", ip_address),
        ("OS", f"{platform.system()} {platform.release()}")
    ]


def print_system_info(host: str, port: int, debug: bool) -> None:
    """
    Print system and server information in a formatted table for ASGI.
    
    Args:
        host: The host address the server is running on
        port: The port number the server is running on
        debug: Whether the app is in debug mode
    """
    # Get system information
    table_data = get_system_info(host, port, debug)
    
    # Print the title
    print(f"\n{Colors.CYAN}{'=' * 60}")
    print(f"{'SYSTEM INFORMATION'.center(60)}")
    print(f"{'=' * 60}{Colors.RESET}")
    
    # Print the table with borders
    print(tabulate(
        table_data,
        headers=["Setting", "Value"],
        tablefmt="grid",
        stralign="left",
        showindex=False,
        maxcolwidths=[None, 50]  # Limit value column width
    ))
    
    # Print the bottom border
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")


def show_startup_message(host: str, port: int, debug: bool) -> None:
    """
    Display the system information for ASGI.
    
    Args:
        host: The host address the server is running on
        port: The port number the server is running on
        debug: Whether the app is in debug mode
    """
    print()  # Add a blank line before system info
    print_system_info(host, port, debug)
    print(f"{Colors.GREEN}➤ Starting Uvicorn ASGI server...{Colors.RESET}\n")


def main() -> None:
    """Main entry point for the ASGI application."""
    # Get configuration
    config = get_config()
    
    # Display startup message
    show_startup_message(config["host"], config["port"], config["debug"])
    
    # Import uvicorn here to avoid loading it when running WSGI
    import uvicorn
    
    # Configure and run Uvicorn
    uvicorn.run(
        "asgi:app",
        host=config["host"],
        port=config["port"],
        reload=config["debug"],
        log_level="warning",  # We handle our own logging
        server_header=False,
        date_header=False,
        proxy_headers=True,
        forwarded_allow_ips='*',
        timeout_keep_alive=30,
    )


if __name__ == "__main__":
    main()
