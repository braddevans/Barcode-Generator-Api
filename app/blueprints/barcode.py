from flask import Blueprint, request, jsonify, make_response, render_template
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
        """Validate barcode generation request parameters.
        
        Returns:
            tuple: (is_valid, (error_response, status_code, show_form))
                  - is_valid: Boolean indicating if the request is valid
                  - error_response: Error response dict if not valid
                  - status_code: HTTP status code if not valid
                  - show_form: Boolean indicating if the form should be shown
        """
        self.logger.debug(f"Validating request for barcode type: {barcode_type}")
        
        if not data:
            self.logger.debug("No data provided, showing form")
            return False, (None, None, True)  # (error_response, status_code, show_form)
            
        if barcode_type not in self.SUPPORTED_TYPES:
            error_msg = f"Unsupported barcode type: {barcode_type}"
            self.logger.error(error_msg)
            return False, ({
                "error": error_msg,
                "supported_types": self.SUPPORTED_TYPES
            }, 400, False)
            
        return True, (None, None, False)
        
        return True, (None, None)
    
    def generate_barcode(self, data, barcode_type='code128', raw=False, **writer_options):
        """Generate a barcode with the given data and type.
        
        Args:
            data: The data to encode in the barcode
            barcode_type: Type of barcode to generate (default: code128)
            raw: If True, returns raw image data
            **writer_options: Additional options for the barcode writer:
                - module_width: Width of a single module (default: 0.2)
                - module_height: Height of a single module (default: 15.0)
                - quiet_zone: Quiet zone size (default: 6.5)
                - font_size: Font size (default: 10)
                - text_distance: Distance between barcode and text (default: 5.0)
                - background: Background color (default: 'white')
                - foreground: Foreground color (default: 'black')
                - write_text: Whether to write the text (default: True)
                - text: Custom text to display (default: None, uses data)
                - center_text: Center the text (default: True)
                - guardbar: Whether to add guard bars (default: False, only for EAN/UPC)
                - guardbar_height: Height of guard bars as a factor of module_height (default: 1.0)
        """
        self.logger.info(f"Generating {barcode_type} barcode for data: {data}")
        
        try:
            # Get barcode class
            barcode_class = barcode.get_barcode_class(barcode_type)
            self.logger.debug(f"Using barcode class: {barcode_class.__name__}")
            
            # Set up writer with options
            writer = ImageWriter()
            
            # Set writer options
            for key, value in writer_options.items():
                if hasattr(writer, key):
                    setattr(writer, key, value)
            
            # Generate barcode
            barcode_instance = barcode_class(data, writer=writer)
            
            # Add guard bars for EAN/UPC barcodes if requested
            if writer_options.get('guardbar', False) and barcode_type in ['ean8', 'ean13', 'ean', 'upc', 'upca']:
                # For EAN13, we need to use the renderer to add guard bars
                if barcode_type == 'ean13':
                    from barcode.ean import EAN13
                    if isinstance(barcode_instance, EAN13):
                        guardbar_height = float(writer_options.get('guardbar_height', 1.0))
                        # Get the renderer and set guard bar height
                        renderer = barcode_instance.writer
                        renderer.guardbar_height = guardbar_height
                        self.logger.debug(f"Set guard bar height to {guardbar_height} for EAN13")
                elif hasattr(barcode_instance, 'add_guard_bar'):
                    # For other barcode types that support add_guard_bar
                    guardbar_height = float(writer_options.get('guardbar_height', 1.0))
                    barcode_instance.add_guard_bar(guardbar_height)
                    self.logger.debug(f"Added guard bars with height factor: {guardbar_height}")
                else:
                    self.logger.warning(f"Guard bars not supported for barcode type: {barcode_type}")
            
            # Save to bytes buffer
            buffer = BytesIO()
            barcode_instance.write(buffer, writer_options)
            
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
            
            # Include writer options in response
            response = {
                'barcode_type': barcode_type,
                'data': data,
                'barcode': f"data:image/png;base64,{b64_barcode}",
                'generated_at': datetime.utcnow().isoformat(),
                'options': writer_options
            }
            
            return response
            
        except Exception as e:
            error_msg = f"Error generating {barcode_type} barcode: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise

# Create instance of BarcodeGenerator
barcode_generator = BarcodeGenerator()

@bp.route('/barcode', methods=['GET'])
def generate_barcode():
    """Endpoint to generate barcode.
    
    Query Parameters:
        data (required): The data to encode in the barcode
        type: Type of barcode (default: code128)
        raw: Return raw image if 'true' (default: false)
        
        # Writer options
        module_width: Width of a single module (default: 0.2)
        module_height: Height of a single module (default: 15.0)
        quiet_zone: Quiet zone size (default: 6.5)
        font_size: Font size (default: 10)
        text_distance: Distance between barcode and text (default: 5.0)
        background: Background color (default: 'white')
        foreground: Foreground color (default: 'black')
        write_text: Whether to write the text (default: 'true')
        text: Custom text to display (default: None, uses data)
        center_text: Center the text (default: 'true')
        guardbar: Add guard bars for EAN/UPC barcodes (default: 'false')
        guardbar_height: Height of guard bars as a factor of module_height (default: 1.0)
    """
    # Get query parameters
    data = request.args.get('data')
    barcode_type = request.args.get('type', 'code128').lower()
    raw = request.args.get('raw', 'false').lower() == 'true'
    
    # Get writer options
    writer_options = {}
    float_params = ['module_width', 'module_height', 'quiet_zone', 'text_distance']
    int_params = ['font_size']
    bool_params = ['write_text', 'center_text', 'guardbar']
    color_params = ['background', 'foreground']
    float_params += ['guardbar_height']
    
    # Process writer options
    for param in request.args:
        if param in float_params + int_params + bool_params + color_params + ['text']:
            value = request.args.get(param)
            
            # Convert to appropriate type
            if param in float_params:
                try:
                    writer_options[param] = float(value)
                except (ValueError, TypeError):
                    pass
            elif param in int_params:
                try:
                    writer_options[param] = int(value)
                except (ValueError, TypeError):
                    pass
            elif param in bool_params:
                writer_options[param] = value.lower() == 'true'
            else:  # color params or text
                writer_options[param] = value
    
    # Validate request
    is_valid, (error_response, status_code, show_form) = barcode_generator.validate_request(data, barcode_type)
    
    # If we should show the form (no data provided)
    if show_form:
        return render_template('barcode_form.html')
        
    # If there's an error response
    if error_response is not None:
        return jsonify(error_response), status_code
    
    try:
        result = barcode_generator.generate_barcode(data, barcode_type, raw, **writer_options)
        
        if raw:
            response = make_response(result['content'])
            response.headers.set('Content-Type', result['content_type'])
            response.headers.set('Content-Disposition', f'attachment; filename={result["filename"]}')
            return response
            
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"Error generating barcode: {str(e)}"
        barcode_generator.logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500
