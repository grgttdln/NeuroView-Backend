from app.models.repositories.image_repository import ImageRepository
from app.models.services.ml_prediction_service import ml_service


class ImageController:
    """Controller class containing business logic for image operations"""
    
    # Initialize the repository
    _repository = ImageRepository()
    
    @staticmethod
    def create_image(data):
        """
        Handle image creation with validation and business logic
        
        Args:
            data (dict): Request data containing image information
            
        Returns:
            tuple: (result_dict, status_code)
        """
        # Validate required fields
        if not data:
            return {
                'error': 'Request body is required',
                'success': False
            }, 400
        
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        
        # Validate name
        if not name:
            return {
                'error': 'Image name is required',
                'success': False
            }, 400
        
        # Set default URL if none provided
        if not url:
            url = 'https://via.placeholder.com/400x300?text=No+Image'
        
        # Basic URL validation (commented out)
        # if not (url.startswith('http://') or url.startswith('https://')):
        #     return {
        #         'error': 'Invalid URL format. URL must start with http:// or https://',
        #         'success': False
        #     }, 400
        
        # Create image using repository
        created_image = ImageController._repository.create_image(name, url)
        
        if created_image:
            return {
                'message': 'Image created successfully',
                'success': True,
                'data': created_image
            }, 201
        else:
            return {
                'error': 'Failed to create image. Please try again.',
                'success': False
            }, 500
    
    @staticmethod
    def get_all_images():
        """
        Handle retrieving all images
        
        Returns:
            tuple: (result_dict, status_code)
        """
        images = ImageController._repository.get_all_images()
        
        return {
            'message': 'Images retrieved successfully',
            'success': True,
            'data': images,
            'count': len(images)
        }, 200
    
    @staticmethod
    def get_image_by_id(image_id):
        """
        Handle retrieving a specific image by ID
        
        Args:
            image_id (str): UUID of the image
            
        Returns:
            tuple: (result_dict, status_code)
        """
        if not image_id:
            return {
                'error': 'Image ID is required',
                'success': False
            }, 400
        
        image = ImageController._repository.get_image_by_id(image_id)
        
        if image:
            return {
                'message': 'Image retrieved successfully',
                'success': True,
                'data': image
            }, 200
        else:
            return {
                'error': 'Image not found',
                'success': False
            }, 404
    
    @staticmethod
    def predict_brain_tumor(image_data):
        """
        Handle brain tumor prediction from image data
        
        Args:
            image_data: Raw image bytes or file-like object
            
        Returns:
            tuple: (result_dict, status_code)
        """
        if not image_data:
            return {
                'error': 'Image data is required',
                'success': False
            }, 400
        
        try:
            # Use ML service to make prediction
            prediction_result = ml_service.predict_brain_tumor(image_data)
            
            if prediction_result['success']:
                return {
                    'message': 'Brain tumor prediction completed successfully',
                    'success': True,
                    'data': prediction_result
                }, 200
            else:
                return {
                    'error': prediction_result.get('error', 'Prediction failed'),
                    'success': False
                }, 500
                
        except Exception as e:
            return {
                'error': f'Internal error during prediction: {str(e)}',
                'success': False
            }, 500
    
    @staticmethod
    def get_ml_model_info():
        """
        Get information about the ML model
        
        Returns:
            tuple: (result_dict, status_code)
        """
        try:
            model_info = ml_service.get_model_info()
            
            return {
                'message': 'Model information retrieved successfully',
                'success': True,
                'data': model_info
            }, 200
            
        except Exception as e:
            return {
                'error': f'Failed to get model info: {str(e)}',
                'success': False
            }, 500
    
    @staticmethod
    def predict_and_save_brain_tumor(image_data, image_id):
        """
        Handle brain tumor prediction from image data and save results to database
        
        Args:
            image_data: Raw image bytes or file-like object
            image_id (str): UUID of the image record to update
            
        Returns:
            tuple: (result_dict, status_code)
        """
        if not image_data:
            return {
                'error': 'Image data is required',
                'success': False
            }, 400
        
        if not image_id:
            return {
                'error': 'Image ID is required',
                'success': False
            }, 400
        
        try:
            # Use ML service to make prediction
            prediction_result = ml_service.predict_brain_tumor(image_data)
            
            if prediction_result['success']:
                # Save prediction results to database information column
                updated_image = ImageController._repository.update_image_information(image_id, prediction_result)
                
                if updated_image:
                    return {
                        'message': 'Brain tumor prediction completed and saved successfully',
                        'success': True,
                        'data': prediction_result,
                        'updated_image': updated_image
                    }, 200
                else:
                    # Prediction succeeded but saving failed
                    return {
                        'message': 'Brain tumor prediction completed but failed to save to database',
                        'success': True,
                        'data': prediction_result,
                        'warning': 'Prediction results could not be saved to database'
                    }, 200
            else:
                return {
                    'error': prediction_result.get('error', 'Prediction failed'),
                    'success': False
                }, 500
                
        except Exception as e:
            return {
                'error': f'Internal error during prediction: {str(e)}',
                'success': False
            }, 500 