# Barcode Generator API

A simple Flask-based API that generates barcodes in various formats and returns them as base64-encoded images.

## Setup

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python wsgi.py
   ```

3. The API will be available at `http://localhost:5000`
   - Base URL: `http://localhost:5000`
   - API Endpoint: `http://localhost:5000/api/barcode`
   - Root URL: `http://localhost:5000/` (shows a welcome message)

## Usage

### Generate a Barcode

Make a GET request to `/api/barcode` with the following query parameters:

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
GET /api/barcode?data=123456789012&type=code128
```

**Raw Image Response:**
```
GET /api/barcode?data=123456789012&type=code128&raw=true
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
