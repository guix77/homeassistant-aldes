"""Support for the Aldes sensors."""
from __future__ import annotations
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, ALDESMode
from .entity import AldesEntity

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add Aldes sensors from a config_entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[AldesClimateEntity] = []

    for product in coordinator.data:
        for thermostat in product["indicator"]["thermostats"]:
            sensors.append(
                AldesClimateEntity(
                    coordinator,
                    entry,
                    product["serial_number"],
                    product["reference"],
                    product["modem"],
                    thermostat["ThermostatId"],
                )
            )

    async_add_entities(sensors)


class AldesClimateEntity(AldesEntity, ClimateEntity):
    """Define an Aldes sensor."""

    def __init__(
        self,
        coordinator,
        config_entry,
        product_serial_number,
        reference,
        modem,
        thermostat_id,
    ):
        super().__init__(
            coordinator, config_entry, product_serial_number, reference, modem
        )
        self.thermostat_id = thermostat_id
        self._attr_device_class = "temperature"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL]
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )
        self._enable_turn_on_off_backwards_compatibility = False
        self._attr_target_temperature_step = 1
        self._attr_hvac_action = HVACAction.OFF

    @property
    def device_info(self):
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.thermostat_id)},
        )

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{DOMAIN}_{self.thermostat_id}_climate"

    @property
    def name(self):
        """Return a name to use for this entity."""
        for product in self.coordinator.data:
            if product["serial_number"] == self.product_serial_number:
                for thermostat in product["indicator"]["thermostats"]:
                    if thermostat["ThermostatId"] == self.thermostat_id:
                        return f"{thermostat['Name']} climate"
            return None

    @property
    def min_temp(self):
        """Get the minimum temperature"""
        for product in self.coordinator.data:
            if product["serial_number"] == self.product_serial_number:
                if product["indicator"]["current_air_mode"] in [ALDESMode.HEAT_COMFORT, ALDESMode.HEAT_ECO]:
                    return product["indicator"]["cmist"]
                elif product["indicator"]["current_air_mode"] in [ALDESMode.COOL_COMFORT, ALDESMode.COOL_BOOST]:
                    return product["indicator"]["fmist"]
            return None

    @property
    def max_temp(self):
        """Get the maximum temperature"""
        for product in self.coordinator.data:
            if product["serial_number"] == self.product_serial_number:
                if product["indicator"]["current_air_mode"] in [ALDESMode.HEAT_COMFORT, ALDESMode.HEAT_ECO]:
                    return product["indicator"]["cmast"]
                elif product["indicator"]["current_air_mode"] in [ALDESMode.COOL_COMFORT, ALDESMode.COOL_BOOST]:
                    return product["indicator"]["fmast"]
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
            if product["isConnected"]:
                if product["serial_number"] == self.product_serial_number:

                    for thermostat in product["indicator"]["thermostats"]:
                        if thermostat["ThermostatId"] == self.thermostat_id:
                            self._attr_target_temperature = thermostat["TemperatureSet"]
                            self._attr_current_temperature = thermostat["CurrentTemperature"]

                            currentAirMode = product["indicator"]["current_air_mode"]
                            # Default OFF
                            hvacMode = HVACMode.OFF
                            # Default IDLE
                            hvacAction = HVACAction.IDLE

                            if currentAirMode == ALDESMode.OFF:
                                hvacAction = HVACAction.OFF
                            # HEATING
                            elif currentAirMode in [ALDESMode.HEAT_COMFORT, ALDESMode.HEAT_ECO]:
                                hvacMode = HVACMode.HEAT
                                # If the temperature is below, it is HEATING, otherwise by default IDLE
                                if  thermostat["CurrentTemperature"] < thermostat["TemperatureSet"] :
                                    hvacAction = HVACAction.HEATING

                            # COOLING
                            elif currentAirMode in [ALDESMode.COOL_COMFORT, ALDESMode.COOL_BOOST]:
                                hvacMode = HVACMode.COOL
                                # If the temperature is above, it is COOLING, otherwise by default IDLE
                                if  thermostat["CurrentTemperature"] > thermostat["TemperatureSet"] :
                                    hvacAction = HVACAction.COOLING

                            # PROG
                            elif currentAirMode in [ALDESMode.HEAT_PROG_A, ALDESMode.HEAT_PROG_B, ALDESMode.COOL_PROG_A, ALDESMode.COOL_PROG_B]:
                                hvacMode = HVACMode.AUTO

                            self._attr_hvac_mode = hvacMode
                            self._attr_hvac_action = hvacAction
            else:
                self._attr_current_temperature = None

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        await self.coordinator.api.set_target_temperature(
            self.modem,
            self.thermostat_id,
            self._thermostat_name,
            kwargs.get(ATTR_TEMPERATURE),
        )
        self._attr_target_temperature = kwargs.get(ATTR_TEMPERATURE)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode in [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL]:
            if hvac_mode == HVACMode.OFF:
                mode = ALDESMode.OFF
            elif hvac_mode == HVACMode.HEAT:
                mode = ALDESMode.HEAT_COMFORT
            elif hvac_mode == HVACMode.COOL:
                mode = ALDESMode.COOL_COMFORT

            await self.coordinator.api.change_mode(
                self.modem,
                mode
        )

    @property
    def _thermostat_name(self):
        """Get the thermostat name as defined in the API"""
        for product in self.coordinator.data:
            if product["serial_number"] == self.product_serial_number:
                for thermostat in product["indicator"]["thermostats"]:
                    if thermostat["ThermostatId"] == self.thermostat_id:
                        return thermostat["Name"]
            return None
