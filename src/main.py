from lib.wifi_manager import WiFiManager
from machine import Pin
import time

# Configuration
WIFI_SSID = "Mon_Reseau"
WIFI_PASS = "Mon_Mot_De_Passe"

# LED pour le statut
status_led = Pin(2, Pin.OUT)

def main():
    # Initialisation WiFi
    wifi = WiFiManager(WIFI_SSID, WIFI_PASS)
    wifi.connect()
    
    # Boucle principale
    while True:
        status_led.value(not status_led.value())  # Toggle LED
        time.sleep(1)

if __name__ == "__main__":
    main() 