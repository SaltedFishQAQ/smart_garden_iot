import nest_asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

nest_asyncio.apply()

# Read the configuration from config.xml (server address, paths, token, etc.)
import xml.etree.ElementTree as ET

tree = ET.parse('telegram_config.xml')
root = tree.getroot()

BASE_URL = root.find('server_address').text  # Fetch the server address from config.xml
TOKEN = root.find('token').text  # Fetch the bot token from config.xml

# API client functions
def fetch_data(endpoint, params):
    response = requests.get(f"{BASE_URL}{endpoint}", params=params)
    if response.status_code == 200:
        return response.json().get('list', [])
    else:
        return []

def get_temperature(start_at, end_at, device_name):
    endpoint = "/data/temperature/list"
    params = {
        'start_at': start_at,
        'end_at': end_at,
        'name': device_name
    }
    return fetch_data(endpoint, params)

def get_humidity(start_at, end_at, device_name):
    endpoint = "/data/humidity/list"
    params = {
        'start_at': start_at,
        'end_at': end_at,
        'name': device_name
    }
    return fetch_data(endpoint, params)

def get_light(start_at, end_at, device_name):
    endpoint = "/data/light/list"
    params = {
        'start_at': start_at,
        'end_at': end_at,
        'name': device_name
    }
    return fetch_data(endpoint, params)

def control_device(device_name, status):
    endpoint = "/device/running"
    data = {
        'name': device_name,
        'status': status
    }
    response = requests.post(f"{BASE_URL}{endpoint}", json=data)
    return response.status_code == 200

def get_rules():
    endpoint = "/rule/list"
    params = {}
    return fetch_data(endpoint, params)

def save_rule(rule):
    endpoint = "/rule/save"
    response = requests.post(f"{BASE_URL}{endpoint}", json=rule)
    return response.status_code == 200

def set_rule_status(rule_id, status):
    endpoint = "/rule/running"
    data = {
        'id': rule_id,
        'status': status
    }
    response = requests.post(f"{BASE_URL}{endpoint}", json=data)
    return response.status_code == 200

# Command handlers
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("Temperature", callback_data='temperature')],
        [InlineKeyboardButton("Humidity", callback_data='humidity')],
        [InlineKeyboardButton("Light", callback_data='light')],
        [InlineKeyboardButton("Rules", callback_data='rules')],
        [InlineKeyboardButton("Watering", callback_data='watering')],
        [InlineKeyboardButton("Status", callback_data='status')],
        [InlineKeyboardButton("Back to Main Menu", callback_data='main_menu')]  # Back to Main Menu button
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "IoT Smart Garden\n"
        "Developed by: \n - Wenxi Lai.\n - Nasrin Hayati \n - Davood Shaterzadeh\n"
        "Please choose an option:"
    )
    await update.message.reply_text(message, reply_markup=get_main_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'temperature':
        await temperature(update, context)
    elif query.data == 'humidity':
        await humidity(update, context)
    elif query.data == 'light':
        await light(update, context)
    elif query.data == 'turnon':
        await turnon(update, context)
    elif query.data == 'turnoff':
        await turnoff(update, context)
    elif query.data == 'rules':
        await rules(update, context)
    elif query.data == 'watering':
        await watering(update, context)
    elif query.data == 'status':
        await status(update, context)
    elif query.data == 'main_menu':
        await main_menu(update, context)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.message.reply_text("Back to main menu:", reply_markup=get_main_menu())

async def temperature(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start_at = '2024-05-10 00:00:00'
    end_at = '2024-05-10 23:59:59'
    device_name = 'device11'
    data = get_temperature(start_at, end_at, device_name)
    if not data:
        await update.callback_query.message.reply_text('Failed to retrieve temperature data.', reply_markup=get_main_menu())
    else:
        message = '\n'.join([f"{item['time']}: {item['value']}°C" for item in data])
        await update.callback_query.message.reply_text(f"Temperature data:\n{message}", reply_markup=get_main_menu())

async def humidity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start_at = '2024-05-10 00:00:00'
    end_at = '2024-05-10 23:59:59'
    device_name = 'device11'
    data = get_humidity(start_at, end_at, device_name)
    if not data:
        await update.callback_query.message.reply_text('Failed to retrieve humidity data.', reply_markup=get_main_menu())
    else:
        message = '\n'.join([f"{item['time']}: {item['value']}%" for item in data])
        await update.callback_query.message.reply_text(f"Humidity data:\n{message}", reply_markup=get_main_menu())

async def light(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Turn On", callback_data='turnon')],
        [InlineKeyboardButton("Turn Off", callback_data='turnoff')],
        [InlineKeyboardButton("Back to Main Menu", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Please choose an option:", reply_markup=reply_markup)

async def turnon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    device_name = 'device11'
    if control_device(device_name, 1):
        await update.callback_query.message.reply_text(f"{device_name} turned on.", reply_markup=get_main_menu())
    else:
        await update.callback_query.message.reply_text(f"Failed to turn on {device_name}.", reply_markup=get_main_menu())

async def turnoff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    device_name = 'device11'
    if control_device(device_name, 0):
        await update.callback_query.message.reply_text(f"{device_name} turned off.", reply_markup=get_main_menu())
    else:
        await update.callback_query.message.reply_text(f"Failed to turn off {device_name}.", reply_markup=get_main_menu())

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Add Rule", callback_data='addrule')],
        [InlineKeyboardButton("View Rules", callback_data='viewrules')],
        [InlineKeyboardButton("Back to Main Menu", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Please choose an option:", reply_markup=reply_markup)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.message.reply_text("Here are the status of the system.", reply_markup=get_main_menu())

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()
