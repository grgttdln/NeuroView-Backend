from app.config.database import supabase_config
from app.models.interfaces.image_interface import ImageInterface
import requests
from typing import Dict, List, Optional, Any


class ImageRepository(ImageInterface):
    """Repository class for handling image data operations using Supabase REST API"""
    
    def create_image(self, name: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Create a new image record using Supabase REST API
        
        Args:
            name (str): Name of the image
            url (str): URL of the image
            
        Returns:
            Optional[Dict[str, Any]]: Created image data or None if failed
        """
        try:
            # Prepare data for insertion
            data = {
                "name": name,
                "url": url
            }
            
            # Make POST request to Supabase
            response = requests.post(
                f"{supabase_config.get_base_url()}/images",
                headers=supabase_config.get_headers(),
                json=data
            )
            
            if response.status_code == 201:
                # Return the first created record
                created_data = response.json()
                return created_data[0] if isinstance(created_data, list) and created_data else created_data
            else:
                print(f"Supabase API error in create_image: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"Request error in create_image: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in create_image: {e}")
            return None
    
    def get_all_images(self) -> List[Dict[str, Any]]:
        """
        Retrieve all images using Supabase REST API
        
        Returns:
            List[Dict[str, Any]]: List of image dictionaries or empty list if failed
        """
        try:
            # Make GET request to Supabase with ordering
            response = requests.get(
                f"{supabase_config.get_base_url()}/images?select=*&order=uploaded_at.desc",
                headers=supabase_config.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Supabase API error in get_all_images: {response.status_code} - {response.text}")
                return []
                
        except requests.RequestException as e:
            print(f"Request error in get_all_images: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in get_all_images: {e}")
            return []
    
    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific image by ID using Supabase REST API
        
        Args:
            image_id (str): UUID of the image
            
        Returns:
            Optional[Dict[str, Any]]: Image data or None if not found
        """
        try:
            # Make GET request to Supabase with ID filter
            response = requests.get(
                f"{supabase_config.get_base_url()}/images?select=*&id=eq.{image_id}",
                headers=supabase_config.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            else:
                print(f"Supabase API error in get_image_by_id: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"Request error in get_image_by_id: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in get_image_by_id: {e}")
            return None
    
    def update_image_information(self, image_id: str, prediction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update the information column of an image with prediction data in JSON format
        
        Args:
            image_id (str): UUID of the image
            prediction_data (Dict[str, Any]): Prediction results to save in JSON format
            
        Returns:
            Optional[Dict[str, Any]]: Updated image data or None if failed
        """
        try:
            # Prepare data for update
            data = {
                "information": prediction_data
            }
            
            # Make PATCH request to Supabase to update the information column
            response = requests.patch(
                f"{supabase_config.get_base_url()}/images?id=eq.{image_id}",
                headers=supabase_config.get_headers(),
                json=data
            )
            
            if response.status_code == 200:
                # Return the updated record
                updated_data = response.json()
                return updated_data[0] if isinstance(updated_data, list) and updated_data else updated_data
            else:
                print(f"Supabase API error in update_image_information: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"Request error in update_image_information: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in update_image_information: {e}")
            return None 