from network import WLAN
import machine
import time

class WiFiManager:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = WLAN(mode=WLAN.STA)
    
    def connect(self):
        if not self.wlan.isconnected():
            print("Connexion au WiFi...")
            self.wlan.connect(self.ssid, auth=(WLAN.WPA2, self.password))
            
            # Attente de la connexion
            while not self.wlan.isconnected():
                time.sleep(1)
                
        print(f"Connecté à {self.ssid}")
        print(f"IP: {self.wlan.ifconfig()[0]}") 