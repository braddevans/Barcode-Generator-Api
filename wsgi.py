"""
WSGI entry point for the Barcode Generator API.

This module serves as the WSGI entry point for running the application
using Gunicorn, uWSGI, or other WSGI servers.
"""
import os
import sys
import socket
import platform
from typing import Tuple, Dict, Any, List

from tabulate import tabulate
from app import create_app, Colors

# Create app instance for WSGI servers
app = create_app()


def print_banner() -> None:
    """Print a beautiful ASCII art banner."""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║{Colors.BOLD}{Colors.GREEN}            BARCODE GENERATOR API - v1.0.0{Colors.RESET}{Colors.CYAN}            ║
║{Colors.GRAY}      Generate barcodes with a simple HTTP API{Colors.CYAN}             ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}"""
    print(banner)


def get_system_info(host: str, port: int, debug: bool) -> List[Tuple[str, str]]:
    """
    Collect system and server information.
    
    Args:
        host: The host address the server is running on
        port: The port number the server is running on
        debug: Whether the app is in debug mode
        
    Returns:
        List of tuples containing (setting_name, setting_value)
    """
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    return [
        ("Environment", f"{Colors.GREEN if debug else Colors.YELLOW}"
                      f"{'Development' if debug else 'Production'}{Colors.RESET}"),
        ("Python", f"{python_version} ({platform.python_implementation()})"),
        ("Host", f"{host}:{port}"),
        ("Local URL", f"{Colors.BLUE}http://127.0.0.1:{port}{Colors.RESET}"),
        ("Network URL", f"{Colors.BLUE}http://{ip_address}:{port}{Colors.RESET}"),
        ("Hostname", hostname),
        ("IP Address", ip_address),
        ("OS", f"{platform.system()} {platform.release()}")
    ]


def print_system_info(host: str, port: int, debug: bool) -> None:
    """
    Print system and server information in a formatted table.
    
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
    Display the startup banner and system information.
    
    Args:
        host: The host address the server is running on
        port: The port number the server is running on
        debug: Whether the app is in debug mode
    """
    print("\n" * 2)  # Add some space before the banner
    print_banner()
    print()
    print_system_info(host, port, debug)
    print(f"\n{Colors.GREEN}➤ Server starting...{Colors.RESET}\n")


def get_config() -> Dict[str, Any]:
    """
    Get configuration from environment variables with defaults.
    
    Returns:
        Dictionary containing configuration values
    """
    return {
        "host": os.environ.get("HOST", "0.0.0.0"),
        "port": int(os.environ.get("PORT", 5000)),
        "debug": os.environ.get("DEBUG", "true").lower() in ("true", "1", "t")
    }


def main() -> None:
    """Main entry point for the application."""
    # Get configuration
    config = get_config()
    
    # Display startup message
    show_startup_message(config["host"], config["port"], config["debug"])
    
    # Run the Flask development server
    app.run(
        host=config["host"],
        port=config["port"],
        debug=config["debug"],
        use_reloader=config["debug"]
    )


if __name__ == "__main__":
    main()
