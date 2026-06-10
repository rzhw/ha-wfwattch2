"""DataUpdateCoordinator for the RS-WFWATTCH2 integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import WFWattch2Client, WattchReading
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class WFWattch2Coordinator(DataUpdateCoordinator[WattchReading]):
    """Coordinator that polls a single WFWattch2 device."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: WFWattch2Client,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{client.host}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> WattchReading:
        """Fetch data from the device."""
        try:
            return await self.client.async_get_reading()
        except (ConnectionError, ValueError) as err:
            raise UpdateFailed(
                f"Error communicating with WFWattch2 at {self.client.host}: {err}"
            ) from err
