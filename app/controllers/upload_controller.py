import os
import uuid
import requests
from werkzeug.utils import secure_filename
from app.models.image_model import ImageModel


class UploadController:
    """Controller class for handling file uploads to Supabase Storage"""
    
    def __init__(self):
        # Initialize Supabase configuration
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.bucket_name = 'brain-images'  
        
        # Storage API headers
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/octet-stream'
        }
    
    def upload_image(self, file, name=None):
        """
        Upload image file to Supabase Storage and create database record
        
        Args:
            file: Flask file object from request
            name: Optional custom name for the image
            
        Returns:
            tuple: (result_dict, status_code)
        """
        try:
            # Validate file
            if not file or file.filename == '':
                return {
                    'error': 'No file provided',
                    'success': False
                }, 400
            
            # Check file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if file_extension not in allowed_extensions:
                return {
                    'error': f'File type not allowed. Supported formats: {", ".join(allowed_extensions)}',
                    'success': False
                }, 400
            
            # Generate unique filename
            secure_name = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}-{secure_name}"
            
            # Read file data
            file_data = file.read()
            
            # Upload to Supabase Storage using HTTP API
            upload_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{unique_filename}"
            
            upload_headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': file.content_type or 'application/octet-stream'
            }
            
            storage_response = requests.post(
                upload_url,
                headers=upload_headers,
                data=file_data
            )
            
            if storage_response.status_code not in [200, 201]:
                return {
                    'error': f'Failed to upload file: {storage_response.text}',
                    'success': False
                }, 500
            
            # Get public URL for the uploaded file
            public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{unique_filename}"
            
            # Use provided name or original filename
            image_name = name if name else secure_name
            
            # Create database record
            created_image = ImageModel.create_image(image_name, public_url)
            
            if created_image:
                return {
                    'message': 'Image uploaded and created successfully',
                    'success': True,
                    'data': created_image
                }, 201
            else:
                # If database creation fails, try to delete the uploaded file
                try:
                    delete_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{unique_filename}"
                    delete_headers = {
                        'apikey': self.supabase_key,
                        'Authorization': f'Bearer {self.supabase_key}'
                    }
                    requests.delete(delete_url, headers=delete_headers)
                except:
                    pass  # Don't fail if cleanup fails
                
                return {
                    'error': 'Failed to create image record in database',
                    'success': False
                }, 500
                
        except Exception as e:
            return {
                'error': f'Upload failed: {str(e)}',
                'success': False
            }, 500 