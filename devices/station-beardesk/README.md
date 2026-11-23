# 🛰️ Station Beardesk

The first station of **Station to Station** (built as "Station 1" on
2026-11-21). Lives on the Honeycomb Storage Wall behind Stefan's monitor —
the home office.

## What it does

- **Measures** CO₂, temperature and humidity (Sensirion SCD41) and ambient
  light (TSL2591)
- **Air traffic light** on an RGB LED: green ≤ 800 ppm → red ≥ 1400 ppm,
  pulses from 1600 ppm, blinks blue when humidity is above 65 %
- **Dims itself** to the room light — bright in daylight, a faint glow at night
- **OLED only on demand**: press the button, the values show for 30 s.
  Nobody (no bear) stares at a display all day

## Hardware

ESP32-DevKit HW-394 (WROOM-32D, USB-C) · SCD41 · TSL2591 · SSD1306 OLED
0.96″ 128×64 · RGB LED (common cathode, 3 × 220 Ω) · push button.
All sensors on one I²C bus at 400 kHz. Wiring pin by pin: [`PINOUT.md`](PINOUT.md).

## Status

| Step | State |
|---|---|
| Breadboard build, ESPHome config | ✅ 2026-11-21, running daily since |
| Carrier PCB (KiCad, `pcb/`) | 🛠️ in design |
| Enclosure (`enclosure/`, by tinkerbear) | 🛠️ waits for PCB dimensions |
| WiFi + values to Orchard (VictoriaMetrics) | ⏳ |

⚠️ The board on the wall still runs the old firmware named `station1`.
It only becomes `station-beardesk` on the next flash.
