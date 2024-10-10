import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, application):
        self.application = application
        self.subscribed_users = set()
        logger.info("NotificationManager initialized.")

    def register_user(self, user_id):
        """Register a user for notifications."""
        self.subscribed_users.add(user_id)
        logger.info(f"User {user_id} registered for notifications. Current subscribers: {self.subscribed_users}")

    async def notify_users(self, message):
        """Send a message to all subscribed users."""
        if not self.subscribed_users:
            logger.info("No subscribed users to send notifications to.")
            return

        for user_id in self.subscribed_users:
            try:
                logger.info(f"Sending message to user {user_id}: {message}")
                await self.application.bot.send_message(chat_id=user_id, text=message)
                logger.info(f"Sent message to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")