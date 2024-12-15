from pyhackrf import HackRf
import numpy as np

def main():
    # Initialisation du HackRF
    hackrf = HackRf()
    
    try:
        # Ouverture du périphérique
        hackrf.setup()
        
        # Configuration des paramètres
        sample_rate = 2e6  # 2 MHz
        freq = 100e6      # 100 MHz
        gain_if = 40      # Gain IF en dB
        gain_rf = 0       # Gain RF en dB
        
        # Configuration du HackRF
        hackrf.sample_rate = sample_rate
        hackrf.center_freq = freq
        hackrf.gain = gain_if
        hackrf.vga_gain = gain_rf
        
        # Lecture des échantillons
        samples = hackrf.read_samples(1024)
        
        # Traitement des données
        # Les échantillons sont sous forme complexe (I/Q)
        magnitude = np.abs(samples)
        print(f"Puissance moyenne: {np.mean(magnitude)}")
        
    finally:
        # Fermeture propre du périphérique
        hackrf.close()

if __name__ == "__main__":
    main()