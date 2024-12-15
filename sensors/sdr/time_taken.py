#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from gnuradio import gr
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
import osmosdr
import time
from datetime import datetime

class SpectrumAnalyzer(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "FFT Timing Test")

        # Paramètres
        self.samp_rate = 2e6      
        self.fft_size = 4096      
        self.freq_start = 800e3   
        self.freq_end = 1050e3    
        self.gain = 40
        
        # Source RTL-SDR
        self.source = osmosdr.source(args="numchan=" + str(1) + " " + "rtl=0")
        self.source.set_sample_rate(self.samp_rate)
        self.source.set_center_freq((self.freq_start + self.freq_end) / 2)
        self.source.set_gain(self.gain)
        self.source.set_if_gain(20)
        self.source.set_bb_gain(20)
        self.source.set_antenna("")

        # FFT blocks
        self.s2v = blocks.stream_to_vector(gr.sizeof_gr_complex, self.fft_size)
        window_taps = window.blackmanharris(self.fft_size)
        self.fft = fft.fft_vcc(
            self.fft_size,
            True,
            window_taps,
            True,
            1
        )
        self.mag = blocks.complex_to_mag_squared(self.fft_size)
        self.probe = blocks.probe_signal_vf(self.fft_size)

        # Connexions
        self.connect(self.source, self.s2v, self.fft, self.mag, self.probe)

    def get_fft_data(self):
        """Récupère les données FFT"""
        return np.array(self.probe.level())

def main():
    print("=== Test de Performance FFT RTL-SDR ===")
    print(f"Fréquences: 800-1050 kHz")
    print(f"Taux d'échantillonnage: 2 MHz")
    print(f"Taille FFT: 4096 points")
    
    # Création de l'analyseur
    tb = SpectrumAnalyzer()
    
    # Démarrage
    print("\nDémarrage du test...")
    tb.start()
    
    try:
        num_samples = 1000  # Nombre de FFT à mesurer
        times = []
        
        print(f"\nMesure du temps pour {num_samples} FFT...")
        for i in range(num_samples):
            start_time = time.perf_counter()
            
            # Récupération des données FFT
            fft_data = tb.get_fft_data()
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
            
            if (i + 1) % 100 == 0:
                print(f"Progression: {i + 1}/{num_samples}")
        
        # Analyse des résultats
        times = np.array(times)
        avg_time = np.mean(times)
        std_time = np.std(times)
        min_time = np.min(times)
        max_time = np.max(times)
        rate = 1.0 / avg_time
        
        print("\nRésultats:")
        print(f"Temps moyen par FFT: {avg_time*1000:.2f} ms (±{std_time*1000:.2f} ms)")
        print(f"Temps min: {min_time*1000:.2f} ms")
        print(f"Temps max: {max_time*1000:.2f} ms")
        print(f"Taux de FFT possible: {rate:.1f} FFT/s")
        print(f"Résolution temporelle possible pour spectrogramme: {1000/rate:.1f} ms")
            
    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur")
    finally:
        print("\nArrêt de l'analyseur...")
        tb.stop()
        tb.wait()
        print("Test terminé.")

if __name__ == '__main__':
    main()