import requests
import base64
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class PlantIDClient:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def encode_image(self, image_bytes: BytesIO) -> str:
        """Encode the image in base64 format."""
        return base64.b64encode(image_bytes.getvalue()).decode('ascii')

    def identify_plant(self, image_bytes: BytesIO) -> dict:
        """Send the image to Plant.ID API as a base64-encoded string in JSON."""
        encoded_image = self.encode_image(image_bytes)
        data = {
            'images': [encoded_image],  # Send as base64 string
            'similar_images': True,  # Corrected: Boolean, not a string
            'classification_level': 'species'  # Example: request classification at species level
        }
        headers = {
            'Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }

        try:
            # Use JSON for the request body
            response = requests.post(f"{self.api_url}/identification", json=data, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Plant ID API error: {response.status_code}, {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Exception while calling Plant ID API: {e}")
            return {}
