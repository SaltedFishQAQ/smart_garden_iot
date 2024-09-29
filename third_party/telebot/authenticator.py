import requests
import logging

logger = logging.getLogger(__name__)

class Authenticator:
    def __init__(self, base_url):
        self.base_url = base_url
        self.authenticated_users = set()  # Keep track of authenticated users

    def is_authenticated(self, user_id):
        """Check if a user is already authenticated."""
        return user_id in self.authenticated_users

    def add_authenticated_user(self, user_id):
        """Mark a user as authenticated."""
        self.authenticated_users.add(user_id)

    def clear_user(self, user_id):
        """Remove a user from authenticated users."""
        self.authenticated_users.discard(user_id)

    def authenticate(self, username, password):
        """Authenticate a user with the provided username and password."""
        auth_data = {
            "name": username,
            "password": password
        }
        try:
            response = requests.post(f"{self.base_url}/user/login", json=auth_data)

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.info(f"User {username} authenticated successfully.")
                    return True, result['data']['name']
                else:
                    logger.warning(f"Authentication failed for user {username}.")
                    return False, "Username/Password is wrong, try again."
            else:
                logger.error(f"Server error during authentication for user {username}.")
                return False, "Error connecting to server."
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return False, "An error occurred. Please try again."

