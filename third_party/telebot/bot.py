import xml.etree.ElementTree as ET
import requests
import nest_asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue
import logging
from mqtt import MQTTClient
from authenticator import Authenticator
from notification import NotificationManager
from plant import PlantIDClient
from io import BytesIO

logging.basicConfig(
    filename='/tmp/bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

nest_asyncio.apply()

# Load configuration
class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        tree = ET.parse(self.config_file)
        root = tree.getroot()
        self.base_url = root.find('server/address').text
        self.token = root.find('bot/token').text
        self.mqtt_broker = root.find('mqtt/broker').text
        self.mqtt_port = int(root.find('mqtt/port').text)
        self.command_channel = root.find('mqtt/topic').text
        self.data_endpoint = root.find('api/data').text
        self.plant_api_url = root.find('plantid/api_url').text
        self.plant_api_key = root.find('plantid/api_key').text


def process_identification_result(result: dict) -> str:
    """Process the plant identification result and format a response."""
    try:
        # Correct parsing of nested fields
        suggestions = result.get('result', {}).get('classification', {}).get('suggestions', [])
        if not suggestions:
            return "No plant suggestions found."

        plant_name = suggestions[0].get('name', 'Unknown')
        probability = suggestions[0].get('probability', 0)
        is_plant = result.get('result', {}).get('is_plant', {}).get('binary', False)

        message = f"Plant identified: {plant_name}\n"
        message += f"Probability: {probability * 100:.2f}%\n"
        message += "This is a plant!" if is_plant else "This might not be a plant."

        # Add similar images if available
        similar_images = suggestions[0].get('similar_images', [])
        if similar_images:
            message += "\nSimilar images:\n"
            for image in similar_images:
                url = image.get('url_small', '')
                license_name = image.get('license_name', 'Unknown License')
                message += f"{url} (License: {license_name})\n"

        return message
    except KeyError:
        return "Unable to process the identification result."


# API Client class for fetching data and rules
class APIClient:
    def __init__(self, config: Config):
        self.base_url = config.base_url
        self.data_endpoint = config.data_endpoint
        self.rules_endpoint = "/rules"
        self.status_endpoint = "/status"
        self.plant_client = PlantIDClient(config.plant_api_url, config.plant_api_key)

    def fetch_data(self, measurement, page=1, size=10):
        """Fetch data from the server for a specific measurement."""
        url = f"{self.base_url}{self.data_endpoint}"
        params = {
            "measurement": measurement,
            "page": page,
            "size": size
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                return data.get("list", [])
        return []

    def fetch_rules(self, page=1, size=10):
        """Fetch rules from the server."""
        url = f"{self.base_url}{self.rules_endpoint}"
        params = {
            "page": page,
            "size": size
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                return data.get("list", [])
        return []

    def fetch_status(self, device_name):
        """Fetch status from the server for a specific device."""
        url = f"{self.base_url}/device/status"
        params = {
            "name": device_name
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                return data.get("data", {})
        return {}

    def identify_plant(self, image_bytes: BytesIO) -> dict:
        """Call PlantIDClient to identify a plant."""
        return self.plant_client.identify_plant(image_bytes)


class IoTBot:
    def __init__(self, config: Config, authenticator: Authenticator, api_client: APIClient, notification_manager: NotificationManager):
        self.config = config
        self.authenticator = authenticator
        self.api_client = api_client
        self.notification_manager = notification_manager

        # Create the MQTT client
        self.mqtt_client = MQTTClient(config, notification_manager)
        self.mqtt_client.connect()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f"Received /start command from user {update.message.from_user.id}.")
        user_id = update.message.from_user.id

        if not self.authenticator.is_authenticated(user_id):
            await update.message.reply_text("Please enter your username:")
            return

        await self.show_main_menu(update)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = update.message.text
        user_id = update.message.from_user.id

        if not self.authenticator.is_authenticated(user_id):
            if 'password_prompt' not in context.user_data:
                context.user_data['username'] = text
                await update.message.reply_text("Please enter your password:")
                context.user_data['password_prompt'] = True
            else:
                username = context.user_data['username']
                password = text
                success, message = self.authenticator.authenticate(username, password)
                if success:
                    await update.message.reply_text(f"Welcome, {message}!")
                    self.authenticator.add_authenticated_user(user_id)

                    # Register user for notifications after successful login
                    self.register_user_for_notifications(update)

                    await self.show_main_menu(update)
                else:
                    await update.message.reply_text(message)
                    await update.message.reply_text("Please enter your username:")
                    context.user_data.clear()
            return

        await self.process_commands(update, text)

    def register_user_for_notifications(self, update):
        """Subscribe user to notifications after successful login."""
        user_id = update.message.from_user.id
        self.mqtt_client.register_user(user_id)

    async def process_commands(self, update: Update, text: str):
        logger.info(f"Received message: {text}")
        if text == "Temperature":
            await self.get_temperature(update)
        elif text == "Humidity":
            await self.get_humidity(update)
        elif text == "Light":
            await self.light_menu(update)
        elif text == "View Rules":
            await self.rules_menu(update)
        elif text == "Watering":
            await self.watering_menu(update)
        elif text == "Status":
            await self.system_status(update)
        elif text == "Turn On Watering":
            self.mqtt_client.mqtt_publish(self.config.command_channel + 'irrigator', {"type": "opt", 'status': True})
            await update.message.reply_text("Watering system turned on.")
        elif text == "Turn Off Watering":
            self.mqtt_client.mqtt_publish(self.config.command_channel + 'irrigator', {"type": "opt", 'status': False})
            await update.message.reply_text("Watering system turned off.")
        elif text == "Turn On Light":
            self.mqtt_client.mqtt_publish(self.config.command_channel + 'light', {"type": "opt", 'status': True})
            await update.message.reply_text("Light turned on.")
        elif text == "Turn Off Light":
            self.mqtt_client.mqtt_publish(self.config.command_channel + 'light', {"type": "opt", 'status': False})
            await update.message.reply_text("Light turned off.")
        elif text == "Back to Main Menu":
            await self.show_main_menu(update)
        elif text == "Identify plant":  # Handle the new "Identify plant" command
            await update.message.reply_text("Please send a photo of the plant.")
        else:
            await update.message.reply_text("Invalid command.")

    async def show_main_menu(self, update: Update):
        keyboard = [
            [KeyboardButton("Temperature"), KeyboardButton("Humidity")],
            [KeyboardButton("Light"), KeyboardButton("View Rules")],
            [KeyboardButton("Watering"), KeyboardButton("Status")],
            [KeyboardButton("Identify plant")]  # Added the new button
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
        await update.message.reply_text("Please choose an option:", reply_markup=reply_markup)

    async def get_temperature(self, update: Update):
        data = self.api_client.fetch_data("temperature")
        if data:
            message = '\n'.join([f"{item.get('created_at', 'N/A')}: {item.get('value', 'N/A')}°C" for item in data])
            await update.message.reply_text(f"Temperature data:\n{message}")
        else:
            await update.message.reply_text("No temperature data available.")

    async def get_humidity(self, update: Update):
        data = self.api_client.fetch_data("humidity")
        if data:
            message = '\n'.join([f"{item.get('created_at', 'N/A')}: {item.get('value', 'N/A')}%" for item in data])
            await update.message.reply_text(f"Humidity data:\n{message}")
        else:
            await update.message.reply_text("No humidity data available.")

    async def light_menu(self, update: Update):
        keyboard = [
            [KeyboardButton("Turn On Light"), KeyboardButton("Turn Off Light")],
            [KeyboardButton("Back to Main Menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
        await update.message.reply_text("Control the light:", reply_markup=reply_markup)

    async def rules_menu(self, update: Update):
        """Fetch and display active rules to the user."""
        rules = self.api_client.fetch_rules()

        comparison_mapping = {
            "gt": "greater than",
            "lt": "less than",
            "lte": "less than or equal to",
        }

        if rules:
            active_rules = [rule for rule in rules if rule.get('is_deleted', 0) == 0]

            if active_rules:
                message = ""
                for rule in active_rules:
                    source = rule.get('src', 'Unknown')
                    entity = rule.get('entity', 'Unknown')
                    compare = rule.get('compare', '')
                    value = rule.get('value', '')
                    destination = rule.get('dst', 'Unknown')
                    action = rule.get('opt', 'Unknown')
                    description = rule.get('desc', 'No description')
                    created_at = rule.get('created_at', 'N/A')

                    comparison_text = comparison_mapping.get(compare, compare)
                    condition = f"If {entity} from {source} is {comparison_text} {value}"
                    action_description = f"turn {action} the {destination}"
                    message += f"Rule: {condition}, {action_description}.\n"
                    message += f"Description: {description}\n"
                    message += f"Created: {created_at}\n\n"

                await update.message.reply_text(message)
            else:
                await update.message.reply_text("No active rules available.")
        else:
            await update.message.reply_text("No rules available.")

    async def watering_menu(self, update: Update):
        keyboard = [
            [KeyboardButton("Turn On Watering"), KeyboardButton("Turn Off Watering")],
            [KeyboardButton("Back to Main Menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
        await update.message.reply_text("Control the watering system:", reply_markup=reply_markup)

    async def system_status(self, update: Update):
        """Fetch and display status for the devices: temperature, humidity, light, oxygen."""
        devices = ["temperature", "humidity", "light", "oxygen"]
        status_message = ""

        for device in devices:
            status = self.api_client.fetch_status(device)

            if status:
                device_status = status.get('device', False)
                sensor_status = status.get('sensor', False)

                device_emoji = "✅" if device_status else "❌"
                sensor_emoji = "✅" if sensor_status else "❌"

                if device in ["oxygen", "light"]:
                    actuator_status = status.get('actuator', False)
                    actuator_emoji = "✅" if actuator_status else "❌"
                    status_message += f"{device.capitalize()}:\n"
                    status_message += f"  Device: {device_emoji}  Sensor: {sensor_emoji}  Actuator: {actuator_emoji}\n\n"
                else:
                    status_message += f"{device.capitalize()}:\n"
                    status_message += f"  Device: {device_emoji}  Sensor: {sensor_emoji}\n\n"
            else:
                status_message += f"{device.capitalize()}:\n"
                status_message += f"  Device: ❌  Sensor: ❌\n\n"

        await update.message.reply_text(status_message)

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        if not self.authenticator.is_authenticated(user_id):
            await update.message.reply_text("Please authenticate first.")
            return

        logger.info(f"Photo received from user {user_id}")

        # Get the photo from the user's message
        photo_file = await update.message.photo[-1].get_file()  # Get the highest resolution photo
        photo_bytes = BytesIO()
        await photo_file.download_to_memory(photo_bytes)

        logger.info("Photo file downloaded to memory")

        # Call the PlantID API
        plant_result = self.api_client.identify_plant(photo_bytes)

        if plant_result is not None:
            logger.info(f"Plant identification successful: {plant_result}")
            formatted_result = process_identification_result(plant_result)
            logger.info(f"Formatted result: {formatted_result}")
            await update.message.reply_text(formatted_result)
        else:
            logger.error("Failed to identify the plant, no result from Plant ID API")
            await update.message.reply_text("Failed to identify the plant. Please try again.")

        await self.show_main_menu(update)


def main():
    config = Config('config.xml')
    authenticator = Authenticator(config.base_url)
    api_client = APIClient(config)
    job_queue = JobQueue()
    application = Application.builder().token(config.token).job_queue(job_queue).build()

    notification_manager = NotificationManager(application)
    bot = IoTBot(config, authenticator, api_client, notification_manager)

    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_photo))  # Handle plant photos

    application.run_polling()


if __name__ == "__main__":
    main()

