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
        encoded_image = self.encode_image(image_bytes)
        data = {
            'images': [encoded_image],
            'similar_images': True,
            'classification_level': 'species'
        }
        headers = {
            'Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }

        try:
            logger.info(f"Sending plant identification request to {self.api_url}/identification")
            response = requests.post(f"{self.api_url}/identification", json=data, headers=headers)

            if response.status_code in [200, 201]:
                logger.info("Plant identification successful, returning result")
                return response.json()
            else:
                logger.error(f"Plant ID API error: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exception while calling Plant ID API: {e}")
            return None

