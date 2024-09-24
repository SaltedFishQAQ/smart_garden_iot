import nest_asyncio
import requests
import xml.etree.ElementTree as ET
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

nest_asyncio.apply()

# Load configuration from config.xml
tree = ET.parse('config.xml')
root = tree.getroot()

BASE_URL = root.find('server/address').text
API_ENDPOINTS = {
    'temperature': root.find('api/temperature').text,
    'humidity': root.find('api/humidity').text,
    'light': root.find('api/light').text,
    'control': root.find('api/control').text,
    'rules': root.find('api/rules').text,
    'save_rule': root.find('api/save_rule').text,
    'set_rule_status': root.find('api/set_rule_status').text,
}
BOT_TOKEN = root.find('bot/token').text

# API
def fetch_data(endpoint, params):
    response = requests.get(f"{BASE_URL}{endpoint}", params=params)
    if response.status_code == 200:
        return response.json().get('list', [])
    else:
        return []

def get_temperature(start_at, end_at, device_name):
    return fetch_data(API_ENDPOINTS['temperature'], {
        'start_at': start_at,
        'end_at': end_at,
        'name': device_name
    })

def get_humidity(start_at, end_at, device_name):
    return fetch_data(API_ENDPOINTS['humidity'], {
        'start_at': start_at,
        'end_at': end_at,
        'name': device_name
    })

def get_light(start_at, end_at, device_name):
    return fetch_data(API_ENDPOINTS['light'], {
        'start_at': start_at,
        'end_at': end_at,
        'name': device_name
    })

def control_device(device_name, status):
    response = requests.post(f"{BASE_URL}{API_ENDPOINTS['control']}", json={
        'name': device_name,
        'status': status
    })
    return response.status_code == 200

def get_rules():
    return fetch_data(API_ENDPOINTS['rules'], {})

def save_rule(rule):
    response = requests.post(f"{BASE_URL}{API_ENDPOINTS['save_rule']}", json=rule)
    return response.status_code == 200

def set_rule_status(rule_id, status):
    response = requests.post(f"{BASE_URL}{API_ENDPOINTS['set_rule_status']}", json={
        'id': rule_id,
        'status': status
    })
    return response.status_code == 200

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Temperature", callback_data='temperature')],
        [InlineKeyboardButton("Humidity", callback_data='humidity')],
        [InlineKeyboardButton("Light", callback_data='light')],
        [InlineKeyboardButton("Watering", callback_data='watering')],
        [InlineKeyboardButton("Rules", callback_data='rules')],
        [InlineKeyboardButton("Status", callback_data='status')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("IoT Smart Garden - Choose an option:", reply_markup=reply_markup)


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()

