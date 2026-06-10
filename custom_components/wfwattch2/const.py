"""Constants for the Ratoc RS-WFWATTCH2 integration."""

DOMAIN = "wfwattch2"

DEFAULT_PORT = 60121
DEFAULT_SCAN_INTERVAL = 10  # seconds
MIN_SCAN_INTERVAL = 1  # seconds
CONNECT_TIMEOUT = 2  # seconds

# Binary protocol: send this command to request a reading
REQUEST_COMMAND = bytes([0xAA, 0x00, 0x02, 0x18, 0x00, 0x65])
RESPONSE_HEADER = 0xAA

# Byte offsets for parsing the response. Each value is 6 little-endian bytes.
VALUE_LENGTH = 6
VOLTAGE_OFFSET = 5
CURRENT_OFFSET = 11
POWER_OFFSET = 17
MIN_RESPONSE_LENGTH = POWER_OFFSET + VALUE_LENGTH

# Values are fixed-point. Power and voltage use 24 fractional bits;
# current uses 30 fractional bits.
FIXED_POINT_DIVISOR = 1 << 24
CURRENT_FIXED_POINT_DIVISOR = 1 << 30
