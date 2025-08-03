from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class ImageInterface(ABC):
    """Abstract interface for image data operations"""
    
    @abstractmethod
    def create_image(self, name: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Create a new image record
        
        Args:
            name (str): Name of the image
            url (str): URL of the image
            
        Returns:
            Optional[Dict[str, Any]]: Created image data or None if failed
        """
        pass
    
    @abstractmethod
    def get_all_images(self) -> List[Dict[str, Any]]:
        """
        Retrieve all images
        
        Returns:
            List[Dict[str, Any]]: List of image dictionaries
        """
        pass
    
    @abstractmethod
    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific image by ID
        
        Args:
            image_id (str): UUID of the image
            
        Returns:
            Optional[Dict[str, Any]]: Image data or None if not found
        """
        pass
    
    @abstractmethod
    def update_image_information(self, image_id: str, prediction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update the information column of an image with prediction data
        
        Args:
            image_id (str): UUID of the image
            prediction_data (Dict[str, Any]): Prediction results to save
            
        Returns:
            Optional[Dict[str, Any]]: Updated image data or None if failed
        """
        pass 