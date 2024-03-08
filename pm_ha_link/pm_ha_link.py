from .mqtt_client import MQTTClient
from spc.spc import SPC
import time

config = {
    "host": "192.168.18.205",
    "port": 1883,
    "username": "mqtt",
    "password": "mqtt",
}

class PMHALink:

    def __init__(self, name, config=None, get_logger=None):
        if get_logger is None:
            import logging
            get_logger = logging.getLogger
        self.log = get_logger(__name__)

        self.update_config(config)

        self.client = MQTTClient(name, config, get_logger)

        self.spc = SPC()
        if 'battery' in self.spc.device.peripherals:
            self.client.add_entity(
                component = "sensor",
                name = "Battery Voltage",
                device_class = "voltage",
                unit_of_measurement = "V",
                get_state = lambda data: data["battery_voltage"] / 1000,
            )
            self.client.add_entity(
                component = "sensor",
                name = "Battery Current",
                device_class = "current",
                unit_of_measurement = "A",
                get_state = lambda data: data["battery_current"] / 1000,
            )
            self.client.add_entity(
                component = "sensor",
                name = "Battery Percentage",
                device_class = "battery",
                unit_of_measurement = "%",
                get_state = lambda data: data["battery_percentage"],
            )
            self.client.add_entity(
                component = "binary_sensor",
                name = "Battery Charging",
                device_class = "battery_charging",
                get_state = lambda data: "ON" if data["is_charging"] else "OFF",
            )
            self.client.add_entity(
                component = "binary_sensor",
                name = "Battery Status",
                device_class = "battery_status",
                get_state = lambda data: "ON" if data["battery_percentage"] > 25 else "OFF",
            )
        if 'external_input' in self.spc.device.peripherals:
            self.client.add_entity(
                component = "sensor",
                name = "External Input Voltage",
                device_class = "voltage",
                unit_of_measurement = "V",
                get_state = lambda data: data["external_input_voltage"] / 1000,
            )
            self.client.add_entity(
                component = "sensor",
                name = "External Input Voltage",
                device_class = "voltage",
                unit_of_measurement = "V",
                get_state = lambda data: data["external_input_voltage"] / 1000,
            )
            self.client.add_entity(
                component = "binary_sensor",
                name = "External Plugged in",
                device_class = "plug",
                get_state = lambda data: "ON" if data["is_plugged_in"] > 3 else "OFF",
            )
        if 'raspberry_pi_power' in self.spc.device.peripherals:
            self.client.add_entity(
                component = "sensor",
                name = "Raspberry Pi Voltage",
                device_class = "voltage",
                unit_of_measurement = "V",
                get_state = lambda data: data["raspberry_pi_voltage"] / 1000,
            )
            self.client.add_entity(
                component = "sensor",
                name = "Raspberry Pi Current",
                device_class = "current",
                unit_of_measurement = "A",
                get_state = lambda data: data["raspberry_pi_current"] / 1000,
            )
        if 'power_source_sensor' in self.spc.device.peripherals:
            self.client.add_entity(
                component = "binary_sensor",
                name = "Power Source",
                device_class = "power",
                get_state = lambda data: data["power_source"],
            )
        if 'fan' in self.spc.device.peripherals:
            self.client.add_entity(
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
        self.client.set_read_sensor(self.spc.read_all)
    
    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    def update_config(self, config):
        self.client.update_config(config)




