# Barcode Generator API

A simple Flask-based API that generates barcodes in various formats and returns them as base64-encoded images.

## Features

- Generate barcodes in multiple formats (Code128, EAN, UPC, ISBN, etc.)
- Returns barcodes as base64-encoded images or raw PNG
- Containerized with Docker for easy deployment
- Production-ready configuration with Gunicorn and Uvicorn
- Health check endpoint
- Comprehensive logging

## Prerequisites

- Python 3.8+
- Docker (for containerized deployment)
- pip (Python package manager)

## Local Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode

```bash
python wsgi.py
```

The API will be available at `http://localhost:5000`
- Base URL: `http://localhost:5000`
- API Endpoint: `http://localhost:5000/barcode`
- Health Check: `http://localhost:5000/health`
- Root URL: `http://localhost:5000/` (shows a welcome message)

### Production Mode with Docker

1. Build and start the container:
   ```bash
   docker-compose up -d --build
   ```

2. The API will be available at `http://localhost:8000`
   - Base URL: `http://localhost:8000`
   - API Endpoint: `http://localhost:8000/barcode`
   - Health Check: `http://localhost:8000/health`

### Managing the Docker Container

- View logs:
  ```bash
  docker-compose logs -f
  ```

- Stop the container:
  ```bash
  docker-compose down
  ```

- Rebuild the container (after making changes):
  ```bash
  docker-compose up -d --build
  ```

## Environment Variables

| Variable  | Default | Description |
|-----------|---------|-------------|
| HOST      | 0.0.0.0 | Host to bind the server to |
| PORT      | 8000    | Port to run the server on |
| DEBUG     | false   | Enable debug mode |
| LOG_LEVEL | INFO    | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

## Usage

### Generate a Barcode

Make a GET request to `/barcode` with the following query parameters:

- `data` (required): The data to encode in the barcode
- `type` (optional): The type of barcode (default: code128)
- `raw` (optional): If set to 'true', returns the raw PNG image instead of a JSON response (default: false)

#### Supported Barcode Types:
- code128 (default)
- ean8
- ean13
- ean
- upc
- isbn10
- isbn13
- issn
- code39

### Example Requests

**JSON Response (default):**
```
GET /barcode?data=123456789012&type=code128
```

**Raw Image Response:**
```
GET /barcode?data=123456789012&type=code128&raw=true
```

### Example Response

```json
{
  "status": "success",
  "barcode_type": "code128",
  "data": "123456789012",
  "barcode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### Using the Barcode

The barcode is returned as a base64-encoded data URL. You can use it directly in an HTML image tag:

```html
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..." />
```

## Error Handling

- If the `data` parameter is missing, returns a 400 error
- If an unsupported barcode type is provided, returns a 400 error with a list of supported types
- Returns 500 for any server-side errors
