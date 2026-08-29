
import time
import RPi.GPIO as GPIO

DATA_PIN = 6
CLOCK_PIN = 5

KALIBRERINGS_FAKTOR = 20.19
ANTAL_MATNINGAR = 30

GPIO.setmode(GPIO.BCM)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(DATA_PIN, GPIO.IN)

print("Gör en hård återställning av HX711...")

# Power-down / reset
GPIO.output(CLOCK_PIN, GPIO.HIGH)
time.sleep(0.005)

# Starta HX711 igen
GPIO.output(CLOCK_PIN, GPIO.LOW)
time.sleep(0.2)


def las_hx711_direkt():
    """Läser ett råvärde från HX711."""

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

    # 25:e klockpulsen:
    # Kanal A, Gain 128
    GPIO.output(CLOCK_PIN, GPIO.HIGH)
    GPIO.output(CLOCK_PIN, GPIO.LOW)

    # Konvertera 24-bit signed
    if data_bits & 0x800000:
        data_bits -= 0x1000000

    return data_bits


def las_filtrerat_varde():
    """
    Tar 10 mätningar.
    Tar bort högsta och lägsta.
    Returnerar medelvärdet av de återstående 8.
    """

    matningar = []

    while len(matningar) < ANTAL_MATNINGAR:

        varde = las_hx711_direkt()

        if varde is not None:
            matningar.append(varde)

        time.sleep(0.02)

    # Sortera från lägst till högst
    matningar.sort()

    # Ta bort de 5 lägsta och 5 högsta värdena
    filtrerade = matningar[5:-5]

    # Medelvärde av de 20 återstående
    medel = sum(filtrerade) / len(filtrerade)

    return medel


# -------------------------------------------------
# NOLLSTÄLLNING
# -------------------------------------------------

print()
print("Nollställer vågen...")
print("Vågen måste vara helt tom.")
print()

time.sleep(2)

offset = las_filtrerat_varde()

print(f"Nollställning klar.")
print(f"Offset: {offset:.0f}")
print(f"Kalibreringsfaktor: {KALIBRERINGS_FAKTOR}")
print()
print("--- STARTAR VIKTMÄTNING ---")
print("Tryck Ctrl+C för att avsluta.")
print()


try:

    while True:

        aktuellt_varde = las_filtrerat_varde()

        differens = aktuellt_varde - offset

        vikt_gram = differens / KALIBRERINGS_FAKTOR

        # Små variationer runt noll visas som 0
        if abs(vikt_gram) < 5:
            vikt_gram = 0.0

        print(
            f"Rå: {aktuellt_varde:10.0f} | "
            f"Skillnad: {differens:8.0f} | "
            f"Vikt: {vikt_gram:8.1f} g",
            end="\r"
        )

        time.sleep(0.1)


except KeyboardInterrupt:

    print()
    print()
    print("Programmet avslutat.")


finally:

    GPIO.cleanup()
