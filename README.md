# Home Assistant integration for RS-WFWATTCH2

Custom Home Assistant integration for Ratoc RS-WFWATTCH2.

## Features

- Creates **Current (A)**, **Power (W)** and **Voltage (V)** sensor entities
- Configurable via the HA UI (Settings → Devices & Services → Add Integration)
- Polls via local network, configurable interval (default 10 seconds)
- **Untested:** Multiple device support
- Japanese translations included

## Requirements

- The RS-WFWATTCH2 must be set up on your Wi-Fi network (via the Ratoc app)
- Home Assistant must be on the same LAN (or have L3 reachability to the device)

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rzhw&repository=ha-wfwattch2&category=integration)

1. Use the HACS link above, or copy the `custom_components/wfwattch2` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration**
4. Search for "Ratoc RS-WFWATTCH2 Watt Checker"
5. Enter a name and the device's IP address
6. The integration will test the connection, then create power and voltage sensors

## Acknowledgements

Protocol details were derived from [RS-WFWATTCH2を使ってPCの消費電力(実測値)をモニタリングしてみよう - @yamaokunousausa(うさうさ)](https://qiita.com/yamaokunousausa/items/2faedd6481093e73e2ca).

## Future ideas

- Add energy tracking via HA's `integration` helper (Riemann sum of power → kWh)
- ON/OFF switch entity (the device supports remote power control)
