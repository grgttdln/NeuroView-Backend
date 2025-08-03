import numpy as np
import pickle
import os
from PIL import Image
import io
from typing import Dict, Tuple, Union


class MLPredictionService:
    """Service class for handling machine learning predictions"""
    
    def __init__(self):
        """Initialize the ML service and load the model"""
        self.model = None
        self.label_map = {
            0: "glioma",
            1: "meningioma", 
            2: "notumor",
            3: "pituitary"
        }
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained neural network model"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'best_brain_nn_model.pkl')
            model_path = os.path.abspath(model_path)
            
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
                
            print(f"✅ ML Model loaded successfully from {model_path}")
            
        except FileNotFoundError:
            print(f"❌ Error: Model file not found at {model_path}")
            raise Exception("ML model file not found. Please ensure the model is properly installed.")
        except Exception as e:
            print(f"❌ Error loading ML model: {e}")
            raise Exception(f"Failed to load ML model: {str(e)}")
    
    def _leaky_relu(self, x, alpha=0.01):
        """Leaky ReLU activation function"""
        return np.where(x > 0, x, alpha * x)
    
    def _softmax(self, x):
        """Softmax activation function"""
        exp_vals = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_vals / np.sum(exp_vals, axis=1, keepdims=True)
    
    def _forward_pass(self, X):
        """Perform forward pass through the neural network"""
        if self.model is None:
            raise Exception("Model not loaded. Cannot perform prediction.")
            
        W1, b1 = self.model["W1"], self.model["b1"]
        W2, b2 = self.model["W2"], self.model["b2"] 
        W3, b3 = self.model["W3"], self.model["b3"]
        
        # Forward pass
        Z1 = X @ W1 + b1
        A1 = self._leaky_relu(Z1)
        Z2 = A1 @ W2 + b2
        A2 = self._leaky_relu(Z2)
        Z3 = A2 @ W3 + b3
        A3 = self._softmax(Z3)
        
        return A3
    
    def _preprocess_image(self, image_data: Union[bytes, Image.Image]) -> np.ndarray:
        """
        Preprocess image data for prediction
        
        Args:
            image_data: Raw image bytes or PIL Image object
            
        Returns:
            Preprocessed image array ready for model input
        """
        try:
            # Handle different input types
            if isinstance(image_data, bytes):
                img = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, Image.Image):
                img = image_data
            else:
                raise ValueError("Invalid image data type. Expected bytes or PIL Image.")
            
            # Convert to grayscale and resize
            img = img.convert("L")
            img_resized = img.resize((32, 32))
            
            # Convert to array and normalize
            img_array = np.array(img_resized).flatten().astype(np.float32)
            
            # Scale using the model's scaler
            scaler = self.model["scaler"]
            img_scaled = scaler.transform(img_array.reshape(1, -1))
            
            return img_scaled
            
        except Exception as e:
            raise Exception(f"Image preprocessing failed: {str(e)}")
    
    def predict_brain_tumor(self, image_data: Union[bytes, Image.Image]) -> Dict:
        """
        Predict brain tumor type from image
        
        Args:
            image_data: Raw image bytes or PIL Image object
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Preprocess the image
            processed_image = self._preprocess_image(image_data)
            
            # Get predictions
            probabilities = self._forward_pass(processed_image)
            predicted_class = int(np.argmax(probabilities))
            tumor_type = self.label_map[predicted_class]
            confidence = float(np.max(probabilities))
            
            # Format probabilities for each class
            class_probabilities = {
                self.label_map[i]: float(probabilities[0][i]) 
                for i in range(len(self.label_map))
            }
            
            return {
                'success': True,
                'predicted_class': predicted_class,
                'tumor_type': tumor_type,
                'confidence': confidence,
                'probabilities': probabilities.tolist()[0],
                'class_probabilities': class_probabilities,
                'message': f'Brain scan classified as: {tumor_type} (confidence: {confidence:.2%})'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Prediction failed: {str(e)}',
                'predicted_class': None,
                'tumor_type': None,
                'confidence': 0.0,
                'probabilities': [],
                'class_probabilities': {}
            }
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary containing model metadata
        """
        if self.model is None:
            return {
                'loaded': False,
                'error': 'Model not loaded'
            }
        
        return {
            'loaded': True,
            'model_type': 'Neural Network',
            'input_shape': '32x32 grayscale',
            'output_classes': len(self.label_map),
            'class_labels': list(self.label_map.values()),
            'description': 'Brain tumor classification model trained on medical imaging data'
        }


# Global instance of the ML service
ml_service = MLPredictionService()