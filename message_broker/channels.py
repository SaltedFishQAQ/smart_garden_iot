from constants.const import MESSAGE_BROKER_BASE_PATH as _PREFIX

# between device and service
DEVICE_DATA = _PREFIX + "device/data/"  # channel for data transmission
DEVICE_COMMAND = _PREFIX + "device/command/"  # channel for device command
DEVICE_OPERATION = _PREFIX + "device/operation/"  # channel for device operation

# between service and database
STORAGE_DATA = _PREFIX + "storage/data/"  # channel for data storage
STORAGE_OPERATION = _PREFIX + "storage/operation/"  # channel for operation storage
