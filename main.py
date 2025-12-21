import paho.mqtt.client as mqtt
import time
import json
import serial


RELAY_DELAY_TIME_MS = 100.0
BROKER_HOST = "127.0.0.1"
USERNAME = ""
PASSWORD = ""

ROOT_TOPIC = "homeassistant/light"
AVAILABLE_TOPIC = f"{ROOT_TOPIC}/available"


class Relay:
    def __init__(self, name: str, description: str, area: str, gpio_on: int, gpio_off: int):
        self.name = name
        self.description = description
        self.area = area
        self.gpio_on = gpio_on
        self.gpio_off = gpio_off

    def set_state(self, state: bool):
        pin_to_pulse = self.gpio_on if state else self.gpio_off
        arduino.write(f'<{pin_to_pulse}>'.encode())
        time.sleep(0.2)


arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=0.1)
time.sleep(0.1)
if arduino.isOpen():
    print(f'{arduino.port} connected!')

relays = {}
with open('config.json', 'r') as f:
    config = json.load(f)
    RELAY_DELAY_TIME_MS = config["delay_time_ms"]
    BROKER_HOST = config["broker"]
    USERNAME = config["username"]
    PASSWORD = config["password"]

    for relay in config["relays"]:
        try:
            area = relay["area"]
        except KeyError:
            area = ""

        relays[f"relay_{relay['id']}"] = Relay(
            relay["id"], relay["description"], area, relay["gpio_on"], relay["gpio_off"])


def publish_homeassistant_config_info(client: mqtt.Client):
    print("Publishing Home Assistant config info")
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
    # if not reason_code.is_failure:
    print("Connection to MQTT broker succeeded")
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
                print(f'{msg.topic} {str(msg.payload)}')

    except (KeyError, IndexError):
        pass


if __name__ == '__main__':
    try:
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message

        client.username_pw_set(USERNAME, PASSWORD)
        client.will_set(AVAILABLE_TOPIC, "offline", 0, False)
        client.connect(BROKER_HOST, 1883, 60)
        client.loop_forever()

    except (KeyboardInterrupt, OSError):
        client.publish(AVAILABLE_TOPIC, "offline")
        client.disconnect()
        arduino.close()
