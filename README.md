## Goal

The goal of this project is to be able to control old GE low voltage relays from Home Assistant while leaving the old relays and switch controls intact.

## Hardware Setup

In order to accomplish the goal, a Raspberry Pi, Arduino Mega, and a number of [SainSmart 8-Channel Solid State Relay](https://www.amazon.com/gp/product/B006J4G45G) modules were used.

Starting from the outside and working down to the GE relay control...

The Raspberry Pi is used to create [MQTT Light](https://www.home-assistant.io/integrations/light.mqtt/) entities in Home Assistant to represent each GE relay in my home control panel. The entities are implemented in the Python service. With this interface, each light can be toggled on or off. The Raspberry Pi doesn't directly control the relays, but instead has a USB serial connection to an Arduino. The Pi can give simple requests to the Arduino to pulse a given GPIO for a hard-coded amount of time.

Since these GE relays require some specific voltage characteristics on the coils, each Arduino GPIO is wired to the input control signal of a solid state relay where the input of the relay is connected to the same transformer that goes out to the normal momentary switches throughout the house and the output goes to either the on or off side of the coil. By pulsing the GPIO on the Arduino we can simulate the same operation of an individual pushing a momentary switch for a short amount of time. Note that having more precise control over the timing is also beneficial for relability of the relays.

Because one GPIO is used for on and one is for off, we require a pair of GPIO to control each GE relay. This results in a lot of outputs being required for this approach which is why an Arduino Mega was used instead of directly controlling the SSRs from the Pi.

## Configuration

The `config.json` file can be used to configure some of the operation of the service.

| Key             | Meaning                                               |
| --------------- | ----------------------------------------------------- |
| `broker`        | The IP address or hostname of the MQTT broker         |
| `username`      | The username to be used to connec to the MQTT broker  |
| `password`      | The password to be used to connect to the MQTT broker |
| `delay_time_ms` | The width of the pulse used to toggle the GE relays   |

Relays are defined in an array called `"relays"`. Each object in the array represents a relay in the control panel. The `"id"` of the relay is used for the MQTT topic path as well as the entity id in Home Assistant. For example, controlling the state of a relay with `"id"` of 1 would be done by publishing to `homeassistnat/light/relay_1/set`. The `"gpio_on"` and `"gpio_off"` keys represent the Arudino Megapin numbers to pulse the on and off sides of the GE relay. Finally, the `description` will be used to set the name of the light in Home Assistant.

```json
{
{
  "broker": "192.168.1.3",
  "username": "lights",
  "password": "lights",
  "delay_time_ms": 100,
  "relays": [
    {
      "id": "1",
      "gpio_on": 8,
      "gpio_off": 9,
      "description": "outside",
      "area": "Outside"
    },
    {
      "id": "2",
      "gpio_on": 10,
      "gpio_off": 11,
      "description": "outside",
      "area": "Outside"
    }
  ]
}
```

No confiuration of Home Assistant is required other than the MQTT integration. The Python service uses the [MQTT Discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery) feature of Home Assistant to automatically make Home Assistant aware of the entities.

## Installation

To install as a service on the Pi

```bash
sudo cp light-control.service /etc/systemd/system/
sudo systemctl enable light-control
sudo systemctl start light-control
```

To check the status:

```bash
sudo systemctl status light-control
```

This should return something like

```
● light-control.service - Systemd service to my custom relay or light control software
     Loaded: loaded (/etc/systemd/system/light-control.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2022-07-17 12:30:21 EDT; 1s ago
   Main PID: 4322 (sh)
      Tasks: 2 (limit: 780)
        CPU: 763ms
     CGroup: /system.slice/light-control.service
             ├─4322 /bin/sh /home/pi/Development/light-control/start.sh
             └─4323 python main.py

Jul 17 12:30:21 raspberrypi systemd[1]: Started Systemd service to my custom relay or light control software.
```

## Arduino PINs

| PIN Number | Working?                      |
| ---------- | ----------------------------- |
| 0          | no - tied to serial?          |
| 1          | no - tied to serial?          |
| 2          | yes                           |
| 3          | yes                           |
| 4          | yes                           |
| 5          | yes                           |
| 6          | yes                           |
| 7          | yes                           |
| 8          | yes                           |
| 9          | yes                           |
| 10         | yes                           |
| 11         | yes                           |
| 12         | yes                           |
| 13         | no - seems to be tied to LED? |
| 14         | yes                           |
| 15         | yes                           |
| 16         | yes                           |
| 17         | yes                           |
| 18         | yes                           |
| 19         | yes                           |
| 20         | no - pulled high on startup?  |
| 21         | no - pulled high on startup?  |
| 22         | yes                           |
| 23         | yes                           |
| 24         | yes                           |
| 25         | yes                           |
| 26         | yes                           |
| 27         | yes                           |
| 28         | yes                           |
| 29         | yes                           |
| 30         | yes                           |
| 31         | yes                           |
| 32         | yes                           |
| 33         | yes                           |
| 34         | yes                           |
| 35         | yes                           |
| 36         | yes                           |
| 37         | yes                           |
| 38         | yes                           |
| 39         | yes                           |
| 40         | yes                           |
| 41         | yes                           |
| 42         | yes                           |
| 43         | yes                           |
| 44         | yes                           |
| 45         | yes                           |
| 46         | yes                           |
| 47         | yes                           |
| 48         | yes                           |
| 49         | yes                           |
| 50         | yes                           |
| 51         | yes                           |
| 52         | yes                           |
| 53         | yes                           |

