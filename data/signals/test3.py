import numpy as np
import matplotlib.pyplot as plt
import random

########################################
# Dictionnaires
########################################
TA_dic = {
    "f1": 8417e2,
    "f2": 8900e2,
    "DI": [0.2e-3, 12.8e-3],
    "DTOA": [2050e-3, 4100e-3]
}

MULTIFCT_dic = {
    "f1": 8700e2,
    "f2": 9600e2,
    "DI": [2e-3, 5e-3, 8e-3, 12e-3, 20e-3],
    "DTOA": [60e-3]
}

dict_list = [
    ("TA_dic", TA_dic),
    ("MULTIFCT_dic", MULTIFCT_dic)
]

########################################
# Fonctions
########################################

def generate_signal_segment(f1, f2, DI_values, DTOA_values, modulation, sampling_rate):
    chosen_DI = random.choice(DI_values)
    chosen_DTOA = random.choice(DTOA_values)
    T_emit = chosen_DI
    dtoa = chosen_DTOA
    T_total = T_emit + dtoa

    t = np.arange(0, T_total, 1/sampling_rate)
    signal_emit = np.zeros_like(t)
    signal_duration = int(T_emit * sampling_rate)

    if modulation == "impulsionnel":
        f_random = np.random.uniform(f1, f2)
        t_imp = t[:signal_duration]
        seg_duration = T_emit
        t_centered = t_imp - (seg_duration / 2)
        sigma = T_emit/6.0
        envelope = np.exp(-t_centered**2/(2*sigma**2))
        impulse_signal = envelope * np.sin(2*np.pi*f_random*t_imp)
        signal_emit[:signal_duration] = impulse_signal

    elif modulation == "FMCW":
        t_seg = t[:signal_duration]
        k = (f2 - f1) / T_emit
        f_inst = f1 + k * t_seg
        phase = np.cumsum(2*np.pi * f_inst / sampling_rate)
        fmcw_signal = np.sin(phase)
        signal_emit[:signal_duration] = fmcw_signal

    return signal_emit


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

    return max_signal, di_segments, dtoa_segments, di_times, dtoa_times


def compute_fft_for_di_segments(di_segments, sampling_rate):
    fft_results = []
    for i, segment in enumerate(di_segments):
        N = len(segment)
        if N == 0:
            print(f"[DEBUG FFT] Le segment DI {i+1} est vide, aucune FFT calculée.")
            continue

        # Appliquer une fenêtre pour réduire le leakage
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


########################################
# Test complet
########################################

if __name__ == "__main__":
    sampling_rate = 1e6  # Augmentation du taux d'échantillonnage à 1 MHz
    epsilon = 0.001
    Nombre_signal = 5

    dict_name, chosen_dict = random.choice(dict_list)
    modulation = "impulsionnel"

    final_signal = np.array([])
    for _ in range(Nombre_signal):
        segment = generate_signal_segment(
            chosen_dict["f1"],
            chosen_dict["f2"],
            chosen_dict["DI"],
            chosen_dict["DTOA"],
            modulation,
            sampling_rate
        )
        final_signal = np.concatenate((final_signal, segment))

    max_signal, di_segments, dtoa_segments, di_times, dtoa_times = analyze_signal(final_signal, epsilon, sampling_rate)

    fft_results = compute_fft_for_di_segments(di_segments, sampling_rate)

    # Affichage des segments DI avec leurs FFT
    for i, (segment, fft_data) in enumerate(zip(di_segments, fft_results)):
        t_segment = np.arange(0, len(segment)) / sampling_rate

        plt.figure(figsize=(12, 5))

        # Segment DI
        plt.subplot(1, 2, 1)
        plt.plot(t_segment, segment)
        plt.title(f"Segment DI {i+1}")
        plt.xlabel("Temps (s)")
        plt.ylabel("Amplitude")
        plt.grid(True)

        # FFT
        plt.subplot(1, 2, 2)
        plt.plot(fft_data["frequencies"], fft_data["amplitudes"])
        plt.title(f"FFT DI {i+1}")
        plt.xlabel("Fréquence (Hz)")
        plt.ylabel("Amplitude normalisée")
        plt.grid(True)

        plt.tight_layout()
        plt.show()
