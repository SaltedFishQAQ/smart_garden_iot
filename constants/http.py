from constants import entity

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
MYSQL_USER_LIST = MYSQL_BASE_ROUTE + entity.USER_TABLE
MYSQL_USER_LOGIN = MYSQL_BASE_ROUTE + entity.USER_TABLE + '/login' # user login
