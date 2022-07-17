import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import time
import json

RELAY_DELAY_TIME_MS = 100.0
BROKER_HOST = "127.0.0.1"


class Relay:
    def __init__(self, gpio_on, gpio_off):
        self.gpio_on = gpio_on
        self.gpio_off = gpio_off

        gpio.setup(self.gpio_on, gpio.OUT)
        gpio.setup(self.gpio_off, gpio.OUT)

    def set_state(self, state):
        pin_to_pulse = self.gpio_on if state else self.gpio_off
        gpio.output(pin_to_pulse, True)
        time.sleep(RELAY_DELAY_TIME_MS / 1000.0)
        gpio.output(pin_to_pulse, False)


gpio.setmode(gpio.BOARD)

# Set up all the relays
relays = {}

with open('config.json', 'r') as f:
    config = json.load(f)
    RELAY_DELAY_TIME_MS = config["delay_time_ms"]
    BROKER_HOST = config["broker"]
    for relay in config["relays"]:
        relays[relay["id"]] = Relay(relay["gpio_on"], relay["gpio_off"])


def on_connect(client, userdata, flags, rc):
    # The callback for when the client receives a CONNACK response from the server.
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("switch/+/set")


def on_message(client, userdata, msg):
    # The callback for when a PUBLISH message is received from the server.
    # Split the topic to determine the correct path
    print(msg.topic+" "+str(msg.payload))

    # command_topic: "switch/1/set"
    try:
        topic_path = msg.topic.split("/")
        if topic_path[0] == "switch":
            switch_number = topic_path[1]
            if topic_path[2] == "set":
                state = msg.payload.decode("UTF-8") == "ON"
                relays[switch_number].set_state(state)

    except IndexError:
        pass


if __name__ == '__main__':
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(BROKER_HOST, 1883, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        print('Interrupted')
        gpio.cleanup()
