#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
from gnuradio import gr
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
import osmosdr
import time
from datetime import datetime
import matplotlib.pyplot as plt

class SpectrumAnalyzer(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Analyseur de Spectre")

        # Paramètres
        self.samp_rate = 2e6
        self.fft_size = 1024
        self.freq_start = 370e6
        self.freq_end = 410e6
        self.freq_step = 1e6
        self.gain = 30
        self.threshold = -70
        self.dwell_time = 1

        # Source RTL-SDR
        self.rtl_source = osmosdr.source(args="numchan=" + str(1) + " " + "rtl=0")
        self.rtl_source.set_sample_rate(self.samp_rate)
        self.rtl_source.set_gain(self.gain)
        self.rtl_source.set_if_gain(20)
        self.rtl_source.set_bb_gain(20)
        self.rtl_source.set_antenna("")

        # FFT blocks
        self.s2v = blocks.stream_to_vector(gr.sizeof_gr_complex, self.fft_size)
        self.fft = fft.fft_vcc(
            self.fft_size,
            True,
            window.blackmanharris(self.fft_size),
            True,
            1
        )
        self.mag = blocks.complex_to_mag_squared(self.fft_size)
        self.probe = blocks.probe_signal_vf(self.fft_size)

        # Connexions
        self.connect(self.rtl_source, self.s2v, self.fft, self.mag, self.probe)

    def scan_spectrum(self):
        """Scanne le spectre et retourne les pics et les données complètes"""
        results = []
        all_frequencies = []
        all_powers = []
        
        num_steps = int((self.freq_end - self.freq_start) / self.freq_step)
        
        for i in range(num_steps):
            current_freq = self.freq_start + i * self.freq_step
            self.rtl_source.set_center_freq(current_freq)
            
            time.sleep(self.dwell_time)
            
            fft_data = np.array(self.probe.level())
            
            if len(fft_data) == 0:
                continue
                
            power_db = 10 * np.log10(fft_data + 1e-10)
            
            freq_step = self.samp_rate / self.fft_size
            frequencies = np.arange(current_freq - self.samp_rate/2,
                                  current_freq + self.samp_rate/2,
                                  freq_step)
            
            # Sauvegarde des données complètes pour le plot
            all_frequencies.extend(frequencies)
            all_powers.extend(power_db)
            
            # Sauvegarde des pics
            for freq, power in zip(frequencies, power_db):
                if power > self.threshold:
                    results.append((freq, float(power)))
        
        return sorted(results, key=lambda x: x[1], reverse=True), all_frequencies, all_powers

def plot_spectrum(frequencies, powers, peaks, timestamp):
    """Crée un plot du spectre"""
    plt.figure(figsize=(15, 8))
    plt.plot(np.array(frequencies)/1e6, powers, 'b-', label='Spectre', alpha=0.6)
    
    # Ajoute les pics détectés
    peak_freqs = [f/1e6 for f, _ in peaks[:10]]
    peak_powers = [p for _, p in peaks[:10]]
    plt.plot(peak_freqs, peak_powers, 'r^', label='Pics détectés', markersize=10)
    
    plt.grid(True)
    plt.xlabel('Fréquence (MHz)')
    plt.ylabel('Puissance (dBm)')
    plt.title(f'Analyse du Spectre {timestamp}')
    plt.legend()
    
    # Ajoute les annotations pour les pics
    for i, (freq, power) in enumerate(zip(peak_freqs, peak_powers)):
        plt.annotate(f'{freq:.3f} MHz\n{power:.1f} dBm',
                    xy=(freq, power),
                    xytext=(10, 10),
                    textcoords='offset points',
                    ha='left',
                    va='bottom',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    arrowprops=dict(arrowstyle='->'))
    
    # Sauvegarde
    plt.savefig(f'spectrum_{timestamp.replace(":", "-")}.png', dpi=300, bbox_inches='tight')
    plt.close()

def write_markdown(results, timestamp, filename="spectrum_analysis.md"):
    """Écrit les résultats dans un fichier Markdown"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"\n## Analyse du Spectre - {timestamp}\n\n")
        
        # Ajoute l'image
        f.write(f"![Spectre](spectrum_{timestamp.replace(':', '-')}.png)\n\n")
        
        f.write("| Fréquence (MHz) | Puissance (dBm) |\n")
        f.write("|-----------------|----------------|\n")
        
        for freq, power in results[:20]:
            f.write(f"| {freq/1e6:.3f} | {power:.2f} |\n")
        
        f.write("\n---\n")

def main():
    print("=== Analyseur de Spectre RTL-SDR ===")
    print(f"Plage de fréquences: 370-410 MHz")
    
    tb = SpectrumAnalyzer()
    print("Démarrage de l'analyse...")
    tb.start()
    
    try:
        while True:
            print("\nAnalyse du spectre en cours...")
            results, frequencies, powers = tb.scan_spectrum()
            
            if results:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                
                # Affichage console
                print("\nTop 10 des signaux les plus forts:")
                for i, (freq, power) in enumerate(results[:10], 1):
                    print(f"{i}. {freq/1e6:.3f} MHz: {power:.2f} dBm")
                
                # Création du plot
                plot_spectrum(frequencies, powers, results, timestamp)
                
                # Enregistrement dans le fichier Markdown
                write_markdown(results, timestamp)
                
            else:
                print("Aucun signal détecté au-dessus du seuil")
            
            print("\nAttente de 5 secondes...")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"Erreur: {str(e)}")
    finally:
        print("Arrêt de l'analyseur...")
        tb.stop()
        tb.wait()
        print("Terminé.")

if __name__ == '__main__':
    main()