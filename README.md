# 🍺 KegScale

KegScale är en Raspberry Pi-baserad våg för att mäta hur mycket öl som finns kvar i ett Corneliusfat.

Systemet använder fyra lastceller tillsammans med en HX711 och en Raspberry Pi. Vikten läses av i Python och presenteras i ett webbaserat gränssnitt med Flask.

Webbsidan visar:

- Total vikt
- Beräknad mängd öl i liter
- Fyllnadsgrad i procent
- Grafisk nivåindikator
- Online/offline-status
- Senaste mättid
- Webbaserad nollställning av vågen


## Hardware

Projektet använder:

- Raspberry Pi 5
- HX711 load cell amplifier
- 4 × 50 kg load cells
- Lastcellerna kopplade som en Wheatstone-brygga
- Nätverksanslutning för webbgränssnittet

HX711 är ansluten till Raspberry Pi med:

| HX711 | Raspberry Pi |
|------|---------------|
| DT / DATA | GPIO 6 |
| SCK / CLOCK | GPIO 5 |
| GND | GND |
| VCC | Matning |

Kopplingsschema och Fritzing-filer finns i katalogen:

```text
hardware/
```


## Project structure

```text
KegScale/
├── kegscale.py
├── kegscale.json
├── config.json
├── control.json
├── debug_vikt.py
├── requirements.txt
│
├── hardware/
│   ├── ...
│
└── web/
    ├── app.py
    │
    ├── templates/
    │   └── index.html
    │
    └── static/
        ├── script.js
        └── style.css
```


## How it works

Systemet är uppdelat i två delar.

### KegScale

`kegscale.py` kommunicerar direkt med HX711 och lastcellerna.

Programmet:

1. Återställer HX711
2. Nollställer vågen vid start
3. Läser 30 mätvärden
4. Sorterar mätvärdena
5. Tar bort de 5 högsta och 5 lägsta
6. Beräknar medelvärdet av resterande 20 mätningar
7. Omvandlar råvärdet till gram
8. Beräknar mängden öl
9. Skriver resultatet till `kegscale.json`


### Web interface

Flask-servern finns i:

```text
web/app.py
```

Flask läser `kegscale.json` och skickar informationen till webbläsaren.

JavaScript uppdaterar sidan automatiskt varje sekund.

Kommunikationen ser ut så här:

```text
Load cells
    ↓
HX711
    ↓
Raspberry Pi GPIO
    ↓
kegscale.py
    ↓
kegscale.json
    ↓
Flask
    ↓
JavaScript
    ↓
Web browser
```


## Calibration

Nuvarande kalibreringsfaktor:

```python
KALIBRERINGS_FAKTOR = 21.04
```

Vågen har kalibrerats med en känd vikt på cirka 3910 gram.

Last på vågen gör HX711-råvärdet mer negativt, därför används:

```python
vikt_gram = -differens / KALIBRERINGS_FAKTOR
```

Mätningen filtreras genom att läsa 30 värden och ta bort de 5 högsta och 5 lägsta innan medelvärdet beräknas.


## Keg configuration

Fatets egenskaper lagras i:

```text
config.json
```

Exempel för ett 19-liters Corneliusfat:

```json
{
    "keg_tare_kg": 4.5,
    "keg_capacity_l": 19.0,
    "beer_density_kg_per_l": 1.01
}
```

### keg_tare_kg

Vikten på det tomma fatet.

### keg_capacity_l

Fatets kapacitet i liter.

### beer_density_kg_per_l

Ungefärlig densitet för ölet i kg/liter.


## Calculating beer volume

Ölets vikt beräknas från:

```text
Ölvikt = Total vikt - Fatets tomvikt
```

Volymen beräknas sedan från:

```text
Liter öl = Ölvikt / Ölets densitet
```

Fyllnadsgraden beräknas från:

```text
Fyllnadsgrad = Liter öl / Fatets kapacitet × 100
```


## JSON data

`kegscale.py` skriver aktuell information till:

```text
kegscale.json
```

Exempel:

```json
{
    "weight_g": 13945.1,
    "weight_kg": 13.945,
    "beer_weight_kg": 9.445,
    "beer_liters": 9.35,
    "fill_percent": 49.2,
    "keg_tare_kg": 4.5,
    "keg_capacity_l": 19.0,
    "beer_density_kg_per_l": 1.01,
    "timestamp": "2026-08-30 13:20:00"
}
```


## Web tare

Vågen kan nollställas direkt från webbgränssnittet.

När användaren klickar på:

```text
Nollställ våg
```

skickar Flask ett kommando genom:

```text
control.json
```

Exempel:

```json
{
    "tare": true
}
```

`kegscale.py` upptäcker kommandot, gör en ny tarering och återställer sedan kommandot.

Det innebär att Flask aldrig behöver kommunicera direkt med GPIO eller HX711.

Kommunikationen är:

```text
Web browser
    ↓
POST /api/tare
    ↓
Flask
    ↓
control.json
    ↓
kegscale.py
    ↓
HX711 tare
```


## Python environment

Skapa en virtuell Python-miljö:

```bash
python3 -m venv myenv
```

Aktivera den:

```bash
source myenv/bin/activate
```

Installera beroenden:

```bash
pip install -r requirements.txt
```


## Running KegScale

KegScale och webbservern körs som två separata processer.

### Terminal 1 – Scale

```bash
cd ~/Projects/KegScale

source myenv/bin/activate

python kegscale.py
```


### Terminal 2 – Web server

```bash
cd ~/Projects/KegScale

source myenv/bin/activate

cd web

python app.py
```

Flask-servern körs på port:

```text
5000
```

Webbgränssnittet kan sedan öppnas från en dator eller mobil på samma nätverk:

```text
http://<raspberry-pi-ip>:5000
```


## Web API

### Read scale

```text
GET /api/weight
```

Returnerar aktuell vikt, ölvolym, fyllnadsgrad och status.


### Tare scale

```text
POST /api/tare
```

Begär att `kegscale.py` nollställer vågen.


## Current features

- [x] HX711 communication
- [x] Four load cells
- [x] Digital filtering
- [x] Scale calibration
- [x] Automatic tare at startup
- [x] Weight in grams and kilograms
- [x] Beer volume calculation
- [x] Keg fill percentage
- [x] JSON status
- [x] Flask web interface
- [x] Automatic web updates
- [x] Online/offline detection
- [x] Graphical keg level
- [x] Web-based scale tare


## Planned features

Possible future improvements:

- [ ] Set empty keg weight from the web interface
- [ ] Change keg capacity from the web interface
- [ ] Configuration page
- [ ] Support for different keg sizes
- [ ] Save tare/offset between restarts
- [ ] Start KegScale automatically at Raspberry Pi boot
- [ ] Start Flask automatically at Raspberry Pi boot
- [ ] Improved web interface
- [ ] Historical consumption data
- [ ] Multiple keg support


## Status

The basic KegScale system is working.

The scale has been calibrated and tested, JSON communication is working, and the Flask web interface displays live weight, calculated beer volume and keg fill percentage.

Web-based tare is also implemented.
