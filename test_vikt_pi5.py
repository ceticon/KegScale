import time
import RPi.GPIO as GPIO

# --- KONFIGURATION ---
DATA_PIN = 6   # DT på HX711
CLOCK_PIN = 5  # SCK på HX711

# --- DIN NYA KALIBRERING ---
KALIBRERINGS_FAKTOR = 16.46  # Räknat ut från dina 1615 gram

print("Initierar GPIO-läge...")
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(DATA_PIN, GPIO.IN)

GPIO.output(CLOCK_PIN, GPIO.HIGH)
time.sleep(0.0001)
GPIO.output(CLOCK_PIN, GPIO.LOW)

def las_hx711_direkt():
    for _ in range(200):
        if GPIO.input(DATA_PIN) == 0:
            break
        time.sleep(0.001)
    else:
        return None

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

# --- AUTOMATISK NOLLSTÄLLNING (TARE) ---
print("\nNollställer vågen... Ställ inget på vågen.")
time.sleep(1)

summa = 0
lyckade_mätningar = 0
# Vi tar ett rejält medelvärde vid start för en perfekt nollpunkt
for _ in range(30):
    v = las_hx711_direkt()
    if v is not None:
        summa += v
        lyckade_mätningar += 1
    time.sleep(0.03)

offset = summa / lyckade_mätningar if lyckade_mätningar > 0 else 4199100
print(f"Nollställd! (Offset: {int(offset)})\n")

print("--- STARTAR VIKTMÄTNING ---")
print("Tryck Ctrl+C för att avsluta.\n")

# Lista för att spara de senaste avläsningarna (glidande medelvärde)
historik = []
BUFFERT_STORLEK = 10 # Ju högre siffra, desto stabilare (men långsammare) våg

try:
    while True:
        varde = las_hx711_direkt()
        
        if varde is not None:
            relativt_varde = varde - offset
            
            # Lägg till i vår historik-buffert
            historik.append(relativt_varde)
            if len(historik) > BUFFERT_STORLEK:
                historik.pop(0) # Ta bort det äldsta värdet
            
            # Räkna ut medelvärdet av de 10 senaste avläsningarna
            filtrerat_relativt = sum(historik) / len(historik)
            
            # Räkna ut vikten i gram
            vikt_gram = filtrerat_relativt / KALIBRERINGS_FAKTOR
            
            # Visa vikten (och dölj minusvärden nära noll orsakade av litet brus)
            if abs(vikt_gram) < 5: 
                vikt_gram = 0.0
                
            print(f"Vikt: {vikt_gram:.1f} g  (Rå-brus: {int(relativt_varde):<5})", end="\r")
        
        time.sleep(0.1) # Snabbare uppdatering nu när vi har filter

except KeyboardInterrupt:
    print("\nProgrammet avslutat.")
finally:
    GPIO.cleanup()
