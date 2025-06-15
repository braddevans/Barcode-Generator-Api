"""
ASGI entry point for the Barcode Generator API.

This module serves as the ASGI entry point for running the application
using Uvicorn or other ASGI servers.
"""
from uvicorn.middleware.wsgi import WSGIMiddleware
from wsgi import app as wsgi_app

# Create ASGI app from WSGI app
app = WSGIMiddleware(wsgi_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "asgi:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
