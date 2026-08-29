import time
import RPi.GPIO as GPIO

DATA_PIN = 6
CLOCK_PIN = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(DATA_PIN, GPIO.IN)

print("Gör en hård återställning av HX711...")
# Att hålla SCK hög i över 60µs sätter chippet i power-down.
# Vi håller den hög i 5 millisekunder för att garantera att det somnar ordentligt.
GPIO.output(CLOCK_PIN, GPIO.HIGH)
time.sleep(0.005)
# Dra ner klockan igen för att väcka chippet till liv
GPIO.output(CLOCK_PIN, GPIO.LOW)
time.sleep(0.1) # Vänta på att chippet ska starta upp internoscillatorn

def las_hx711_direkt():
    # Vi ökar väntetiden till 1000 iterationer (ger chippet mer tid att bli redo)
    for _ in range(1000):
        if GPIO.input(DATA_PIN) == 0:
            break
        time.sleep(0.001)
    else:
        # Om pinnen fortfarande är hög (1), skriv ut det för felsökning
        return "INTE_REDO"

    data_bits = 0
    for _ in range(24):
        GPIO.output(CLOCK_PIN, GPIO.HIGH)
        data_bits = (data_bits << 1) | GPIO.input(DATA_PIN)
        GPIO.output(CLOCK_PIN, GPIO.LOW)

    GPIO.output(CLOCK_PIN, GPIO.HIGH)
    GPIO.output(CLOCK_PIN, GPIO.LOW)

    if data_bits & 0x800000:
        data_bits -= 0x1000000

    return data_bits

print("Läser in startvärde...")
start_v = None
for _ in range(10):
    test_v = las_hx711_direkt()
    if isinstance(test_v, int):
        start_v = test_v
        break
    time.sleep(0.1)

if start_v is None:
    print("--> Kunde inte sätta nollpunkt, sensorn svarar inte alls.")
    start_v = 4199100
else:
    print(f"--> Fysiskt startvärde (Offset) sparades som: {start_v}\n")

print("--- STARTAR REALTIDS-DEBUG ---")
try:
    while True:
        aktuellt_fysiskt = las_hx711_direkt()
        
        if isinstance(aktuellt_fysiskt, int):
            differens = aktuellt_fysiskt - start_v
            print(f"Start: {start_v} | Just nu: {aktuellt_fysiskt} | Skillnad: {differens}")
        else:
            # Skriv ut det faktiska spänningsläget på datapinnen just nu (bör vara 0 eller 1)
            print(f"Sensorn ej redo. Fysisk status på GPIO {DATA_PIN}: {GPIO.input(DATA_PIN)}")
            
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nAvslutat.")
finally:
    GPIO.cleanup()
