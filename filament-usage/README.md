# Filament usage

# About

![grafana preview](./grafana.png)

This repo is about generic filament usage by the 3D printer:

- read current filament weight via tensor beam attached to esp32
- register esp32 in Home Assistant
- Home Assistant exposes metrics in Prometheus format
- metrics are scraped (fetched) by Prometheus instance
- Grafana uses Prometheus as data source
- Grafana dashboard uses some basic formulas to convert weight to meters
  of filament to be used

This allows to estimate how much filament is left and thus what to print
without need for a filament change.

# Known limitations

- This can be done without Home Assistant - in that case you would just need to
  configure esp32 to expose prometheus metrics and then configure prometheus to
  scrape the device directly - do whatever you like.
- I was not doing load cell calibration in esphome, I will do it in grafana dashboard

# Hardware Bill of Materials

- esp32 device such as [nodemcu dev kit](https://www.espressif.com/en/products/devkits/esp32-devkitc/overview)
  which as usb converter so you can attach it to the computer over USB
- usb cable - depends on your hardware - so it may be USB-A to Micro-USB or USB-C to USB-C and so on...
- power supply for esp32 - older phone charger over micro-usb or usb-c should be enough
- [load cell 5kg](https://www.sparkfun.com/products/14729) - notice that max weight is important
  and choose such load cell that it can sustain expected weight range, I suggest 5kg, otherwise anything
  more can be less precise or reaching lower read limit, and and anything less will reach the upper reading limits
- [load cell amplifier](https://www.sparkfun.com/products/13879) - with hx711 sensor
- some metal/plastic/wooden planks + screws + washers
- at least 4 dupont cables - between load cell amplifier and esp32
- at least 2 example weights with precise values to calibrate the load cell,
  such as 0.5kg and 1kg - or a measuring cup from the kitchen that you can fill in with the water
  to reach given weight

- soldering iron to connect load cell and gold pins to load cell amplifier
- some device to run esphome dashboard / HomeAssistant / Prometheus / Grafana
  Raspberry Pi with at least 2GB of ram should be sufficient

# Software Bill of Materials

- WiFi network to attach esp32 device to it
- existing HomeAssistant installation accessible over WiFi, I assume it already works

# Hardware assembly

First I suggest to read [here](https://randomnerdtutorials.com/esp32-load-cell-hx711/)

- create a 'weight setup', which means one plank attached to the bottom of the
  load cell, and the other plank is attached to the top of the load cell, all
  using generic nuts/bolts/washers

- solder cables from load cell to load cell amplifier
- solder gold pins to the  load cell amplifier
- attach dupont cables between load cell amplifier and esp32

# Software

## Esp32 device

- install esphome on the device - I suggest via [web-browser](https://web.esphome.io/)
  via USB cable
- extend device config with [hx711 params](https://esphome.io/components/sensor/hx711.html),
  below code fragment assumes that `GPIO18` and `GPIO19` are used to connect the device to esp32:

  ```yaml
  sensor:
    - platform: hx711
      name: "HX711 Value"
      dout_pin: GPIO19
      clk_pin: GPIO18
      gain: 128
      update_interval: 10s
  ```

  You can see example config for the device [here](./esp-device.yaml)

- in esphome dashboard find your device configuration and add the code above to the device,
  then flash esphome firmware, after a moment device should be back online
- see if the tensor beam reacts to the changes - you just should be able to see raw values
  in esphome dashboard logs or in Home Assistant
- ensure tensor beam is not under load - write down the current raw value as `LOAD_ZERO`
- place example known weight on the tensor beam, write down the raw value as `LOAD_KNOWN`, remove the weight,
  this will come in handy later on

## HomeAssistant + Prometheus

- prepare HomeAssistant to expose metrics - see [here](https://www.home-assistant.io/integrations/prometheus/),
  in HomeAssistant you need just `prometheus:` line section in the config and restart HomeAssistant

- configure Prometheus to scrape the metrics - in case of Home Assistant you may need to add basic auth via API key,
  below is example config fragment to use to copy/paste to Prometheus config:

  ```yaml
    - authorization:
        credentials: redacted....put.your.own.credentials.here
      job_name: home-assistant
      metrics_path: /api/prometheus
      scrape_interval: 15s
      scrape_timeout: 10s
      static_configs:
      - targets:
        - home-assistant-host--or-ip-address:8123
  ```

  [full details here](https://www.home-assistant.io/integrations/prometheus/#full-example),

## Grafana

### Install dashboard

- use Grafana and connect it to Prometheus as data source,
  ensure you can find hx711 metrics in the grafana - they should be under something like
  `homeassistant_sensor_state{entity="sensor.esp32_devkit_v4_9e8360_hx711_value"}`
- add [dashboard](./grafana-dashboard.json) to the Grafana, it will be named `Tensor Beam`

### Calculate load cell parameters

We can use `y=ax+b` equation to get the given weight from a load cell.

The `y` is the raw value which is reported by load cell.
The `x` is the weight we place on the load cell.

We measured two weights before, and we know their values:

- `LOAD_ZERO` when nothing was placed `(x=0)`
- `LOAD_KNOWN` when we placed given known weight (for example 1kg)

we can calculate `a` and `b` - those will be needed below.

- `LOAD_ZERO = ax+b` , but we assume `x=0`, thus `b = LOAD_ZERO`
- `LOAD_KNOWN = ax+b`, and because we know `b`, we can write
  `LOAD_KNOWN = ax + LOAD_ZERO`, so, `a = (LOAD_KNOWN - LOAD_ZERO)/x`
  and because we know what weight we placed on the load cell we can replace it as x and will get the value of `a`

Now we have `a` and `b` values.

### Configure dashboard values

- go to the dashboard
- click cog icon in top right fragment of the dashboard
- on the left menu select `Variables`
- edit Variable `a` and set it's `Value` to the `a` we calculated above, click `Update`
- edit Variable `b` and set it's `Value` to the `b` we calculated above, click `Update`
- do back and save the dashboard

### Using dashboard on daily basis

- Now when you are on the dashboard you can adjust parameters in the input
  fields on the top of the dashboard,
- Adjust those to meet your needs such as spool size, filament diameter and density,
  on the right I've added some known example values for given spools.
- Remember to change those values when you place a new spool.
