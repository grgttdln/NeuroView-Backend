import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseConfig:
    """Supabase REST API configuration class"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.base_url = f"{self.url}/rest/v1"
        
        # Default headers for all requests
        self.headers = {
            'apikey': self.anon_key,
            'Authorization': f'Bearer {self.anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def get_headers(self):
        """Get headers for Supabase API requests"""
        return self.headers
    
    def get_base_url(self):
        """Get base URL for Supabase REST API"""
        return self.base_url


# Global Supabase config instance
supabase_config = SupabaseConfig() 