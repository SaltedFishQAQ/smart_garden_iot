from devices.sensor import gas, humidity, light, soil_moisture, temperature


def get_sensor(params):
    name = params['sensor']
    if name == gas.TAG:
        return gas.GasDetector()
    elif name == humidity.TAG:
        return humidity.HumiditySensor()
    elif name == light.TAG:
        return light.LightSensor()
    elif name == soil_moisture.TAG:
        return soil_moisture.SoilMoistureSensor(params['soil_type'])
    elif name == temperature.TAG:
        return temperature.TemperatureSensor()
    else:
        return None
