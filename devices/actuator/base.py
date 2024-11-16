from devices.actuator import gate_switch, irrigator, light_switch, oxygen_valve


def get_actuator(params):
    name = params['actuator']
    if name == gate_switch.TAG:
        return gate_switch.GateSwitch()
    elif name == irrigator.TAG:
        return irrigator.Irrigator()
    elif name == light_switch.TAG:
        return light_switch.LightSwitch()
    elif name == oxygen_valve.TAG:
        return oxygen_valve.OxygenValve()
    else:
        return None
