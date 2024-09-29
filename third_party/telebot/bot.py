import nest_asyncio
import requests
import paho.mqtt.client as mqtt
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import xml.etree.ElementTree as ET
import json
import logging

# Enable logging to file
logging.basicConfig(
    filename='/tmp/bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

nest_asyncio.apply()

# Config Class to Read XML
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

# API Client Class
class APIClient:
    def __init__(self, config: Config):
        self.base_url = config.base_url

    def fetch_data(self, endpoint, params):
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()
        return {}

# Bot Handler Class
class IoTBot:
    def __init__(self, config: Config, api_client: APIClient):
        self.config = config
        self.api_client = api_client
        self.mqtt_client = mqtt.Client()

        # MQTT Connect
        try:
            logger.info("Connecting to MQTT broker...")
            self.mqtt_client.connect(self.config.mqtt_broker, self.config.mqtt_port)
            self.mqtt_client.loop_start()
            logger.info(f"Connected to MQTT broker at {self.config.mqtt_broker}:{self.config.mqtt_port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

    def mqtt_publish(self, topic, message):
        """Simplified MQTT publish function"""
        try:
            logger.info(f"Publishing to {topic}: {message}")
            result = self.mqtt_client.publish(topic, json.dumps(message))
            result.wait_for_publish()  # Make sure the message is sent
            logger.info(f"Published to {topic} with message: {message}")
        except Exception as e:
            logger.error(f"Failed to publish to MQTT: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self.show_main_menu(update)

    async def show_main_menu(self, update: Update):
        keyboard = [
            [KeyboardButton("Temperature"), KeyboardButton("Humidity")],
            [KeyboardButton("Light"), KeyboardButton("Rules")],
            [KeyboardButton("Watering"), KeyboardButton("Status")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
        await update.message.reply_text("Please choose an option:", reply_markup=reply_markup)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = update.message.text
        logger.info(f"Received message: {text}")

        if text == "Temperature":
            await self.get_temperature(update)
        elif text == "Humidity":
            await self.get_humidity(update)
        elif text == "Light":
            await self.light_menu(update)
        elif text == "Rules":
            await self.rules_menu(update)
        elif text == "Watering":
            await self.watering_menu(update)
        elif text == "Status":
            await self.status(update)
        elif text == "Turn On Watering":
            self.mqtt_publish(self.config.command_channel + 'irrigator', {'status': True})
            await update.message.reply_text("Watering system turned on.")
        elif text == "Turn Off Watering":
            self.mqtt_publish(self.config.command_channel + 'irrigator', {'status': False})
            await update.message.reply_text("Watering system turned off.")
        elif text == "Turn On Light":
            self.mqtt_publish(self.config.command_channel + 'luminance', {'status': True})
            await update.message.reply_text("Light turned on.")
        elif text == "Turn Off Light":
            self.mqtt_publish(self.config.command_channel + 'luminance', {'status': False})
            await update.message.reply_text("Light turned off.")
        elif text == "Back to Main Menu":
            await self.show_main_menu(update)  # Call the main menu function to return to main menu
        else:
            await update.message.reply_text("Invalid command.")

    async def get_temperature(self, update: Update):
        params = {
            'page': 1,
            'size': 10,
            'start_at': '2024-09-01 00:00:00'
        }
        data = self.api_client.fetch_data("/data/temperature", params=params)

        if 'list' in data:
            temp_list = data['list']
            message = '\n'.join([f"{item.get('time', 'N/A')}: {item.get('value', 'N/A')}°C" for item in temp_list])
            await update.message.reply_text(f"Temperature data:\n{message}")
        else:
            await update.message.reply_text("No temperature data available.")

    async def get_humidity(self, update: Update):
        data = self.api_client.fetch_data("/data/humidity/list", params={})
        message = '\n'.join([f"{item.get('time', 'N/A')}: {item.get('value', 'N/A')}%" for item in data])
        await update.message.reply_text(f"Humidity data:\n{message}")

    async def light_menu(self, update: Update):
        keyboard = [
            [KeyboardButton("Turn On Light"), KeyboardButton("Turn Off Light")],
            [KeyboardButton("Back to Main Menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
        await update.message.reply_text("Control the light:", reply_markup=reply_markup)

    async def rules_menu(self, update: Update):
        keyboard = [
            [KeyboardButton("Add Rule"), KeyboardButton("View Rules")],
            [KeyboardButton("Back to Main Menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
        await update.message.reply_text("Manage rules:", reply_markup=reply_markup)

    async def status(self, update: Update):
        await update.message.reply_text("Here are the status of the system.")

    async def watering_menu(self, update: Update):
        keyboard = [
            [KeyboardButton("Turn On Watering"), KeyboardButton("Turn Off Watering")],
            [KeyboardButton("Back to Main Menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
        await update.message.reply_text("Control the watering system:", reply_markup=reply_markup)

# Main Application Runner
def main():
    config = Config('config.xml')
    api_client = APIClient(config)
    bot = IoTBot(config, api_client)
    application = Application.builder().token(config.token).build()

    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()


