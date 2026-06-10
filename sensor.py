"""Sensor platform for the RS-WFWATTCH2 integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import WattchReading
from .const import DOMAIN
from .coordinator import WFWattch2Coordinator


@dataclass(frozen=True, kw_only=True)
class WFWattch2SensorEntityDescription(SensorEntityDescription):
    """Describes a WFWattch2 sensor entity."""

    value_fn: Callable[[WattchReading], float]


SENSOR_DESCRIPTIONS: tuple[WFWattch2SensorEntityDescription, ...] = (
    WFWattch2SensorEntityDescription(
        key="power",
        translation_key="power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda reading: reading.power,
    ),
    WFWattch2SensorEntityDescription(
        key="current",
        translation_key="current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        value_fn=lambda reading: reading.current,
    ),
    WFWattch2SensorEntityDescription(
        key="voltage",
        translation_key="voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda reading: reading.voltage,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WFWattch2 sensor entities."""
    coordinator: WFWattch2Coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        WFWattch2Sensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class WFWattch2Sensor(CoordinatorEntity[WFWattch2Coordinator], SensorEntity):
    """Representation of a WFWattch2 sensor."""

    entity_description: WFWattch2SensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WFWattch2Coordinator,
        entry: ConfigEntry,
        description: WFWattch2SensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, "WFWattch2"),
            manufacturer="Ratoc Systems",
            model="RS-WFWATTCH2",
            configuration_url=f"http://{entry.data[CONF_HOST]}",
        )

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
