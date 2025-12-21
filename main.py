import paho.mqtt.client as mqtt
import time
import json
import serial
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


RELAY_DELAY_TIME_MS = 100.0
BROKER_HOST = "127.0.0.1"
USERNAME = ""
PASSWORD = ""

ROOT_TOPIC = "homeassistant/light"
AVAILABLE_TOPIC = f"{ROOT_TOPIC}/available"


class ArduinoInterface(ABC):
    @abstractmethod
    def send_command(self, pin: int):
        pass

    def close(self):
        pass


class SerialArduino(ArduinoInterface):
    def __init__(self, port: str, baudrate: int):
        self.serial = serial.Serial(port, baudrate, timeout=0.1)
        time.sleep(0.1)
        if self.serial.isOpen():
            logging.info(f'{self.serial.port} connected!')
        else:
            logging.warning(f'Failed to connect to Arduino on {port}')

    def send_command(self, pin: int):
        self.serial.write(f'<{pin}>'.encode())
        time.sleep(0.2)

    def close(self):
        self.serial.close()


class MockArduino(ArduinoInterface):
    def send_command(self, pin: int):
        logging.info(f"Mock: Sending command to pin {pin}")


class Relay:
    def __init__(self, name: str, description: str, area: str, gpio_on: int, gpio_off: int, arduino_interface: ArduinoInterface):
        self.name = name
        self.description = description
        self.area = area
        self.gpio_on = gpio_on
        self.gpio_off = gpio_off
        self.arduino_interface = arduino_interface

    def set_state(self, state: bool):
        pin_to_pulse = self.gpio_on if state else self.gpio_off
        self.arduino_interface.send_command(pin_to_pulse)

relays = {}
arduino_interface = None
with open('config.json', 'r') as f:
    config = json.load(f)
    RELAY_DELAY_TIME_MS = config["delay_time_ms"]
    BROKER_HOST = config["broker"]
    USERNAME = config["username"]
    PASSWORD = config["password"]

    
    try:
        arduino_interface = SerialArduino("/dev/ttyACM0", 115200)
    except serial.SerialException:
        arduino_interface = MockArduino()

    for relay in config["relays"]:
        try:
            area = relay["area"]
        except KeyError:
            area = ""

        relays[f"relay_{relay['id']}"] = Relay(
            relay["id"], relay["description"], area, relay["gpio_on"], relay["gpio_off"], arduino_interface)


def publish_homeassistant_config_info(client: mqtt.Client):
    logging.info("Publishing Home Assistant config info")
    for id, relay in relays.items():
        config = {
            "~": f"{ROOT_TOPIC}/{id}",
            "unique_id": id,
            "object_id": id,
            "availability": {
                "topic": f"{AVAILABLE_TOPIC}"
            },
            "name": relay.description if relay.description else id,
            "command_topic": "~/switch",
        }


        client.publish(f"{ROOT_TOPIC}/{id}/config", json.dumps(config), 1)


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        logging.error(f"Failed to connect to MQTT broker: {reason_code}")
        return
    logging.info(f"Connected to MQTT broker: {reason_code}")
    publish_homeassistant_config_info(client)

    client.publish(f"{ROOT_TOPIC}/available", "online", 1, True)
    client.subscribe(f"{ROOT_TOPIC}/+/switch")


def on_message(client: mqtt.Client, userdata, msg):
    # command_topic: "homeassistant/light/relay_1/set"
    try:
        topic_path = msg.topic.split("/")
        if topic_path[1] == "light":
            relay_id = topic_path[2]
            if topic_path[3] == "switch":
                state = msg.payload.decode("UTF-8") == "ON"
                relays[relay_id].set_state(state)
                logging.info(f'{msg.topic} {str(msg.payload)}')

    except (KeyError, IndexError):
        logging.warning(f"Invalid message topic or payload: {msg.topic} {str(msg.payload)}")


if __name__ == '__main__':
    try:
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message

        client.username_pw_set(USERNAME, PASSWORD)
        client.will_set(AVAILABLE_TOPIC, "offline", 0, False)
        client.connect(BROKER_HOST, 1883, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, shutting down")
        client.publish(AVAILABLE_TOPIC, "offline")
        client.disconnect()
        arduino_interface.close()
    except OSError as e:
        logging.error(f"OS error occurred: {e}")
        client.publish(AVAILABLE_TOPIC, "offline")
        client.disconnect()
        arduino_interface.close()
