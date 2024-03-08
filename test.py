from pm_ha_link.pm_ha_link import PM_HA_Link
from spc.spc import SPC
import time

config = {
    "host": "192.168.18.205",
    "port": 1883,
    "username": "mqtt",
    "password": "mqtt",
}

def test():
    spc = SPC()
    link = PM_HA_Link("test",
                                discovery_perfix="homeassistant",
                                config=config,
                                get_logger=None)

    link.add_entity(
        component = "sensor",
        name = "Battery Voltage",
        device_class = "voltage",
        unit_of_measurement = "V",
        get_state = lambda data: data["battery_voltage"] / 1000,
    )
    link.add_entity(
        component = "sensor",
        name = "Battery Current",
        device_class = "current",
        unit_of_measurement = "A",
        get_state = lambda data: data["battery_current"] / 1000,
    )
    link.add_entity(
        component = "sensor",
        name = "Battery Percentage",
        device_class = "battery",
        unit_of_measurement = "%",
        get_state = lambda data: data["battery_percentage"],
    )
    link.add_entity(
        component = "sensor",
        name = "External Input Voltage",
        device_class = "voltage",
        unit_of_measurement = "V",
        get_state = lambda data: data["external_input_voltage"] / 1000,
    )
    link.add_entity(
        component = "sensor",
        name = "Raspberry Pi Voltage",
        device_class = "voltage",
        unit_of_measurement = "V",
        get_state = lambda data: data["raspberry_pi_voltage"] / 1000,
    )
    link.add_entity(
        component = "sensor",
        name = "Raspberry Pi Current",
        device_class = "current",
        unit_of_measurement = "A",
        get_state = lambda data: data["raspberry_pi_current"] / 1000,
    )
    link.add_entity(
        component = "binary_sensor",
        name = "Power Source",
        device_class = "power",
        get_state = lambda data: data["power_source"],
    )
    link.add_entity(
        component = "binary_sensor",
        name = "Battery Charging",
        device_class = "battery_charging",
        get_state = lambda data: "ON" if data["is_charging"] else "OFF",
    )
    link.add_entity(
        component = "binary_sensor",
        name = "Battery Status",
        device_class = "battery_status",
        get_state = lambda data: "ON" if data["battery_percentage"] > 25 else "OFF",
    )
    link.add_entity(
        component = "binary_sensor",
        name = "External Plugged in",
        device_class = "plug",
        get_state = lambda data: "ON" if data["is_plugged_in"] > 3 else "OFF",
    )
    link.add_entity(
        component = "fan",
        name = "Fan",
        get_state = lambda data: "ON" if data["fan_state"] else "OFF",
        set_state = lambda data: spc.set_fan_state(data == "ON"),
        get_percent = lambda data: data["fan_speed"],
        set_percent = lambda data: spc.set_fan_speed(int(data)),
        get_preset_mode = lambda data: data["fan_state"],
        set_preset_mode = lambda data: print(data),
        preset_modes = ["auto", "quiet", "normal", "performance"],
    )
    link.set_read_sensor(spc.read_all)
    link.start()
    while True:
        time.sleep(1)
    
if __name__ == "__main__":
    test()




