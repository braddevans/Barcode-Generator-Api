from flask import Blueprint, request, jsonify, make_response
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from datetime import datetime
from .. import SimpleLogger

# Create blueprint
bp = Blueprint('barcode', __name__)

class BarcodeGenerator:
    """Handles barcode generation and validation."""
    
    # Supported barcode types
    SUPPORTED_TYPES = ['code128', 'ean8', 'ean13', 'ean', 'upc', 'isbn10', 'isbn13', 'issn', 'code39']
    
    def __init__(self):
        self.logger = SimpleLogger(self.__class__.__name__)
    
    def validate_request(self, data, barcode_type):
        """Validate barcode generation request parameters."""
        self.logger.debug(f"Validating request for barcode type: {barcode_type}")
        
        if not data:
            error_msg = "Missing required parameter 'data'"
            self.logger.error(error_msg)
            return False, ({"error": error_msg}, 400)
        
        if barcode_type not in self.SUPPORTED_TYPES:
            error_msg = f"Unsupported barcode type: {barcode_type}"
            self.logger.error(error_msg)
            return False, ({
                "error": error_msg,
                "supported_types": self.SUPPORTED_TYPES
            }, 400)
        
        return True, (None, None)
    
    def generate_barcode(self, data, barcode_type='code128', raw=False):
        """Generate a barcode with the given data and type."""
        self.logger.info(f"Generating {barcode_type} barcode for data: {data}")
        
        try:
            # Get barcode class
            barcode_class = barcode.get_barcode_class(barcode_type)
            self.logger.debug(f"Using barcode class: {barcode_class.__name__}")
            
            # Generate barcode
            barcode_instance = barcode_class(data, writer=ImageWriter())
            
            # Save to bytes buffer
            buffer = BytesIO()
            barcode_instance.write(buffer)
            
            # Convert to base64
            b64_barcode = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            self.logger.info(f"Successfully generated {barcode_type} barcode")
            
            if raw:
                self.logger.debug("Returning raw image response")
                return {
                    'content': buffer.getvalue(),
                    'content_type': 'image/png',
                    'filename': f'barcode_{barcode_type}.png'
                }
            
            return {
                'barcode_type': barcode_type,
                'data': data,
                'barcode': f"data:image/png;base64,{b64_barcode}",
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error generating {barcode_type} barcode: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise

# Create instance of BarcodeGenerator
barcode_generator = BarcodeGenerator()

@bp.route('/barcode', methods=['GET'])
def generate_barcode():
    """Endpoint to generate barcode."""
    # Get query parameters
    data = request.args.get('data')
    barcode_type = request.args.get('type', 'code128').lower()
    raw = request.args.get('raw', 'false').lower() == 'true'
    
    # Validate request
    is_valid, error_response = barcode_generator.validate_request(data, barcode_type)
    if not is_valid:
        return error_response
    
    try:
        result = barcode_generator.generate_barcode(data, barcode_type, raw)
        
        if raw:
            response = make_response(result['content'])
            response.headers.set('Content-Type', result['content_type'])
            response.headers.set('Content-Disposition', 'inline', filename=result['filename'])
            return response
            
        return jsonify({
            "status": "success",
            **result
        })
            
    except Exception as e:
        error_msg = f"Error generating {barcode_type} barcode: {str(e)}"
        return jsonify({
            "status": "error",
            "message": error_msg,
            "type": type(e).__name__
        }), 500
