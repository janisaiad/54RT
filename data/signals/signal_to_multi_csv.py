import numpy as np
import matplotlib.pyplot as plt
import csv
import random
import os


def analyze_signal(signal: np.ndarray, epsilon: float, sampling_rate: float):
    max_signal = np.max(np.abs(signal))
    threshold = epsilon * max_signal

    is_dtoa = np.abs(signal) < threshold
    min_dtoa_duration = 0.001
    min_dtoa_samples = int(min_dtoa_duration * sampling_rate)

    def extract_segments(mask, min_len):
        segments = []
        start = None
        for i, val in enumerate(mask):
            if val and start is None:
                start = i
            elif not val and start is not None:
                if i - start >= min_len:
                    segments.append((start, i - 1))
                start = None
        if start is not None and len(mask) - start >= min_len:
            segments.append((start, len(mask) - 1))
        return segments

    dtoa_indices = extract_segments(is_dtoa, min_dtoa_samples)
    dtoa_segments = [signal[s:e+1] for s, e in dtoa_indices]

    di_indices = []
    current_start = 0
    for (dtoa_start, dtoa_end) in dtoa_indices:
        if dtoa_start > current_start:
            di_indices.append((current_start, dtoa_start - 1))
        current_start = dtoa_end + 1

    if dtoa_indices and dtoa_indices[-1][1] < len(signal) - 1:
        di_indices.append((dtoa_indices[-1][1] + 1, len(signal) - 1))
    elif not dtoa_indices:
        di_indices.append((0, len(signal)-1))

    di_segments = [signal[s:e+1] for s, e in di_indices]

    # Convert indices to times
    dtoa_times = [(s / sampling_rate, e / sampling_rate) for s, e in dtoa_indices]
    di_times = [(s / sampling_rate, e / sampling_rate) for s, e in di_indices]

    return di_segments, dtoa_segments, di_times, dtoa_times


def get_segment_durations(times):
    return [end - start for start, end in times]


def compute_fft_for_di_segments(di_segments, sampling_rate):
    fft_results = []
    for i, segment in enumerate(di_segments):
        N = len(segment)
        if N == 0:
            print(f"[DEBUG FFT] Le segment DI {i+1} est vide, aucune FFT calculée.")
            fft_results.append({"frequencies": [], "amplitudes": []})
            continue

        # Appliquer une fenêtre pour réduire le leakage spectral
        window = np.hanning(N)
        segment_windowed = segment * window

        fft_vals = np.fft.fft(segment_windowed)
        fft_freqs = np.fft.fftfreq(N, d=1/sampling_rate)

        half_N = N // 2
        freqs = fft_freqs[:half_N]
        amplitudes = np.abs(fft_vals[:half_N]) * (2 / N)

        # Debug FFT
        print(f"[DEBUG FFT] Segment DI {i+1}:")
        print(f"  Nombre d'échantillons: {N}")
        print(f"  Fréquence max dans FFT: {np.max(freqs)} Hz")
        print(f"  Amplitude max dans FFT: {np.max(amplitudes)}")

        fft_results.append({"frequencies": freqs, "amplitudes": amplitudes})
    return fft_results

import os
import csv

def process_signal_and_save_csv(signal, sampling_rate, epsilon, output_dir="output_csv"):
    # Analyse du signal
    di_segments, dtoa_segments, di_times, dtoa_times = analyze_signal(signal, epsilon, sampling_rate)
    fft_results = compute_fft_for_di_segments(di_segments, sampling_rate)

    # Calcul des durées
    di_durations = get_segment_durations(di_times)
    dtoa_durations = get_segment_durations(dtoa_times)

    # Création du répertoire de sortie
    os.makedirs(output_dir, exist_ok=True)

    # Sauvegarde
    for i, (segment, fft_result) in enumerate(zip(di_segments, fft_results)):
        di_duration = di_durations[i]
        dtoa_duration = dtoa_durations[i] if i < len(dtoa_durations) else 0

        # Construire la liste [(freq, amplitude), ...]
        fft_list = [(float(freq), float(ampl)) for freq, ampl in zip(fft_result["frequencies"], fft_result["amplitudes"])]

        # Préparer les données pour le CSV
        # Ligne 1 : en-tête
        rows = [["Durée DI", "Durée DTOA Suivant", "FFT (Freq, Amplitude)"]]

        # Ligne 2 : DI, DTOA, FFT sous forme de liste complète sur la même ligne
        rows.append([di_duration, dtoa_duration, fft_list])

        # Écriture du fichier CSV
        file_name = f"{output_dir}/DI_{i+1}.csv"
        with open(file_name, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        print(f"[INFO] Fichier CSV sauvegardé : {file_name}")

sampling_rate = 2e6
epsilon = 0.01