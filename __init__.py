"""The Ratoc RS-WFWATTCH2 integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant

from .client import WFWattch2Client
from .const import DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import WFWattch2Coordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RS-WFWATTCH2 from a config entry."""
    client = WFWattch2Client(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = WFWattch2Coordinator(hass, client, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
