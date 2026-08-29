# KegScale 🍺

Ett Python-baserat projekt för att väga ölfat i realtid med en Raspberry Pi 5 och en HX711-vågsensor.

## Struktur
* `debug_vikt.py` - Realtids-debug för att läsa av sensorvärden.
* `requirements.txt` - Minimalistiska beroenden för Raspberry Pi 5 (`lgpio`).
* `web/` - Webbgränssnitt (under utveckling).

## Installation & Användning

1. Skapa och aktivera den virtuella miljön:
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```

2. Installera beroenden:
   ```bash
   pip install -r requirements.txt
   ```

3. Kör debug-skriptet:
   ```bash
   python3 debug_vikt.py
   ```
