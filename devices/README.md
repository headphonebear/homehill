# 🛰️ Devices — Station to Station

Small self-built hardware that lives in the house: ESP32 boards with sensors,
an LED, maybe a display. No cloud, no vendor app, no hub. Each device measures
something locally and (soon) reports it to Orchard.

The project is called **Station to Station** (after the Bowie record): a
growing network of small stations, one per place, that all feed **one**
database. Where a value comes from doesn't matter to the database — a
self-built station, a reused Bluetooth sensor, later maybe a Pi with a camera.

Same idea as [`servers/`](../servers/): declarative config, flashed by hand.
The difference is that here the **hardware is ours too** — so the board
layout and the printed enclosure live next to the firmware.

## Layout

One folder per device, named after **where it lives**:

```
devices/
└── station-beardesk/          # 🐻 Stefan's desk, Honeycomb Storage Wall
    ├── README.md              #    what it is, what it measures, status
    ├── station-beardesk.yaml  #    ESPHome config — the firmware
    ├── PINOUT.md              #    the wiring, pin by pin
    ├── pcb/                   #    KiCad project (carrier board)      — coming
    └── enclosure/             #    printable case (STL/3MF + source)  — coming
```

## Conventions

- **Name = place**, not a number: `station-<place>`. The ESPHome `name:` and
  the file name are the same, so the device shows up on the network under it.
- **Firmware: ESPHome**, run from the official Docker image on barn:
  ```bash
  cd devices/<device>
  docker run --rm -v "$PWD":/config --device /dev/ttyUSB0 \
    ghcr.io/esphome/esphome:2026.11.0 run --no-logs --device /dev/ttyUSB0 <device>.yaml
  ```
  `esphome upload` does **not** recompile — always use `run`.
- **Secrets never land here.** This repo is public. WiFi passwords and API keys
  go into a `secrets.yaml` next to the config (gitignored, see `.gitignore`);
  the source of truth is Vaultwarden. The config only says `!secret wifi_ssid`.
- **Hardware is shared on purpose.** The PCB is a *carrier board*: the ESP32
  dev kit and sensor breakouts plug into female headers, nothing is soldered
  to them. A dead module gets swapped, not desoldered. Enclosures get published
  (MakerWorld/Printables) with a link back here.
