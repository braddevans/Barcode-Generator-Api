# 🏷️ Barcode Generator API

A high-performance Flask-based API for generating barcodes in various formats. Returns barcodes as base64-encoded images or raw PNGs with extensive customization options.

## ✨ Features

- 🚀 **Multiple Barcode Formats**: Support for Code128, EAN, UPC, ISBN, and more
- 🖼️ **Flexible Output**: Get barcodes as base64-encoded images or raw PNGs
- 🎨 **Fully Customizable**: Control size, colors, text, and layout
- 📦 **Containerized**: Ready for Docker deployment
- 🏗️ **Production Ready**: Built with Gunicorn and best practices
- 📊 **Detailed Logging**: Built-in logging for easy debugging

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Docker (for containerized deployment)
- pip (Python package manager)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BarcodeApp
   ```

2. **Set up virtual environment**
   ```bash
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python wsgi.py
   ```
   The API will be available at `http://localhost:5000`

## 🛠️ API Usage

### Base URL
- Development: `http://localhost:5000`
- Production: `http://your-domain.com`

### Endpoints

#### 1. API Status
```
GET /
```
Returns API status and available endpoints.

#### 2. Generate Barcode
```
GET /barcode?data=TEST123&type=code128&raw=false
```

**Required Parameters:**
- `data` - The data to encode in the barcode

**Optional Parameters:**
- `type` - Barcode type (default: `code128`)
- `raw` - Return raw PNG if `true` (default: `false`)

**Barcode Customization:**
- `module_width` - Width of a single module (default: `0.2`)
- `module_height` - Height of a single module (default: `15.0`)
- `quiet_zone` - Quiet zone size (default: `6.5`)
- `font_size` - Font size (default: `10`)
- `text_distance` - Distance between barcode and text (default: `5.0`)
- `background` - Background color (default: `white`)
- `foreground` - Foreground color (default: `black`)
- `write_text` - Whether to write the text (default: `true`)
- `text` - Custom text to display (default: uses `data` parameter)
- `center_text` - Center the text (default: `true`)

**Example with Customization:**
```
GET /barcode?data=TEST123&type=code128&module_width=0.3&module_height=20&foreground=red&background=white&font_size=12
```

## 🔍 Supported Barcode Types

- `code128` - Code 128 (default)
- `ean8` - EAN-8
- `ean13` - EAN-13
- `ean` - EAN (auto-detects length)
- `upc` - UPC-A
- `isbn10` - ISBN-10
- `isbn13` - ISBN-13
- `issn` - ISSN
- `code39` - Code 39
- `gs1` - GS1
- `gtin` - GTIN

## 🐳 Docker Deployment

### Build the Image
```bash
docker build -t barcode-api .
```

### Run with Docker Compose (Recommended)
```bash
docker-compose up -d
```
The API will be available at `http://localhost:8000`

### Environment Variables

| Variable    | Default     | Description                          |
|-------------|-------------|--------------------------------------|
| `HOST`     | 0.0.0.0    | Host to bind to                     |
| `PORT`     | 8000        | Port to run on                      |
| `FLASK_ENV`| production  | Environment (development/production) |
| `DEBUG`    | false       | Enable debug mode                   |

## 📚 Usage Examples

### Basic Usage

```bash
# Generate a Code128 barcode
curl "http://localhost:5000/barcode?data=TEST123"

# Generate an EAN-13 barcode
curl "http://localhost:5000/barcode?data=5901234123457&type=ean13"

# Get raw PNG image
curl "http://localhost:5000/barcode?data=TEST123&raw=true" --output barcode.png
```

### Advanced Customization

```bash
# Custom colors and size
curl "http://localhost:5000/barcode?data=TEST123&foreground=blue&background=white&module_width=0.3"

# Custom text and font
curl "http://localhost:5000/barcode?data=12345&text=SCAN%20ME&font_size=14&center_text=true"

# Minimal barcode (no text)
curl "http://localhost:5000/barcode?data=TEST123&write_text=false"
```

## 🔄 Response Format

### JSON Response (default)

```json
{
  "barcode_type": "code128",
  "data": "TEST123",
  "barcode": "data:image/png;base64,...",
  "generated_at": "2023-07-20T12:00:00.000000",
  "options": {
    "module_width": 0.2,
    "module_height": 15.0,
    "quiet_zone": 6.5,
    "font_size": 10,
    "text_distance": 5.0,
    "background": "white",
    "foreground": "black",
    "write_text": true,
    "center_text": true
  }
}
```

### Raw Image Response (when raw=true)
Returns the raw PNG image file with appropriate headers.

## ⚠️ Error Handling

Error responses include a JSON object with an `error` field containing a descriptive message.

**Example error response (400 Bad Request):**
```json
{
  "error": "Missing required parameter 'data'"
}
```

**Example error response (400 Unsupported Type):**
```json
{
  "error": "Unsupported barcode type: invalid_type",
  "supported_types": ["code128", "ean8", "ean13", ...]
}
```

## 🔧 Health Check

The Docker container includes a health check that verifies the API is running:

```bash
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [python-barcode](https://github.com/WhyNotHugo/python-barcode)
- Powered by Flask and Gunicorn
- Containerized with Docker
