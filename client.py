"""TCP client for communicating with RS-WFWATTCH2 devices."""

from __future__ import annotations

import asyncio
import logging
import struct
from dataclasses import dataclass

from .const import (
    CONNECT_TIMEOUT,
    CURRENT_FIXED_POINT_DIVISOR,
    CURRENT_OFFSET,
    DEFAULT_PORT,
    FIXED_POINT_DIVISOR,
    MIN_RESPONSE_LENGTH,
    POWER_OFFSET,
    REQUEST_COMMAND,
    RESPONSE_HEADER,
    VALUE_LENGTH,
    VOLTAGE_OFFSET,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class WattchReading:
    """A single reading from a WFWattch2 device."""

    power: float  # Watts
    voltage: float  # Volts
    current: float  # Amperes


def _parse_value(data: bytes, offset: int, divisor: int) -> float:
    """Parse a 6-byte little-endian fixed-point value at offset."""
    raw = int.from_bytes(data[offset : offset + VALUE_LENGTH], byteorder="little")
    return raw / divisor


class WFWattch2Client:
    """Client for communicating with an RS-WFWATTCH2 device over TCP."""

    def __init__(self, host: str, port: int = DEFAULT_PORT) -> None:
        """Initialise the client."""
        self._host = host
        self._port = port

    @property
    def host(self) -> str:
        """Return the device host."""
        return self._host

    async def async_get_reading(self) -> WattchReading:
        """Connect to the device and fetch a power/voltage reading.

        Raises:
            ConnectionError: If the device is unreachable.
            ValueError: If the response is malformed.
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=CONNECT_TIMEOUT,
            )
        except (OSError, asyncio.TimeoutError) as err:
            raise ConnectionError(
                f"Cannot connect to WFWattch2 at {self._host}:{self._port}"
            ) from err

        try:
            writer.write(REQUEST_COMMAND)
            await writer.drain()

            data = await asyncio.wait_for(
                reader.read(64),
                timeout=CONNECT_TIMEOUT,
            )
        except (OSError, asyncio.TimeoutError) as err:
            raise ConnectionError(
                f"Communication error with WFWattch2 at {self._host}"
            ) from err
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass

        # TODO: check against reported response length?
        # https://qiita.com/yamaokunousausa/items/2faedd6481093e73e2ca#%E3%83%AC%E3%82%B9%E3%83%9D%E3%83%B3%E3%82%B9%E4%BE%8B
        if len(data) < MIN_RESPONSE_LENGTH:
            raise ValueError(
                f"Response too short ({len(data)} bytes, "
                f"expected >= {MIN_RESPONSE_LENGTH})"
            )

        if data[0] != RESPONSE_HEADER:
            raise ValueError(
                f"Unexpected response header: 0x{data[0]:02X} "
                f"(expected 0x{RESPONSE_HEADER:02X})"
            )

        voltage = _parse_value(data, VOLTAGE_OFFSET, FIXED_POINT_DIVISOR)
        current = _parse_value(data, CURRENT_OFFSET, CURRENT_FIXED_POINT_DIVISOR)
        power = _parse_value(data, POWER_OFFSET, FIXED_POINT_DIVISOR)

        _LOGGER.debug(
            "WFWattch2 %s: power=%.2fW, voltage=%.2fV, current=%.3fA",
            self._host,
            power,
            voltage,
            current,
        )

        return WattchReading(power=power, voltage=voltage, current=current)

    async def async_test_connection(self) -> bool:
        """Test whether the device is reachable and responds correctly."""
        try:
            await self.async_get_reading()
        except (ConnectionError, ValueError):
            return False
        return True
