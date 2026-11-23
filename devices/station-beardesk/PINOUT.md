# 🛰️ Station Beardesk: Pinbelegung

Stand: **2026-11-23**, Platine v0.2. Quelle der Wahrheit für die Software ist
`station-beardesk.yaml`. Diese Datei beschreibt die **Verdrahtung**.

> **⚠️ Pins umgezogen (Platine v0.2):** LED Rot/Grün/Blau **D27/D26/D25 → D19/D18/D17**,
> Taster **D33 → D16**. I²C (D21/D22) bleibt. Grund: Auf der Platine steht der ESP32 auf dem
> Kopf (USB-C unten, Kabel hängt nach unten), dann zeigt die 3V3-Reihe zum Display.
> Die Tabellen unten zeigen noch das **Steckbrett vom 2026-11-21** – vor der Bestellung wird
> es auf die neuen Pins umgesteckt und getestet.

## Board

**ESP32-DevKit HW-394** (ESP32-WROOM-32D, USB-C). Steckt auf dem Labor-Steckbrett **über
einer ±-Schiene**: linke Pinreihe in Spalte J des linken Blocks, rechte Pinreihe in Spalte A
des nächsten Blocks. Die Schiene läuft frei unter dem Board durch und dient darunter als
**Stromverteiler** (rot = 3V3, blau = GND).

Pin-Reihenfolge, **USB-Buchse oben**, gezählt von oben:

| # | links | rechts |
|---|---|---|
| 1 | **3V3** 🔴 | VIN |
| 2 | **GND** ⚫ | GND |
| 3 | D15 | D13 |
| 4 | D2 (Board-LED) | D12 |
| 5 | D4 | D14 |
| 6 | D16 | **D27** → LED Rot |
| 7 | D17 | **D26** → LED Grün |
| 8 | D5 | **D25** → LED Blau |
| 9 | D18 | **D33** → Taster |
| 10 | D19 | D32 |
| 11 | **D21** → I²C SDA 🟢 | D35 |
| 12 | RX0 | D34 |
| 13 | TX0 | VN |
| 14 | **D22** → I²C SCL 🟠 | VP |
| 15 | D23 | EN |

## Strom

| Von | Nach | Kabelfarbe |
|---|---|---|
| ESP32 **3V3** | Plus-Schiene (rot) | 🔴 rot |
| ESP32 **GND** | Minus-Schiene (blau) | ⚫ schwarz |

Alle Module holen ihren Strom von der Schiene. **Regel:** Nur Rot in Plus, nur Schwarz in Minus.

## I²C-Bus (400 kHz)

**SDA = GPIO21 (D21)**, **SCL = GPIO22 (D22)**. Alle drei Geräte hängen parallel daran.
Keine Adresskonflikte.

| Gerät | Adresse | VCC | GND | SDA | SCL | Rest |
|---|---|---|---|---|---|---|
| **SCD41** (CO₂/Temp/Feuchte) | 0x62 | + Schiene | − Schiene | D21 | D22 | – |
| **OLED 0,96″** SSD1306 128×64 | 0x3C (Platine: „0x78“) | + Schiene | − Schiene | D21 | D22 | – |
| **TSL2591** (Licht) | 0x29 | **VIN** → + Schiene | − Schiene | D21 | D22 | 3Vo, INT frei |

WHY 400 kHz: Bei 50 kHz blockierte jedes OLED-Update ~220 ms die Hauptschleife.

### Stiftleisten der Module (für die Platine)

Abgelesen vom Aufdruck, Fotos 2026-11-23 (`~/localsend/IMG_20261123_2122*`–`2124*`).
Pin 1 = links, wenn man den Aufdruck lesen kann.

| Modul | Pins | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| **SCD41** (blaue Platine, Leiste „H1“) | 4 | GND | VCC | SCL | SDA | | |
| **OLED 0,96″** | 4 | GND | VCC | SCL | SDA | | |
| **TSL2591** (Adafruit) | 6 | Vin | GND | 3Vo | INT | SDA | SCL |

WHY das wichtig ist: Auf dem Steckbrett geht jedes Kabel einzeln, auf der Platine sitzt
die Buchsenleiste fest. Eine falsche Reihenfolge heißt: Modul verkehrt herum, VCC auf GND.

## RGB-LED (Luft-Ampel)

5 mm, diffus, **gemeinsame Kathode**: **langes Bein → Minus-Schiene**.
Jede Farbe über **220 Ω** (Rot-Rot-Braun) an ihren Pin, PWM über LEDC.

| Farbe | Pin |
|---|---|
| 🔴 Rot | **GPIO27 (D27)** |
| 🟢 Grün | **GPIO26 (D26)** |
| 🔵 Blau | **GPIO25 (D25)** |

Ermittelt per `../rgbtest/` (D25 → D26 → D27 leuchteten Blau → Grün → Rot).

## Taster (Display auf Abruf)

**Gelber Klick-Taster** (Pollin): ein Kontakt → **GPIO33 (D33)**, der andere → **Minus-Schiene**.
Kein externer Widerstand: interner Pull-up (`INPUT_PULLUP`, `inverted: true`).
⚠️ Der Taster hat mehr Beine als Kontakte. Er funktioniert nur an den beiden Beinen, die beim
Drücken verbunden werden (Station 1 lief anfangs nicht, weil die falschen Beine benutzt waren).

## Platine v0.2: ESP32-Pins

| Funktion | Pin | Leiste (USB-C unten) |
|---|---|---|
| 3V3 / GND | 3V3 / GND | J1 Pin 1 / 2 (unten rechts) |
| I²C SDA / SCL | D21 / D22 | J1 Pin 11 / 14 |
| LED Rot / Grün / Blau | **D19 / D18 / D17** | J1 Pin 10 / 9 / 7 |
| Taster | **D16** | J1 Pin 6 |
| GND | GND | J2 Pin 2 |

Nicht benutzt, weil Strapping-Pins (Bootverhalten): D2, D5, D12, D15.

## Freie Pins (Steckbrett, Stand 2026-11-21)

Rechts: D13, D12, D14, D32 (D34/D35/VN/VP sind **nur Eingänge**).
Links: D15, D2 (Board-LED), D4, D16, D17, D5, D18, D19, D23.
Nicht verwenden: RX0/TX0 (USB-Seriell), EN.
