#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
from gnuradio import gr
from gnuradio import blocks
from gnuradio import fft
from gnuradio import analog
from gnuradio import filter
from gnuradio.fft import window
from gnuradio.filter import firdes
import osmosdr
import time  # Utilisation de time au lieu de gr.time

class RadarRadioReceiver(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Récepteur Radar/Radio")

        # Paramètres
        self.samp_rate = 2e6
        self.center_freq = 100e6
        self.gain = 20
        self.fft_size = 1024

        # Source RTL-SDR
        self.rtl_source = osmosdr.source(
            args="numchan=" + str(1) + " " + "rtl=0"
        )
        self.rtl_source.set_sample_rate(self.samp_rate)
        self.rtl_source.set_center_freq(self.center_freq)
        self.rtl_source.set_freq_corr(0)
        self.rtl_source.set_gain(self.gain)
        self.rtl_source.set_if_gain(20)
        self.rtl_source.set_bb_gain(20)
        self.rtl_source.set_antenna("")

        # Stream to Vector
        self.s2v = blocks.stream_to_vector(gr.sizeof_gr_complex, self.fft_size)

        # FFT
        self.fft_block = fft.fft_vcc(
            self.fft_size, 
            True, 
            window.blackmanharris(self.fft_size),
            True, 
            1
        )

        # Magnitude
        self.mag = blocks.complex_to_mag_squared(self.fft_size)

        # Vector to Stream
        self.v2s = blocks.vector_to_stream(gr.sizeof_float, self.fft_size)

        # Moyenne mobile
        self.avg = blocks.moving_average_ff(
            100,    # Taille fenêtre
            1,      # Scale
            4000    # Max items
        )

        # Probe signal
        self.probe = blocks.probe_signal_f()

        # Connexions
        self.connect(self.rtl_source, self.s2v)
        self.connect(self.s2v, self.fft_block)
        self.connect(self.fft_block, self.mag)
        self.connect(self.mag, self.v2s)
        self.connect(self.v2s, self.avg)
        self.connect(self.avg, self.probe)

    def get_signal_characteristics(self):
        """Récupère et affiche les caractéristiques du signal"""
        while True:
            try:
                # Récupération puissance
                power_level = self.probe.level()
                
                # Éviter les valeurs nulles ou négatives
                if power_level <= 0:
                    power_level = 1e-10  # Valeur minimale pour éviter log(0)
                
                # Calcul SNR
                noise_floor = -90  # dBm (estimation)
                power_db = 10 * np.log10(power_level)
                snr = power_db - noise_floor
                
                print("\nCaractéristiques du signal:")
                print(f"Fréquence centrale : {self.center_freq/1e6:.2f} MHz")
                print(f"Taux d'échantillonnage : {self.samp_rate/1e6:.2f} MHz")
                print(f"Gain : {self.gain} dB")
                print(f"Niveau de puissance : {power_db:.2f} dBm")
                print(f"SNR estimé : {snr:.2f} dB")
                print(f"Niveau brut : {power_level}")
                print("-" * 50)
                
                time.sleep(1)  # Utilisation de time.sleep au lieu de gr.time.sleep
                
            except KeyboardInterrupt:
                print("\nArrêt du récepteur...")
                break
            except Exception as e:
                print(f"Erreur: {str(e)}")
                break

def main():
    print("=== Récepteur RTL-SDR ===")
    print(f"GNU Radio version: {gr.version()}")
    print("Initialisation du récepteur...")
    
    tb = RadarRadioReceiver()
    print("Démarrage de l'acquisition...")
    tb.start()
    
    try:
        tb.get_signal_characteristics()
    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur")
    finally:
        print("Arrêt du récepteur...")
        tb.stop()
        tb.wait()
        print("Terminé.")

if __name__ == '__main__':
    main()
