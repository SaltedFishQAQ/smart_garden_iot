import nest_asyncio
import requests
import paho.mqtt.client as mqtt
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue
import xml.etree.ElementTree as ET
import json
import logging
import asyncio
from asyncio import run_coroutine_threadsafe
from authenticator import Authenticator
from notification import NotificationManager

logging.basicConfig(
    filename='/tmp/bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

nest_asyncio.apply()

#load configuration
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


# API Client class for fetching data and rules
class APIClient:
    def __init__(self, config: Config):
        self.base_url = config.base_url
        self.data_endpoint = config.data_endpoint  #temperature, humidity
        self.rules_endpoint = "/rules"
        self.status_endpoint = "/status"

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


# handling bot operations and MQTT communication
class IoTBot:
    def __init__(self, config: Config, authenticator: Authenticator, api_client: APIClient, notification_manager: NotificationManager):
        self.config = config
        self.authenticator = authenticator
        self.api_client = api_client
        self.notification_manager = notification_manager
        self.mqtt_client = mqtt.Client()
        self.loop = asyncio.get_event_loop()

        self.subscribed_users = set()

        # MQTT Connect
        try:
            logger.info("Connecting to MQTT broker...")
            self.mqtt_client.on_message = self.on_mqtt_message
            self.mqtt_client.connect(self.config.mqtt_broker, self.config.mqtt_port)
            self.mqtt_client.loop_start()
            logger.info(f"Connected to MQTT broker at {self.config.mqtt_broker}:{self.config.mqtt_port}")

            self.mqtt_client.subscribe(self.config.command_channel + "prediction")
            logger.info(f"Subscribed to topic: {self.config.command_channel}prediction")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

    def on_mqtt_message(self, client, userdata, msg):
        """Callback when a message is received from the MQTT broker"""
        try:
            payload_str = msg.payload.decode('utf-8')
            payload_str = payload_str.replace("'", '"')
            payload = json.loads(payload_str)
            prediction = payload.get('prediction', 'No prediction data.')
            logger.info(f"Received message from topic {msg.topic}: {prediction}")
            logger.info(f"Notifying all subscribed users: {self.subscribed_users}")
            run_coroutine_threadsafe(self.notification_manager.notify_users(prediction), self.loop)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MQTT message: {e}")
        except Exception as e:
            logger.error(f"Error in on_mqtt_message: {e}")

    def mqtt_publish(self, topic, message):
        """Publish function"""
        try:
            logger.info(f"Publishing to {topic}: {message}")
            result = self.mqtt_client.publish(topic, json.dumps(message))
            result.wait_for_publish()  # Make sure the message is sent
            logger.info(f"Published to {topic} with message: {message}")
        except Exception as e:
            logger.error(f"Failed to publish to MQTT: {e}")

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
        if user_id not in self.subscribed_users:
            logger.info(f"Subscribing user {user_id} to notifications...")
            self.subscribed_users.add(user_id)
            logger.info(f"User {user_id} subscribed to notifications. Subscribed users: {self.subscribed_users}")
        else:
            logger.info(f"User {user_id} is already subscribed.")

        logger.info(f"Registering user {user_id} in NotificationManager.")
        self.notification_manager.register_user(user_id)

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
            self.mqtt_publish(self.config.command_channel + 'irrigator', {"type": "opt", 'status': True})
            await update.message.reply_text("Watering system turned on.")
        elif text == "Turn Off Watering":
            self.mqtt_publish(self.config.command_channel + 'irrigator', {"type": "opt", 'status': False})
            await update.message.reply_text("Watering system turned off.")
        elif text == "Turn On Light":
            self.mqtt_publish(self.config.command_channel + 'light', {"type": "opt", 'status': True})
            await update.message.reply_text("Light turned on.")
        elif text == "Turn Off Light":
            self.mqtt_publish(self.config.command_channel + 'light', {"type": "opt", 'status': False})
            await update.message.reply_text("Light turned off.")
        elif text == "Back to Main Menu":
            await self.show_main_menu(update)
        else:
            await update.message.reply_text("Invalid command.")

    async def show_main_menu(self, update: Update):
        keyboard = [
            [KeyboardButton("Temperature"), KeyboardButton("Humidity")],
            [KeyboardButton("Light"), KeyboardButton("View Rules")],
            [KeyboardButton("Watering"), KeyboardButton("Status")]
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

    application.run_polling()


if __name__ == "__main__":
    main()


