[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

- April 2026: those looking for a maintained AldesConnect integration can go there: https://github.com/saniho/homeassistant-aldes
- October 2024: archived in favor of a local DIY solution: https://github.com/guix77/esphome-aldes-tone

# Aldes integration for Home Assistant

This integration allows Home Assistant to interact with an Aldes product through the cloud. You must have an AldesConnect box connected to the device, set up and working in the mobile app.

## Supported products

### T.One® AIR

+ Binary sensor entity to check if the product is connected to Aldes cloud
+ Temperature sensor entity for each room
+ Climate entity for each room with a thermostat to set the target temperature, and a global mode switch between OFF, HEAT and COOL.

### Other products

+ T.One® AquaAIR: the air part could work (to be confirmed) but there's no water implementation.

## Installation

In HACS, add the custom repository https://github.com/guix77/homeassistant-aldes and select the Integration category.

## Configuration

The username and password asked during the configuration are the same that you use for the Aldes mobile app.

## Credits

- [API doc](https://community.jeedom.com/t/aldes-connect-api/57068)
- [API auth & call examples](https://github.com/aalmazanarbs/hassio_aldes)
- [More API doc](https://community.jeedom.com/t/aldes-t-one-api-php/94269)
- [Integration blueprint](https://github.com/custom-components/integration_blueprint)

## See also

- https://github.com/Fredzxda/homeassistant-aldes for EASYHOME PureAir Compact CONNECT
