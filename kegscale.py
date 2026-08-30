import time
import json
from datetime import datetime
import RPi.GPIO as GPIO


# -------------------------------------------------
# KONFIGURATION
# -------------------------------------------------

DATA_PIN = 6
CLOCK_PIN = 5

KALIBRERINGS_FAKTOR = 21.04

ANTAL_MATNINGAR = 30
ANTAL_BORTTAGNA = 5

JSON_FIL = "kegscale.json"
CONFIG_FIL = "config.json"
CONTROL_FIL = "control.json"


# -------------------------------------------------
# GPIO
# -------------------------------------------------

GPIO.setmode(GPIO.BCM)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(DATA_PIN, GPIO.IN)


# -------------------------------------------------
# HX711 RESET
# -------------------------------------------------

def reset_hx711():
    print("Återställer HX711...")

    GPIO.output(CLOCK_PIN, GPIO.HIGH)
    time.sleep(0.005)

    GPIO.output(CLOCK_PIN, GPIO.LOW)
    time.sleep(0.2)


# -------------------------------------------------
# LÄS ETT RÅVÄRDE
# -------------------------------------------------

def las_hx711():

    for _ in range(1000):

        if GPIO.input(DATA_PIN) == 0:
            break

        time.sleep(0.001)

    else:
        return None

    data_bits = 0

    for _ in range(24):

        GPIO.output(CLOCK_PIN, GPIO.HIGH)

        data_bits = (
            (data_bits << 1)
            | GPIO.input(DATA_PIN)
        )

        GPIO.output(CLOCK_PIN, GPIO.LOW)

    GPIO.output(CLOCK_PIN, GPIO.HIGH)
    GPIO.output(CLOCK_PIN, GPIO.LOW)

    if data_bits & 0x800000:
        data_bits -= 0x1000000

    return data_bits


# -------------------------------------------------
# FILTRERAD MÄTNING
# -------------------------------------------------

def las_filtrerat_varde():

    matningar = []

    while len(matningar) < ANTAL_MATNINGAR:

        varde = las_hx711()

        if varde is not None:
            matningar.append(varde)

        time.sleep(0.02)

    matningar.sort()

    filtrerade = matningar[
        ANTAL_BORTTAGNA:
        -ANTAL_BORTTAGNA
    ]

    return sum(filtrerade) / len(filtrerade)


# -------------------------------------------------
# TARE
# -------------------------------------------------

def tare():

    print()
    print("Nollställer vågen...")

    time.sleep(1)

    offset = las_filtrerat_varde()

    print(f"Ny offset: {offset:.0f}")
    print()

    return offset


# -------------------------------------------------
# CONFIG
# -------------------------------------------------

def las_config():

    try:
        with open(CONFIG_FIL, "r") as fil:
            return json.load(fil)

    except Exception as e:

        print(f"Kunde inte läsa {CONFIG_FIL}: {e}")

        return {
            "keg_tare_kg": 4.5,
            "keg_capacity_l": 19.0,
            "beer_density_kg_per_l": 1.01
        }


# -------------------------------------------------
# CONTROL
# -------------------------------------------------

def las_control():

    try:

        with open(CONTROL_FIL, "r") as fil:
            return json.load(fil)

    except Exception:

        return {
            "tare": False
        }


def aterstall_control():

    data = {
        "tare": False
    }

    with open(CONTROL_FIL, "w") as fil:
        json.dump(data, fil, indent=4)


# -------------------------------------------------
# JSON STATUS
# -------------------------------------------------

def skriv_json(vikt_gram):

    config = las_config()

    total_vikt_kg = vikt_gram / 1000.0

    keg_tare_kg = config["keg_tare_kg"]
    keg_capacity_l = config["keg_capacity_l"]
    beer_density = config["beer_density_kg_per_l"]

    beer_weight_kg = total_vikt_kg - keg_tare_kg

    if beer_weight_kg < 0:
        beer_weight_kg = 0.0

    beer_liters = beer_weight_kg / beer_density

    fill_percent = (
        beer_liters / keg_capacity_l
    ) * 100.0

    if fill_percent < 0:
        fill_percent = 0.0

    if fill_percent > 100:
        fill_percent = 100.0

    data = {
        "weight_g": round(vikt_gram, 1),
        "weight_kg": round(total_vikt_kg, 3),

        "beer_weight_kg": round(beer_weight_kg, 3),
        "beer_liters": round(beer_liters, 2),
        "fill_percent": round(fill_percent, 1),

        "keg_tare_kg": keg_tare_kg,
        "keg_capacity_l": keg_capacity_l,
        "beer_density_kg_per_l": beer_density,

        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    with open(JSON_FIL, "w") as fil:
        json.dump(data, fil, indent=4)


# -------------------------------------------------
# HUVUDPROGRAM
# -------------------------------------------------

reset_hx711()

offset = tare()

print("--- KEG-SCALE STARTAD ---")
print("Tryck Ctrl+C för att avsluta.")
print()

try:

    while True:

        # -----------------------------------------
        # Kontrollera webbkommando
        # -----------------------------------------

        control = las_control()

        if control.get("tare"):

            print()
            print("Tarering begärd från webben.")

            offset = tare()

            aterstall_control()


        # -----------------------------------------
        # Läs vikt
        # -----------------------------------------

        aktuellt_varde = las_filtrerat_varde()

        differens = aktuellt_varde - offset

        vikt_gram = (
            -differens
            / KALIBRERINGS_FAKTOR
        )

        if abs(vikt_gram) < 5:
            vikt_gram = 0.0

        skriv_json(vikt_gram)

        print(
            f"Rå: {aktuellt_varde:10.0f} | "
            f"Skillnad: {differens:9.0f} | "
            f"Vikt: {vikt_gram:8.1f} g",
            end="\r"
        )

        time.sleep(0.1)


except KeyboardInterrupt:

    print()
    print("Keg-Scale avslutad.")


finally:

    GPIO.cleanup()