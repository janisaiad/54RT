import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
import plotly.graph_objects as go
from simulate import dict_list, sampling_rate, modulations

# Set page config
st.set_page_config(
    page_title="Visualisation des signaux radar",
    page_icon="📊",
    layout="wide"
)

# Create tabs for different pages
tab1, tab2 = st.tabs(["Visualisation des signaux", "Résultats de classification"])

with tab1:
    def generate_signal(di, dtoa, modulation, chosen_dict, num_periods=1, zoom_di=False, zoom_fraction=1):
        """Génère un signal radar selon les paramètres choisis"""
        # Réduire la résolution temporelle pour les signaux longs
        if di + dtoa > 10:  # Si le signal est plus long que 10 secondes
            local_sampling_rate = 1000  # Réduire à 1kHz pour les longs signaux
        else:
            local_sampling_rate = sampling_rate
            
        T_total = di + dtoa
        if zoom_di:
            # Pour le zoom sur DI, on centre sur le milieu de DI
            zoom_duration = di/zoom_fraction
            t_start = (di/2) - (zoom_duration/2)
            t_end = (di/2) + (zoom_duration/2)
            t = np.arange(t_start, t_end, 1/local_sampling_rate)
        else:
            t = np.arange(0, T_total * num_periods, 1/local_sampling_rate)
        
        signal_emit = np.zeros_like(t)
        signal_duration = int(di * local_sampling_rate)
        
        f1 = chosen_dict["f1"]
        f2 = chosen_dict["f2"]
        
        # Générer le signal de base pour une période
        base_signal = np.zeros(int(T_total * local_sampling_rate))
        if modulation == "impulsionnel":
            f_signal = (f1 + f2) / 2
            t_imp = np.arange(0, di, 1/local_sampling_rate)
            t_centered = t_imp - (di / 2)
            sigma = di/6.0
            envelope = np.exp(-t_centered**2/(2*sigma**2))
            impulse_signal = envelope * np.sin(2*np.pi*f_signal*t_imp)
            base_signal[:signal_duration] = impulse_signal

        elif modulation == "FMCW":
            t_seg = np.arange(0, di, 1/local_sampling_rate)
            half = di/2
            f_inst = np.zeros(signal_duration)
            for i in range(signal_duration):
                tau = i/local_sampling_rate
                if tau < half:
                    f_inst[i] = f1 + (f2 - f1)*(tau/half)
                else:
                    f_inst[i] = f2 - (f2 - f1)*((tau - half)/half)
            phase = np.cumsum(2*np.pi*f_inst/local_sampling_rate)
            base_signal[:signal_duration] = np.sin(phase)

        elif modulation == "CW":
            f_signal = (f1 + f2) / 2
            t_seg = np.arange(0, di, 1/local_sampling_rate)
            base_signal[:signal_duration] = np.sin(2*np.pi*f_signal*t_seg)

        elif modulation == "chirp":
            t_seg = np.arange(0, di, 1/local_sampling_rate)
            freq = np.linspace(f1, f2, signal_duration)
            phase = np.cumsum(2*np.pi*freq/local_sampling_rate)
            base_signal[:signal_duration] = np.sin(phase)
        
        if zoom_di:
            # Pour le zoom, on extrait seulement la portion centrale du signal
            zoom_samples = int(zoom_duration * local_sampling_rate)
            mid_point = int(signal_duration/2)
            half_zoom = int(zoom_samples/2)
            return {'signal': base_signal[mid_point-half_zoom:mid_point+half_zoom], 'time': t}
        else:
            # Répéter le signal pour le nombre de périodes demandé
            for i in range(num_periods):
                start_idx = i * len(base_signal)
                end_idx = start_idx + len(base_signal)
                if end_idx <= len(signal_emit):
                    signal_emit[start_idx:end_idx] = base_signal
                    
            return {'signal': signal_emit, 'time': t}

    # Add a title
    st.title("Visualisation des signaux radar")

    # Add controls in sidebar
    st.sidebar.subheader("Paramètres")

    # Create modulation selector in sidebar
    modulation = st.sidebar.selectbox(
        'Type de modulation',
        modulations
    )

    # Add radio buttons for signal display options
    st.sidebar.subheader("Options d'affichage")
    display_option = st.sidebar.radio(
        "Choisir la durée d'affichage:",
        ["DI seulement", "DI + DTOA", "3 × (DI + DTOA)"]
    )

    # Create tabs for each dictionary
    tabs = st.tabs([dict_name for dict_name, _ in dict_list])

    for i, (dict_name, dict_data) in enumerate(dict_list):
        with tabs[i]:
            st.header(f"Signal simulé pour {dict_name}")
            
            # Use first values from dictionary
            di = dict_data["DI"][0]
            dtoa = dict_data["DTOA"][0]
            
            # Generate signal based on display option
            if display_option == "DI seulement":
                result = generate_signal(di, 0, modulation, dict_data)
                title_suffix = "- DI seulement"
            elif display_option == "DI + DTOA":
                result = generate_signal(di, dtoa, modulation, dict_data)
                title_suffix = "- DI + DTOA"
            else:  # 3 periods
                result = generate_signal(di, dtoa, modulation, dict_data, num_periods=3)
                title_suffix = "- 3 périodes"

            # Create interactive plot using plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=result['time'],
                y=result['signal'],
                mode='lines',
                name='Signal'
            ))
            
            fig.update_layout(
                title=f"Signal temporel - {dict_name} {title_suffix}",
                xaxis_title="Temps (s)",
                yaxis_title="Amplitude",
                showlegend=True,
                height=600,
                yaxis=dict(range=[-2, 2])  # Set y-axis range from -2 to 2
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # Display signal parameters
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Fréquence min", f"{dict_data['f1']} Hz")
            with col2:
                st.metric("Fréquence max", f"{dict_data['f2']} Hz")

with tab2:
    st.title("Résultats de classification")
    
    # Load results file
    results_path = "data/result.csv"
    eval_path = "data/eval.csv"
    
    if os.path.exists(results_path) and os.path.exists(eval_path):
        # Load evaluation data
        eval_df = pd.read_csv(eval_path)
        
        # Skip first 3 rows (global metrics and empty line)
        results_df = pd.read_csv(results_path, skiprows=3)
        
        # Get number of signals
        num_signals = len(results_df)
        
        # Create signal selector
        selected_signal = st.selectbox(
            "Choisir un signal",
            range(1, num_signals + 1),
            format_func=lambda x: f"Signal {x}"
        )
        
        # Get selected row from results
        row = results_df[results_df['Signal'] == f'Signal {selected_signal}'].iloc[0]
        
        # Get corresponding row from eval data (index is selected_signal - 1)
        eval_row = eval_df.iloc[selected_signal - 1]
        
        # Create columns for modulation and dictionary results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Classification de la modulation")
            st.write(f"**Modulation réelle:** {row['Modulation Reelle']}")
            st.write(f"**Modulation prédite:** {row['Modulation Predite']}")
            
            # Get modulation probabilities - only keep the 4 main modulations
            main_mods = ['Prob CW', 'Prob FMCW', 'Prob chirp', 'Prob impulsionnel']
            mod_probs = row[main_mods].astype(float)
            
            # Create heatmap for modulation probabilities
            fig_mod = go.Figure(data=go.Heatmap(
                z=[mod_probs.values],
                x=[col.replace('Prob ', '') for col in mod_probs.index],
                colorscale='Reds',
                showscale=False,
                showlegend=False,
                hoverongaps=False
            ))
            fig_mod.update_layout(
                title="Probabilités des modulations", 
                height=250,
                yaxis={'showticklabels': False}
            )
            st.plotly_chart(fig_mod, use_container_width=True)
            
        with col2:
            st.subheader("Classification du dictionnaire")
            st.write(f"**Dictionnaire réel:** {row['Dictionnaire Reel']}")
            st.write(f"**Dictionnaire prédit:** {row['Dictionnaire Predit']}")
            
            # Get dictionary probabilities - only keep the 6 dictionaries
            dict_cols = ['Prob CONDUITE_TIR_1_dic', 'Prob CONDUITE_TIR_2_dic', 'Prob MULTIFCT_dic', 
                         'Prob SUR_SURFACE_dic', 'Prob TA_dic', 'Prob VEILLE_COMBINEE_dic']
            dict_probs = row[dict_cols].astype(float)
            
            # Create heatmap for dictionary probabilities
            fig_dict = go.Figure(data=go.Heatmap(
                z=[dict_probs.values],
                x=[col.replace('Prob ', '') for col in dict_probs.index],
                colorscale='Reds',
                showscale=False,
                showlegend=False,
                hoverongaps=False
            ))
            fig_dict.update_layout(
                title="Probabilités des dictionnaires", 
                height=250,
                yaxis={'showticklabels': False}
            )
            st.plotly_chart(fig_dict, use_container_width=True)
            
        # Display features from eval data
        st.subheader("Caractéristiques du signal")
        features = ['DI choisi', 'DTOA choisi', 'amplitude_max', 'energie_totale', 
                   'freq_dominante', 'bande_passante', 'moyenne', 'variance', 
                   'asymetrie', 'kurtosis']
        
        # Create 2 columns with 5 features each
        col1, col2 = st.columns(2)
        for i, feature in enumerate(features):
            value = eval_row[feature]
            if i < 5:
                col1.metric(feature, f"{value:.3f}")
            else:
                col2.metric(feature, f"{value:.3f}")
    else:
        st.error("Les fichiers de résultats ou d'évaluation n'existent pas. Veuillez d'abord effectuer la classification.")