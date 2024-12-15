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

        # Paramètres adaptés pour RTL-SDR
        self.samp_rate = 2e6      # 2 MHz (maximum stable pour RTL-SDR)
        self.fft_size = 1024
        self.freq_start = 370e6   # 370 MHz
        self.freq_end = 410e6     # 410 MHz
        self.freq_step = 1e6      # 1 MHz steps
        self.gain = 30
        self.threshold = -70
        self.dwell_time = 0.1
        self.history_size = 60    # 60 scans pour le spectrogramme

        # Buffer pour le spectrogramme
        self.spectrogram_buffer = []
        
        # Source RTL-SDR
        self.source = osmosdr.source(args="numchan=" + str(1) + " " + "rtl=0")
        self.source.set_sample_rate(self.samp_rate)
        self.source.set_gain(self.gain)
        self.source.set_if_gain(20)
        self.source.set_bb_gain(20)
        self.source.set_antenna("")

        # Blocs de traitement
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
        self.connect(self.source, self.s2v, self.fft, self.mag, self.probe)

    def scan_spectrum(self):
        """Scanne le spectre et retourne les données pour le spectrogramme"""
        spectrum_data = []
        results = []
        
        num_steps = int((self.freq_end - self.freq_start) / self.freq_step)
        
        for i in range(num_steps):
            current_freq = self.freq_start + i * self.freq_step
            self.source.set_center_freq(current_freq)
            
            time.sleep(self.dwell_time)
            
            try:
                fft_data = np.array(self.probe.level())
                if len(fft_data) == 0:
                    continue
                    
                power_db = 10 * np.log10(fft_data + 1e-10)
                spectrum_data.extend(power_db)
                
                # Calcul des fréquences pour ce segment
                freq_step = self.samp_rate / self.fft_size
                frequencies = np.arange(current_freq - self.samp_rate/2,
                                      current_freq + self.samp_rate/2,
                                      freq_step)
                
                for freq, power in zip(frequencies, power_db):
                    if power > self.threshold:
                        results.append((freq, float(power)))
                        
            except Exception as e:
                print(f"Erreur pendant le scan: {str(e)}")
                continue
        
        # Mise à jour du buffer du spectrogramme
        if spectrum_data:
            self.spectrogram_buffer.append(spectrum_data)
            if len(self.spectrogram_buffer) > self.history_size:
                self.spectrogram_buffer.pop(0)
        
        return sorted(results, key=lambda x: x[1], reverse=True)

def plot_spectrogram(analyzer, timestamp):
    """Crée et sauve le spectrogramme"""
    if not analyzer.spectrogram_buffer:
        print("Pas de données pour le spectrogramme")
        return
        
    plt.figure(figsize=(15, 10))
    
    # Création du spectrogramme
    spectrogram_data = np.array(analyzer.spectrogram_buffer)
    
    # Calcul des axes
    freq_axis = np.linspace(analyzer.freq_start/1e6, 
                           analyzer.freq_end/1e6, 
                           spectrogram_data.shape[1])
    time_axis = np.arange(spectrogram_data.shape[0]) * \
                (analyzer.dwell_time * len(freq_axis))
    
    # Plot du spectrogramme
    plt.pcolormesh(freq_axis, 
                   time_axis, 
                   spectrogram_data,
                   shading='auto',
                   cmap='viridis')
    
    plt.colorbar(label='Puissance (dBm)')
    plt.xlabel('Fréquence (MHz)')
    plt.ylabel('Temps (s)')
    plt.title(f'Spectrogramme {analyzer.freq_start/1e6:.0f}-{analyzer.freq_end/1e6:.0f} MHz - {timestamp}')
    
    # Ajout d'informations techniques
    plt.text(0.02, 0.98, 
             f'Taux échantillonnage: {analyzer.samp_rate/1e6:.1f} MHz\n'
             f'Résolution FFT: {analyzer.fft_size} points\n'
             f'Pas de fréquence: {analyzer.freq_step/1e6:.1f} MHz',
             transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8),
             verticalalignment='top')
    
    # Sauvegarde
    plt.savefig(f'spectrogram/spectrogram_{timestamp.replace(":", "-")}.png', 
                dpi=300, 
                bbox_inches='tight')
    plt.close()

def write_markdown(results, timestamp, filename="rtlsdr_analysis.md"):
    """Écrit les résultats dans un fichier Markdown"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"\n## Analyse Spectrale - {timestamp}\n\n")
        
        # Ajout du spectrogramme
        f.write(f"![Spectrogramme](spectrogram_{timestamp.replace(':', '-')}.png)\n\n")
        
        f.write("### Pics de Signal Détectés\n\n")
        f.write("| Fréquence (MHz) | Puissance (dBm) |\n")
        f.write("|-----------------|----------------|\n")
        
        for freq, power in results[:20]:
            f.write(f"| {freq/1e6:.3f} | {power:.2f} |\n")
        
        f.write("\n---\n")

def main():
    print("=== Analyseur de Spectre RTL-SDR ===")
    print(f"Plage: 370-410 MHz")
    print(f"Taux d'échantillonnage: 2 MHz")
    
    tb = SpectrumAnalyzer()
    print("Démarrage de l'analyse...")
    tb.start()
    
    try:
        while True:
            print("\nAcquisition du spectrogramme...")
            
            # Acquisition de plusieurs scans pour le spectrogramme
            for _ in range(tb.history_size):
                results = tb.scan_spectrum()
                print(".", end="", flush=True)
                time.sleep(0.1)
            
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            
            # Création du spectrogramme
            plot_spectrogram(tb, timestamp)
            
            # Sauvegarde des résultats
            write_markdown(results, timestamp)
            
            print("\nSpectrogramme sauvegardé")
            print("Attente de 5 secondes...")
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