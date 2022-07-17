## Configuration

The `config.json` file can be used to configure some of the operation of the service.

The `"broker"` is to set the MQTT broker hostname or IP address.

The `"delay_time_ms"` is length of the pulse used to pulse the GE relays.

Relays are defined in an array called `"relays"`. Each object in the array represents a relay in the control panel. The `"id"` of the relay is used for the MQTT topic path. For example, controlling the state of a relay with `"id"` of 1 would be done by publishing to `switch/1/set`. The `"gpio_on"` and `"gpio_off"` keys represent the [Raspberry Pi pin numbers](https://community-storage.element14.com/communityserver-components-secureimagefileviewer/telligent/evolution/components/attachments/13/153/00/00/00/01/74/28/pi3_gpio.png-861x1023.png?sv=2016-05-31&sr=b&sig=bshad40PBcirvkDKAuF3ALzq0keleuBvcCbkjJbI63Y%3D&se=2022-07-23T23%3A59%3A59Z&sp=r&_=khnm8BEyu11eFApR1Ychhg==) to pulse the on and off sides of the GE relay.

```json
{
  "broker": "192.168.1.75",
  "delay_time_ms": 100,
  "relays": [
    {
      "id": "1",
      "gpio_on": 7,
      "gpio_off": 11,
      "relay_number": 13,
      "description": ""
    },
    {
      "id": "2",
      "gpio_on": 12,
      "gpio_off": 13,
      "relay_number": 14,
      "description": ""
    },
    {
      "id": "3",
      "gpio_on": 15,
      "gpio_off": 16,
      "relay_number": 15,
      "description": ""
    },
    {
      "id": "4",
      "gpio_on": 18,
      "gpio_off": 22,
      "relay_number": 16,
      "description": ""
    }
  ]
}
```


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