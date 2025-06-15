# Barcode Generator API

A simple Flask-based API that generates barcodes in various formats and returns them as base64-encoded images or raw PNGs.

## Features

- Generate barcodes in multiple formats (Code128, EAN, UPC, ISBN, etc.)
- Returns barcodes as base64-encoded images or raw PNG
- Simple console logging for easy debugging
- Containerized with Docker for easy deployment
- Production-ready configuration with Gunicorn
- Lightweight and fast

## Prerequisites

- Python 3.13+
- Docker (for containerized deployment)
- pip (Python package manager)

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd BarcodeApp
   ```

2. Create and activate a virtual environment:
   ```bash
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode

```bash
python wsgi.py
```

The API will be available at `http://localhost:5000`

### Using the API

1. **Get API Status**
   ```
   GET /
   ```
   Returns API status and available endpoints.

2. **Generate Barcode**
   ```
   GET /barcode?data=TEST123&type=code128&raw=false
   ```
   - `data` (required): The data to encode in the barcode
   - `type` (optional): Barcode type (default: code128)
   - `raw` (optional): If true, returns raw PNG image (default: false)

## Docker Deployment

### Building the Docker Image

```bash
docker build -t barcode-api .
```

### Running with Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start the API at `http://localhost:8000`

### Environment Variables

- `HOST`: Host to bind to (default: 0.0.0.0)
- `PORT`: Port to run on (default: 8000)
- `FLASK_ENV`: Environment (development/production)
- `DEBUG`: Enable debug mode (true/false)

## API Endpoints

- `GET /` - API status and documentation
- `GET /barcode` - Generate a barcode

## Barcode Types

Supported barcode types include:
- code128 (default)
- ean
- ean13
- ean8
- gs1
- gtin
- isbn10
- isbn13
- issn
- upc
- upca

## Examples

### Generate a Code128 barcode (JSON response)
```
GET /barcode?data=TEST123
```

### Generate an EAN13 barcode (raw PNG)
```
GET /barcode?data=5901234123457&type=ean13&raw=true
```

## Logs

Logs are written to the `logs/` directory when running in a container.
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
