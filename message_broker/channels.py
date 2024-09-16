from constants.const import MESSAGE_BROKER_BASE_PATH as _PREFIX

# between device and service
DEVICE_DATA = _PREFIX + "device/data/"  # channel for data transmission
DEVICE_COMMAND = _PREFIX + "device/command/"  # channel for device command

# between service and database
STORAGE_DATA = _PREFIX + "storage/"  # channel for data storage
