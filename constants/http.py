import os
from constants import entity

SERVICE_HOST = "0.0.0.0"
INNER_SERVICE_HOST = "http://127.0.0.1"
MYSQL_HOST = "http://" + os.getenv('MYSQL_HOST', 'localhost')
INFLUX_HOST = "http://" + os.getenv('INFLUXDB_HOST', 'localhost')

#added for decision service
WEATHER_ADAPTER = "http://3.79.189.115"
BROKER_ADDRESS = "43.131.48.203"

# service port
SERVICE_PORT_AUTH = 8081
SERVICE_PORT_RULE = 8082
SERVICE_PORT_USER = 8083
SERVICE_PORT_INFLUX = 8084
SERVICE_PORT_MYSQL = 8085

# added for decision service
SERVICE_PORT_WEATHER = 5000
BROKER_PORT = 1883


# influx
INFLUX_BASE_ROUTE = '/influx/'
INFLUX_MEASUREMENT_LIST = INFLUX_BASE_ROUTE + "measurement"
INFLUX_DATA_GET = INFLUX_BASE_ROUTE + "data"
INFLUX_DATA_COUNT = INFLUX_BASE_ROUTE + "data/count"
INFLUX_OPERATION_GET = INFLUX_BASE_ROUTE + "operation"
# mysql
MYSQL_BASE_ROUTE = '/mysql/'
MYSQL_DEVICE_LIST = MYSQL_BASE_ROUTE + entity.DEVICE_TABLE  # get device list
MYSQL_DEVICE_CERTIFIED_LIST = MYSQL_BASE_ROUTE + entity.DEVICE_TABLE + '/certified'  # get certified device list
MYSQL_DEVICE_APPROVE = MYSQL_BASE_ROUTE + entity.DEVICE_TABLE + '/approve'  # approve device
MYSQL_DEVICE_RUNNING = MYSQL_BASE_ROUTE + entity.DEVICE_TABLE + '/running'  # change device running status
MYSQL_DEVICE_REGISTER = MYSQL_BASE_ROUTE + entity.DEVICE_TABLE + '/register'  # register device
MYSQL_DEVICE_COUNT = MYSQL_BASE_ROUTE + entity.DEVICE_TABLE + '/count'  # get amount of devices
MYSQL_USER_LIST = MYSQL_BASE_ROUTE + entity.USER_TABLE  # get user list
MYSQL_USER_LOGIN = MYSQL_BASE_ROUTE + entity.USER_TABLE + '/login'  # user login
MYSQL_USER_REGISTER = MYSQL_BASE_ROUTE + entity.USER_TABLE + '/register'  # user register
MYSQL_SERVICE_LIST = MYSQL_BASE_ROUTE + entity.SERVICE_TABLE  # get service list
MYSQL_SERVICE_REGISTER = MYSQL_BASE_ROUTE + entity.SERVICE_TABLE + '/register'  # register service
MYSQL_RULE_LIST = MYSQL_BASE_ROUTE + entity.RULE_TABLE  # get rule list
MYSQL_RULE_COUNT = MYSQL_BASE_ROUTE + entity.RULE_TABLE + '/count'  # get amount of rules
MYSQL_RULE_SAVE = MYSQL_BASE_ROUTE + entity.RULE_TABLE + '/save'  # save rule list
MYSQL_RULE_RUNNING = MYSQL_BASE_ROUTE + entity.RULE_TABLE + '/running'  # change rule running status
MYSQL_SCHEDULE_LIST = MYSQL_BASE_ROUTE + entity.SCHEDULE_TABLE  # get schedule list
MYSQL_SCHEDULE_COUNT = MYSQL_BASE_ROUTE + entity.SCHEDULE_TABLE + '/count'  # get amount of schedules
MYSQL_SCHEDULE_SAVE = MYSQL_BASE_ROUTE + entity.SCHEDULE_TABLE + '/save'  # save schedule list
MYSQL_SCHEDULE_RUNNING = MYSQL_BASE_ROUTE + entity.SCHEDULE_TABLE + '/running'  # change schedule running status
MYSQL_AREA_LIST = MYSQL_BASE_ROUTE + entity.AREA_TABLE
MYSQL_AREA_SAVE = MYSQL_BASE_ROUTE + entity.AREA_TABLE + '/save'
# user
USER_BASE_ROUTE = '/'
USER_DATA_ENTITY_LIST = USER_BASE_ROUTE + 'data/entities'
USER_DATA_GET = USER_BASE_ROUTE + 'data'
USER_DATA_COUNT = USER_BASE_ROUTE + 'data/count'
USER_OPERATION_GET = USER_BASE_ROUTE + 'operation'
USER_MEASUREMENT_LIST = USER_BASE_ROUTE + 'measurement'
USER_DATA_TEMPERATURE = USER_BASE_ROUTE + 'data/temperature'
USER_DATA_HUMIDITY = USER_BASE_ROUTE + 'data/humidity'
USER_DATA_LIGHT = USER_BASE_ROUTE + 'data/light'
USER_DATA_MOCK = USER_BASE_ROUTE + 'data/mock'
USER_DEVICE_RUNNING = USER_BASE_ROUTE + 'device/running'
USER_DEVICE_COMMAND = USER_BASE_ROUTE + 'device/command/send'
USER_DEVICE_APPROVE = USER_BASE_ROUTE + 'device/approve'
USER_DEVICE_STATUS = USER_BASE_ROUTE + 'device/status'
USER_CATALOG_SERVICE = USER_BASE_ROUTE + 'catalog/services'
USER_CATALOG_DEVICE = USER_BASE_ROUTE + 'catalog/devices'
USER_CATALOG_DEVICE_COUNT = USER_BASE_ROUTE + 'catalog/devices/count'
USER_RULE_LIST = USER_BASE_ROUTE + 'rules'
USER_RULE_CREATE = USER_BASE_ROUTE + 'rules'
USER_RULE_UPDATE = USER_BASE_ROUTE + 'rules'
USER_RULE_COUNT = USER_BASE_ROUTE + 'rules/count'
USER_RULE_RUNNING = USER_BASE_ROUTE + 'rules/running'
USER_SCHEDULE_LIST = USER_BASE_ROUTE + 'schedules'
USER_SCHEDULE_CREATE = USER_BASE_ROUTE + 'schedules'
USER_SCHEDULE_UPDATE = USER_BASE_ROUTE + 'schedules'
USER_SCHEDULE_COUNT = USER_BASE_ROUTE + 'schedules/count'
USER_SCHEDULE_RUNNING = USER_BASE_ROUTE + 'schedules/running'
USER_LOGIN = USER_BASE_ROUTE + 'user/login'
USER_REGISTER = USER_BASE_ROUTE + 'user/register'
USER_LIST = USER_BASE_ROUTE + 'user'
USER_AREA_LIST = USER_BASE_ROUTE + 'area'
USER_AREA_CREATE = USER_BASE_ROUTE + 'area'
USER_AREA_UPDATE = USER_BASE_ROUTE + 'area'
# device
DEVICE_BASE_ROUTE = '/device/'
DEVICE_STATUS_GET = DEVICE_BASE_ROUTE + 'status'
# open weather map
WEATHER_BASE_ROUTE = '/weather/'
WEATHER_DATA_GET = WEATHER_BASE_ROUTE + 'data'
# Open Meteo
HISTORICAL_WEATHER_BASE_ROUTE = '/historical_weather/'

