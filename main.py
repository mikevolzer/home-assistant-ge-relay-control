import paho.mqtt.client as mqtt
import time
import json
import serial


RELAY_DELAY_TIME_MS = 100.0
BROKER_HOST = "127.0.0.1"


class Relay:
    def __init__(self, gpio_on, gpio_off):
        self.gpio_on = gpio_on
        self.gpio_off = gpio_off

    def set_state(self, state):
        pin_to_pulse = self.gpio_on if state else self.gpio_off
        arduino.write(f'<{pin_to_pulse}>'.encode())


arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=0.1)
time.sleep(0.1)
if arduino.isOpen():
    print(f'{arduino.port} connected!')

relays = {}
with open('config.json', 'r') as f:
    config = json.load(f)
    RELAY_DELAY_TIME_MS = config["delay_time_ms"]
    BROKER_HOST = config["broker"]
    for relay in config["relays"]:
        relays[relay["id"]] = Relay(relay["gpio_on"], relay["gpio_off"])


def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code "+str(rc))
    client.subscribe("switch/+/set")


def on_message(client, userdata, msg):
    print(f'{msg.topic} {str(msg.payload)}')

    # command_topic: "switch/1/set"
    try:
        topic_path = msg.topic.split("/")
        if topic_path[0] == "switch":
            switch_number = topic_path[1]
            if topic_path[2] == "set":
                state = msg.payload.decode("UTF-8") == "ON"
                relays[switch_number].set_state(state)

    except IndexError:
        # Ignore index exceptions rather than check if the relay id is valid.
        pass


if __name__ == '__main__':
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(BROKER_HOST, 1883, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        client.disconnect()
        arduino.close()
