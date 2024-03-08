

class Entity:
    def __init__(self,
                 discovery_perfix,
                 node_name,
                 component,
                 name,
                 device_class=None,
                 unit_of_measurement=None,
                 get_state=None,
                 set_state=None,
                 get_percent=None,
                 set_percent=None,
                 get_preset_mode=None,
                 set_preset_mode=None,
                 preset_modes=None
                 ) -> None:
        self.discovery_perfix = discovery_perfix
        self.component = component
        self.id = name.lower().replace(' ', '_')
        self.node_name = node_name
        self.node_id = node_name.lower().replace(' ', '_').replace('-', '_')
        self.name = f"{self.node_name} {name}"
        self.entity_id = f"{self.node_id}_{id}"
        self.device_class = device_class
        self.unit_of_measurement = unit_of_measurement
        self.get_state = get_state
        self.set_state = set_state
        self.get_percent = get_percent
        self.set_percent = set_percent
        self.get_preset_mode = get_preset_mode
        self.set_preset_mode = set_preset_mode
        self.preset_modes = preset_modes

        self.config_topic = f"{self.discovery_perfix}/{self.component}/{self.node_id}/{self.id}/config"
        self.topic_prefix = f"{self.discovery_perfix}/{self.node_id}/{self.id}"
        self.state_topic = f"{self.topic_prefix}/state"
        self.availability_topic = f"{self.topic_prefix}/availability"
        self.percent_topic = f"{self.topic_prefix}/percent"
        self.command_topic = f"{self.topic_prefix}/set"
        self.percent_command_topic = f"{self.topic_prefix}/set_percent"
        self.preset_mode_state_topic = f"{self.topic_prefix}/preset_mode"
        self.preset_mode_command_topic = f"{self.topic_prefix}/set_preset_mode"

        self.create_entity()
    
    def create_entity(self) -> None:
        data = {
            "component": self.component,
            "config_topic": self.config_topic,
            "config": {
                "name": self.name,
                "unique_id": f"{self.entity_id}",
                "state_topic": self.state_topic,
                "value_template": "{{ value_json.state }}",
                "state_value_template": "{{ value_json.state }}",
                "availability": {
                    "topic": self.availability_topic,
                    "value_template": "{{ value_json.state }}",
                }
            }
        }
        if self.device_class != None:
            data["config"]["device_class"] = self.device_class
        if self.unit_of_measurement != None:
            data["config"]["unit_of_measurement"] = self.unit_of_measurement
        if self.get_state != None:
            data["get_state"] = self.get_state
        if self.set_state != None:
            data["set_state"] = self.set_state
            data["config"]["command_topic"] = self.command_topic
        if self.get_percent != None:
            data["get_percent"] = self.get_percent
        if self.set_percent != None:
            data["set_percent"] = self.set_percent
            data["config"]["percentage_value_template"] = "{{ value_json.state }}"
            data["config"]["percentage_state_topic"] = self.percent_topic
            data["config"]["percentage_command_topic"] = self.percent_command_topic
        if self.get_preset_mode != None:
            data["get_preset_mode"] = self.get_preset_mode
        if self.set_preset_mode != None:
            data["set_preset_mode"] = self.set_preset_mode
        if self.preset_modes != None:
            data["config"]["preset_modes"] = self.preset_modes
            data["config"]["preset_modes_value_template"] = "{{ value_json.state }}"
            data["config"]["preset_mode_state_topic"] = self.preset_mode_state_topic
            data["config"]["preset_mode_command_topic"] = self.preset_mode_command_topic