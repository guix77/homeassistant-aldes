"""Support for the AldesConnect sensors."""
from __future__ import annotations
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, MANUFACTURER
from .entity import AldesConnectEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add AldesConnect sensors from a config_entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[AldesConnectSensor] = []

    for product in coordinator.data:
        for thermostat in product["indicator"]["thermostats"]:
            sensors.append(
                AldesConnectSensor(
                    coordinator,
                    entry,
                    product["serial_number"],
                    product["reference"],
                    thermostat["ThermostatId"],
                )
            )

    async_add_entities(sensors)


class AldesConnectSensor(AldesConnectEntity, SensorEntity):
    """Define an AldesConnect sensor."""

    def __init__(
        self, coordinator, config_entry, product_serial_number, reference, thermostat_id
    ):
        super().__init__(coordinator, config_entry, product_serial_number, reference)
        self._attr_device_class = "temperature"
        self._attr_native_unit_of_measurement = TEMP_CELSIUS
        self.thermostat_id = thermostat_id

    @property
    def device_info(self):
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.thermostat_id)},
            manufacturer=MANUFACTURER,
            name=f"Thermostat {self.thermostat_id}",
        )

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{DOMAIN}_{self.product_serial_number}_{self.thermostat_id}_temperature"

    @property
    def name(self):
        """Return a name to use for this entity."""
        for product in self.coordinator.data:
            if product["serial_number"] == self.product_serial_number:
                for thermostat in product["indicator"]["thermostats"]:
                    if thermostat["ThermostatId"] == self.thermostat_id:
                        return f"{thermostat['Name']} temperature"
            return None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update attributes when the coordinator updates."""
        self._async_update_attrs()
        super()._handle_coordinator_update()

    @callback
    def _async_update_attrs(self) -> None:
        """Update binary sensor attributes."""
        for product in self.coordinator.data:
            if product["serial_number"] == self.product_serial_number:
                for thermostat in product["indicator"]["thermostats"]:
                    if thermostat["ThermostatId"] == self.thermostat_id:
                        self._attr_native_value = thermostat["CurrentTemperature"]
