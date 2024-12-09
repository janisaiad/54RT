import random
import csv
import numpy as np
import matplotlib.pyplot as plt
import os
from multiprocessing import Pool, cpu_count


# Dictionnaires fournis
TA_dic = {
    "f1": 8417,
    "f2": 8900,
    "DI": [0.2, 12.8],
    "DTOA": [2050, 4100]
}

MULTIFCT_dic = {
    "f1": 8700,
    "f2": 9600,
    "DI": [2, 5, 8, 12, 20],
    "DTOA": [60]
}

CONDUITE_TIR_1_dic = {
    "f1": 8542,
    "f2": 8977,
    "DI": [0.1, 0.8],
    "DTOA": [300, 500]
}

SUR_SURFACE_dic = {
    "f1": 8500,
    "f2": 9500,
    "DI": [0.2, 0.5, 8],
    "DTOA": [720, 804]
}

VEILLE_COMBINEE_dic = {
    "f1": 9225,
    "f2": 9900,
    "DI": [0.25, 1.9, 7],
    "DTOA": [30, 50, 250, 380]
}

CONDUITE_TIR_2_dic = {
    "f1": 8500,
    "f2": 9100,
    "DI": [0.1, 3.2],
    "DTOA": [80, 110]
}

dict_list = [
    ("TA_dic", TA_dic),
    ("MULTIFCT_dic", MULTIFCT_dic),
    ("CONDUITE_TIR_1_dic", CONDUITE_TIR_1_dic),
    ("SUR_SURFACE_dic", SUR_SURFACE_dic),
    ("VEILLE_COMBINEE_dic", VEILLE_COMBINEE_dic),
    ("CONDUITE_TIR_2_dic", CONDUITE_TIR_2_dic)
]

sampling_rate = 20000
modulations = ["impulsionnel", "FMCW", "CW", "chirp"]

# Chemins vers les fichiers CSV dans le nouveau dossier classification/data
output_features_path = os.path.join(os.path.dirname(__file__), "data", "output_features.csv")
eval_path = os.path.join(os.path.dirname(__file__), "data", "eval.csv")

def generate_signal_features(index):  # Added index parameter
    # Sélection aléatoire du dictionnaire
    dict_name, chosen_dict = random.choice(dict_list)

    # Choix DI et DTOA
    chosen_DI = random.choice(chosen_dict["DI"])
    chosen_DTOA = random.choice(chosen_dict["DTOA"])

    # Choix de la modulation
    chosen_modulation = random.choice(modulations)

    # Paramètres du signal
    f1 = chosen_dict["f1"]
    f2 = chosen_dict["f2"]
    T_emit = chosen_DI
    dtoa = chosen_DTOA

    # T_total = DI + DTOA
    T_total = T_emit + dtoa
    t = np.arange(0, T_total, 1/sampling_rate)
    signal_emit = np.zeros_like(t)
    signal_duration = int(T_emit * sampling_rate)

    # Génération du signal sur [0, DI]
    if chosen_modulation == "impulsionnel":
        f_random = np.random.uniform(f1, f2)
        t_imp = t[:signal_duration]
        seg_duration = T_emit
        t_centered = t_imp - (seg_duration / 2)
        sigma = T_emit/6.0
        envelope = np.exp(-t_centered**2/(2*sigma**2))
        impulse_signal = envelope * np.sin(2*np.pi*f_random*t_imp)
        signal_emit[:signal_duration] = impulse_signal

    elif chosen_modulation == "FMCW":
        t_seg = t[:signal_duration]
        half = T_emit/2
        f_inst = np.zeros(signal_duration)
        for i in range(signal_duration):
            tau = i/sampling_rate
            if tau < half:
                f_inst[i] = f1 + (f2 - f1)*(tau/half)
            else:
                f_inst[i] = f2 - (f2 - f1)*((tau - half)/half)
        phase = np.cumsum(2*np.pi*f_inst/sampling_rate)
        fmcw_signal = np.sin(phase)
        signal_emit[:signal_duration] = fmcw_signal

    elif chosen_modulation == "CW":
        f_random = np.random.uniform(f1, f2)
        t_seg = t[:signal_duration]
        cw_signal = np.sin(2*np.pi*f_random*t_seg)
        signal_emit[:signal_duration] = cw_signal

    elif chosen_modulation == "chirp":
        t_seg = t[:signal_duration]
        k = (f2 - f1)/T_emit
        t_rel = t_seg - t_seg[0]
        chirp_signal = np.sin(2*np.pi*(f1*t_rel + 0.5*k*t_rel**2))
        signal_emit[:signal_duration] = chirp_signal

    # FFT sur la zone DI
    di_signal = signal_emit[:signal_duration]
    N = len(di_signal)
    if N == 0:
        di_signal = np.array([0])
        N = 1

    freqs = np.fft.fftfreq(N, d=1/sampling_rate)
    di_fft = np.fft.fft(di_signal)
    half = N//2
    freqs_plot = freqs[:half]
    fft_magnitude = np.abs(di_fft[:half])*(2/N) if N>0 else [0]

    # Calcul des caractéristiques pour l'embedding
    amplitude_max = np.max(fft_magnitude)
    energie_totale = np.sum(fft_magnitude**2)
    freq_dominante = freqs_plot[np.argmax(fft_magnitude)]
    
    # Calcul de la bande passante à -3dB
    max_amp = np.max(fft_magnitude)
    threshold = max_amp / np.sqrt(2)
    mask = fft_magnitude >= threshold
    if np.any(mask):
        freq_min = np.min(freqs_plot[mask])
        freq_max = np.max(freqs_plot[mask])
        bande_passante = freq_max - freq_min
    else:
        bande_passante = 0
        
    # Moments statistiques
    moyenne = np.mean(fft_magnitude)
    variance = np.var(fft_magnitude)
    asymetrie = np.mean(((fft_magnitude - moyenne)/np.std(fft_magnitude))**3) if variance > 0 else 0
    kurtosis = np.mean(((fft_magnitude - moyenne)/np.std(fft_magnitude))**4) - 3 if variance > 0 else 0

    return (chosen_DI, chosen_DTOA, chosen_modulation, dict_name,
            amplitude_max, energie_totale, freq_dominante, bande_passante,
            moyenne, variance, asymetrie, kurtosis)

