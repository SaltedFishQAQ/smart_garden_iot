import os
from constants import entity

SERVICE_HOST = "0.0.0.0"
INNER_SERVICE_HOST = "http://127.0.0.1"
MYSQL_HOST = "http://" + os.getenv('MYSQL_HOST', 'localhost')
INFLUX_HOST = "http://" + os.getenv('INFLUXDB_HOST', 'localhost')
# service port
SERVICE_PORT_USER = 8083
SERVICE_PORT_INFLUX = 8084
SERVICE_PORT_MYSQL = 8085

# influx
INFLUX_BASE_ROUTE = '/influx/'
INFLUX_TEMPERATURE_GET = INFLUX_BASE_ROUTE + entity.TEMPERATURE
INFLUX_HUMIDITY_GET = INFLUX_BASE_ROUTE + entity.HUMIDITY
INFLUX_LIGHT_GET = INFLUX_BASE_ROUTE + entity.LIGHT
INFLUX_GATE_GET = INFLUX_BASE_ROUTE + entity.GATE
INFLUX_IRRIGATOR_GET = INFLUX_BASE_ROUTE + entity.IRRIGATOR
# mysql
MYSQL_BASE_ROUTE = '/mysql/'
MYSQL_DEVICE_LIST = MYSQL_BASE_ROUTE + entity.DEVICE_TABLE  # get device list
MYSQL_DEVICE_CERTIFIED_LIST = MYSQL_BASE_ROUTE + entity.DEVICE_TABLE + '/certified'  # get certified device list
MYSQL_DEVICE_RUNNING = MYSQL_BASE_ROUTE + entity.DEVICE_TABLE + '/running'  # change device running status
MYSQL_USER_LIST = MYSQL_BASE_ROUTE + entity.USER_TABLE  # get user list
MYSQL_USER_LOGIN = MYSQL_BASE_ROUTE + entity.USER_TABLE + '/login'  # user login
MYSQL_USER_REGISTER = MYSQL_BASE_ROUTE + entity.USER_TABLE + '/register'  # user register
MYSQL_SERVICE_LIST = MYSQL_BASE_ROUTE + entity.SERVICE_TABLE  # get service list
MYSQL_SERVICE_REGISTER = MYSQL_BASE_ROUTE + entity.SERVICE_TABLE + 'register'  # register service
MYSQL_RULE_LIST = MYSQL_BASE_ROUTE + entity.RULE_TABLE  # get rule list
MYSQL_RULE_SAVE = MYSQL_BASE_ROUTE + entity.RULE_TABLE + '/save'  # save rule list
MYSQL_RULE_RUNNING = MYSQL_BASE_ROUTE + entity.RULE_TABLE + '/running'  # change rule running status
# user
USER_BASE_ROUTE = '/'
USER_DATA_ENTITY_LIST = USER_BASE_ROUTE + 'data/entity/list'
USER_DATA_TEMPERATURE = USER_BASE_ROUTE + 'data/temperature/list'
USER_DATA_HUMIDITY = USER_BASE_ROUTE + 'data/humidity/list'
USER_DATA_LIGHT = USER_BASE_ROUTE + 'data/light/list'
USER_DATA_MOCK = USER_BASE_ROUTE + 'data/mock'
USER_DEVICE_RUNNING = USER_BASE_ROUTE + 'device/running'
USER_DEVICE_COMMAND = USER_BASE_ROUTE + 'device/command/send'
USER_CATALOG_SERVICE = USER_BASE_ROUTE + 'catalog/service/list'
USER_CATALOG_DEVICE = USER_BASE_ROUTE + 'catalog/device/list'
USER_RULE_LIST = USER_BASE_ROUTE + 'rule/list'
USER_RULE_SAVE = USER_BASE_ROUTE + 'rule/save'
USER_RULE_RUNNING = USER_BASE_ROUTE + 'rule/running'
USER_LOGIN = USER_BASE_ROUTE + 'user/login'
USER_REGISTER = USER_BASE_ROUTE + 'user/register'
