from flask import Blueprint, request, jsonify
from app.controllers.image_controller import ImageController
from app.controllers.upload_controller import UploadController

# Create Blueprint for image routes
image_bp = Blueprint('images', __name__)

# Initialize upload controller
upload_controller = UploadController()


def _handle_health_check():
    """Handle health check requests"""
    return jsonify({
        'message': 'NeuroView Backend API is running',
        'success': True,
        'status': 'healthy'
    }), 200


def _handle_get_all_images():
    """Handle get all images requests"""
    result, status_code = ImageController.get_all_images()
    return jsonify(result), status_code


def _handle_get_image_by_id(image_id):
    """Handle get specific image by ID requests"""
    result, status_code = ImageController.get_image_by_id(image_id)
    return jsonify(result), status_code


def _handle_create_image():
    """Handle create image from JSON data requests"""
    data = request.get_json()
    result, status_code = ImageController.create_image(data)
    return jsonify(result), status_code


def _handle_upload_image():
    """Handle file upload requests with automatic ML prediction and save results to database"""
    file = request.files['file']
    name = request.form.get('name')
    
    try:
        # Upload the image first
        upload_result, upload_status = upload_controller.upload_image(file, name)
        
        if upload_status != 201:
            return jsonify(upload_result), upload_status
        
        # Get the image ID from the upload result
        image_id = upload_result['data'].get('id')
        
        if not image_id:
            return jsonify({
                'message': 'Image uploaded successfully, but no image ID returned',
                'success': True,
                'data': upload_result['data'],
                'warning': 'Could not run prediction without image ID'
            }), 201
        
        # Reset file pointer to beginning for prediction
        file.seek(0)
        file_data = file.read()
        
        # Run ML prediction on the uploaded image and save to database
        prediction_result, prediction_status = ImageController.predict_and_save_brain_tumor(file_data, image_id)
        
        # Combine upload and prediction results
        if prediction_status == 200 and prediction_result['success']:
            combined_result = {
                'message': 'Image uploaded, analyzed, and prediction saved successfully',
                'success': True,
                'data': upload_result['data'],
                'prediction': prediction_result['data'],
                'updated_image': prediction_result.get('updated_image')
            }
            return jsonify(combined_result), 201
        else:
            # Upload succeeded but prediction failed - still return success with upload data
            combined_result = {
                'message': 'Image uploaded successfully, but prediction failed',
                'success': True,
                'data': upload_result['data'],
                'prediction_error': prediction_result.get('error', 'Prediction failed')
            }
            return jsonify(combined_result), 201
            
    except Exception as e:
        return jsonify({
            'error': f'Upload or prediction failed: {str(e)}',
            'success': False
        }), 500


def _handle_predict_brain_tumor():
    """Handle brain tumor prediction from uploaded image with optional saving to database"""
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file provided',
            'success': False
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'error': 'No file selected',
            'success': False
        }), 400
    
    try:
        # Read file data
        file_data = file.read()
        
        # Check if image_id is provided to save results
        image_id = request.form.get('image_id')
        
        if image_id:
            # Use the predict and save method
            result, status_code = ImageController.predict_and_save_brain_tumor(file_data, image_id)
        else:
            # Use the regular prediction method without saving
            result, status_code = ImageController.predict_brain_tumor(file_data)
            
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            'error': f'Error processing file: {str(e)}',
            'success': False
        }), 500


def _handle_get_model_info():
    """Handle ML model information requests"""
    result, status_code = ImageController.get_ml_model_info()
    return jsonify(result), status_code


def _handle_invalid_post_request():
    """Handle invalid POST requests with helpful error message"""
    return jsonify({
        'error': 'Invalid POST request. Expected either file upload (multipart/form-data with file) or JSON data (name/url)',
        'success': False,
        'examples': {
            'file_upload': 'Send multipart/form-data with "file" field',
            'create_image': 'Send JSON with {"name": "...", "url": "..."}'
        }
    }), 400


@image_bp.route('/predict', methods=['POST'])
def predict_brain_tumor():
    """
    Endpoint for brain tumor prediction from uploaded image
    
    POST requests:
    - multipart/form-data with 'file' -> predict brain tumor type
    - multipart/form-data with 'file' and 'image_id' -> predict and save results to database
    
    Returns:
        JSON response with prediction results
    """
    return _handle_predict_brain_tumor()


@image_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """
    Endpoint for getting ML model information
    
    Returns:
        JSON response with model metadata
    """
    return _handle_get_model_info()


@image_bp.route('/auto', methods=['GET', 'POST'])
def auto_detect_api():
    """
    Universal API endpoint that automatically detects which operation to perform
    based on request method, parameters, and data type.
    
    GET requests:
    - ?action=health -> health check
    - ?action=model-info -> get ML model information
    - ?id=<uuid> -> get specific image
    - default -> get all images
    
    POST requests:
    - multipart/form-data with 'file' + ?action=predict -> brain tumor prediction
    - multipart/form-data with 'file' -> upload image with automatic prediction and save to database
    - application/json with name/url -> create image
    
    Returns:
        JSON response based on detected operation
    """
    try:
        if request.method == 'GET':
            # Handle GET requests
            action = request.args.get('action')
            image_id = request.args.get('id')
            
            if action == 'health':
                return _handle_health_check()
            elif action == 'model-info':
                return _handle_get_model_info()
            elif image_id:
                return _handle_get_image_by_id(image_id)
            else:
                return _handle_get_all_images()
        
        elif request.method == 'POST':
            # Handle POST requests
            action = request.args.get('action')
            
            # Check if it's a file upload (multipart/form-data with file)
            if 'file' in request.files and request.files['file'].filename != '':
                # Check if it's a prediction request
                if action == 'predict':
                    return _handle_predict_brain_tumor()
                else:
                    # Default to upload
                    return _handle_upload_image()
            
            # Check if it's JSON data for creating an image
            elif request.is_json and request.get_json():
                return _handle_create_image()
            
            else:
                return _handle_invalid_post_request()
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'success': False,
            'message': str(e)
        }), 500 