def generate_data(create_features=True, create_eval=True):
    # Nombre de processeurs à utiliser
    num_processes = cpu_count()
    
    if create_features:
        with open(output_features_path, "w", newline='') as features_file:
            features_writer = csv.writer(features_file)
            features_writer.writerow([
                "DI choisi", "DTOA choisi", 
                "amplitude_max", "energie_totale", "freq_dominante", "bande_passante",
                "moyenne", "variance", "asymetrie", "kurtosis",
                "modulation", "dict_name"
            ])
            
            # Utilisation de multiprocessing pour générer les données d'entraînement
            with Pool(num_processes) as pool:
                results = pool.map(generate_signal_features, range(Nombre))
                
            for result in results:
                features_writer.writerow([
                    result[0], result[1],  # DI, DTOA
                    result[4], result[5], result[6], result[7],  # Features
                    result[8], result[9], result[10], result[11],  # Moments statistiques
                    result[2], result[3]  # Modulation, dict_name
                ])
    
    if create_eval:
        with open(eval_path, "w", newline='') as eval_file:
            eval_writer = csv.writer(eval_file)
            eval_writer.writerow([
                "DI choisi", "DTOA choisi",
                "amplitude_max", "energie_totale", "freq_dominante", "bande_passante",
                "moyenne", "variance", "asymetrie", "kurtosis",
                "modulation", "dict_name"
            ])
            
            # Utilisation de multiprocessing pour générer les données d'évaluation
            with Pool(num_processes) as pool:
                results = pool.map(generate_signal_features, range(Nombre_eval))
                
            for result in results:
                eval_writer.writerow([
                    result[0], result[1],  # DI, DTOA
                    result[4], result[5], result[6], result[7],  # Features
                    result[8], result[9], result[10], result[11],  # Moments statistiques
                    result[2], result[3]  # Modulation, dict_name
                ])


if __name__ == "__main__":
    Nombre = 1000  # Nombre de lignes de données à générer
    Nombre_eval = 100  # Nombre de lignes pour l'évaluation
    generate_data(create_features=False, create_eval=True)  # Crée les deux fichiers