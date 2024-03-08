#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import json
import socket
import threading

class PM_HA_Link:
    TIMEOUT = 5

    def __init__(self, node_name, discovery_perfix="homeassistant", config=None, get_logger=None):
        if get_logger is None:
            import logging
            get_logger = logging.getLogger
        self.log = get_logger(__name__)

        self.node_name = node_name
        self.node_id = node_name.lower().replace(' ', '_').replace('-', '_')
        self.discovery_perfix = discovery_perfix
        self.update_config(config)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.entities = {}
        self.__read_sensor__ = lambda: {}

        self.config_changed = False
        self.setters = {}
        self.preset_mode = "normal"
        self.connected = None
        self.thread = None
        self.running = False

    def update_config(self, config):
        if 'host' in config:
            if not isinstance(config['host'], str):
                self.log.error("Invalid host")
            else:
                self.host = config['host']
        if 'port' in config:
            if not isinstance(config['port'], int):
                self.log.error("Invalid port")
            else:
                self.port = config['port']
        if 'username' in config:
            if not isinstance(config['username'], str):
                self.log.error("Invalid username")
            else:
                self.username = config['username']
        if 'password' in config:
            if not isinstance(config['password'], str):
                self.log.error("Invalid password")
            else:
                self.password = config['password']
        if 'update_interval' in config:
            if not isinstance(config['update_interval'], (int, float)):
                self.log.error("Invalid update_interval")
            else:
                self.update_interval = config['update_interval']

    def connect(self):
        self.connected = None
        if (self.username != None and self.password != None):
            self.client.username_pw_set(self.username, self.password)
        try:
            self.client.connect(self.host, self.port)
        except socket.gaierror:
            self.log.warning(f"Connection Failed. Name or service not known: {self.host}:{self.port}")
            return False
        
        self.client.loop_start()
        timestart = time.time()
        while time.time() - timestart < self.TIMEOUT:
            if self.connected == True:
                self.log.info(f"Connected to broker")
                self.init()
                return True
            elif self.connected == False:
                self.log.warning(f"Connection Failed. Check username and password")
                return False
            time.sleep(1)
        self.log.warning(f"Connection Failed. Timeout")
        return False

    # upload configs:
    def init(self):
        for entity in self.entities.values():
            self.publish(entity["config_topic"], entity["config"])
            if "percentage_command_topic" in entity["config"]:
                topic = entity["config"]["percentage_command_topic"]
                self.client.subscribe(topic)
                self.setters[topic] = entity["set_percent"]
            if "command_topic" in entity["config"]:
                topic = entity["config"]["command_topic"]
                self.client.subscribe(topic)
                self.setters[topic] = entity["set_state"]
            if "preset_mode_command_topic" in entity["config"]:
                topic = entity["config"]["preset_mode_command_topic"]
                self.client.subscribe(topic)
                self.setters[topic] = entity["set_preset_mode"]
            time.sleep(0.1)

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print(f"Connection Failed.")
            self.connected = False
        else:
            print(f"Connected to broker")
            self.connected = True
    
    def on_message(self, client, userdata, msg):
        if msg.topic in self.setters:
            self.setters[msg.topic](msg.payload.decode())

    def add_entity(self,
        component=None,
        name=None,
        device_class=None,
        unit_of_measurement=None,
        get_state=None,
        set_state=None,
        get_percent=None,
        set_percent=None,
        get_preset_mode=None,
        set_preset_mode=None,
        preset_modes=None):

        id = name.lower().replace(' ', '_')
        name = f"{self.node_name} {name}"
        entity_id = f"{self.node_id}_{id}"
        config_topic = f"{self.discovery_perfix}/{component}/{self.node_id}/{id}/config"
        topic_prefix = f"{self.discovery_perfix}/{self.node_id}/{id}"
        state_topic = f"{topic_prefix}/state"
        availability_topic = f"{topic_prefix}/availability"
        percent_topic = f"{topic_prefix}/percent"
        command_topic = f"{topic_prefix}/set"
        percent_command_topic = f"{topic_prefix}/set_percent"
        preset_mode_state_topic = f"{topic_prefix}/preset_mode"
        preset_mode_command_topic = f"{topic_prefix}/set_preset_mode"

        data = {
            "component": component,
            "config_topic": config_topic,
            "config": {
                "name": name,
                "unique_id": f"{entity_id}",
                "state_topic": state_topic,
                "value_template": "{{ value_json.state }}",
                "state_value_template": "{{ value_json.state }}",
                "availability": {
                    "topic": availability_topic,
                    "value_template": "{{ value_json.state }}",
                }
            }
        }
        if device_class != None:
            data["config"]["device_class"] = device_class
        if unit_of_measurement != None:
            data["config"]["unit_of_measurement"] = unit_of_measurement
        if get_state != None:
            data["get_state"] = get_state
        if set_state != None:
            data["set_state"] = set_state
            data["config"]["command_topic"] = command_topic
        if get_percent != None:
            data["get_percent"] = get_percent
        if set_percent != None:
            data["set_percent"] = set_percent
            data["config"]["percentage_value_template"] = "{{ value_json.state }}"
            data["config"]["percentage_state_topic"] = percent_topic
            data["config"]["percentage_command_topic"] = percent_command_topic
        if get_preset_mode != None:
            data["get_preset_mode"] = get_preset_mode
        if set_preset_mode != None:
            data["set_preset_mode"] = set_preset_mode
        if preset_modes != None:
            data["config"]["preset_modes"] = preset_modes
            data["config"]["preset_modes_value_template"] = "{{ value_json.state }}"
            data["config"]["preset_mode_state_topic"] = preset_mode_state_topic
            data["config"]["preset_mode_command_topic"] = preset_mode_command_topic

        self.entities[id] = data

    def publish(self, topic, data):
        self.client.publish(topic, json.dumps(data))

    def publish_state(self, topic, state):
        self.publish(topic, {"state": state})

    def set_read_sensor(self, func):
        self.__read_sensor__ = func

    def run(self):
        result = self.__read_sensor__()
        for entity in self.entities.values():
            data = {}
            if "get_state" in entity:
                data["state"] = entity["get_state"](result)
            if "get_preset_mode" in entity:
                data["state"] = entity["get_preset_mode"](result)
            if "get_percent" in entity:
                data["state"] = entity["get_percent"](result)
            if len(data) > 0:
                self.publish(entity["config"]["state_topic"], data)
                self.publish(entity["config"]["availability"]["topic"], {"state": "online"})

    def loop(self):
        while self.running:
            while True:
                connected = self.connect()
                if connected:
                    break
                else:
                    self.log.error(f"Failed to start MQTT client")
                    while True:
                        time.sleep(self.update_interval)
                        if self.config_changed:
                            self.log.debug("MQTT client config updated, Trying to connect")
                            break

            self.log.info("Home Assistant MQTT client started")

            while True:
                self.run()
                time.sleep(self.update_interval)

    def start(self):
        if self.running:
            self.log.warning("Already running")
            return
        self.running = True
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()
        self.log.info("PM MQTT Helper Start")

    def stop(self):
        if not self.running:
            self.log.warning("Already stopped")
            return
        self.running = False
        self.thread.join()
        self.log.info("PM MQTT Helper Stop")
