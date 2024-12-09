import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from typing import Tuple, List
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import csv
import joblib
import os

class RadarClassifier:
    """
    Classe pour la classification de signaux radar militaires.
    Utilise deux classifieurs Random Forest pour prédire:
    - Le type de modulation du signal
    - Le dictionnaire (type de radar) dont provient le signal
    """
    def __init__(self):
        """
        Initialise les classifieurs pour les deux labels (modulation et dictionnaire).
        """
        # Initialisation du scaler pour normaliser les features
        self.scaler = StandardScaler()
        
        # Initialisation des deux classifieurs Random Forest
        self.classifier_modulation = RandomForestClassifier(n_estimators=100, random_state=42)
        self.classifier_dict = RandomForestClassifier(n_estimators=100, random_state=42)
        
        
    def train(self, dataset_path: str) -> Tuple[dict, dict]:
        """
        Entraîne les modèles sur le dataset.
        
        Args:
            dataset_path: Chemin vers le fichier CSV du dataset contenant les features extraites
            
        Returns:
            Tuple contenant:
            - metrics_mod: Métriques d'évaluation pour le classifieur de modulation
            - metrics_dict: Métriques d'évaluation pour le classifieur de dictionnaire
        """
        # Chargement des données depuis le CSV
        df = pd.read_csv(dataset_path)
        
        # Définition des features à utiliser pour la classification
        features = ['DI choisi', 'DTOA choisi','amplitude_max', 'energie_totale', 'freq_dominante', 'bande_passante',
                   'moyenne', 'variance', 'asymetrie', 'kurtosis']
        X = df[features]
        y_mod = df['modulation']      # Au lieu de 'chosen_modulation'
        y_dict = df['dict_name']      # Celui-ci est correct
        
        # Split des données en ensembles d'entraînement et de test (80/20)
        X_train, X_test, y_mod_train, y_mod_test, y_dict_train, y_dict_test = train_test_split(
            X, y_mod, y_dict, test_size=0.2, random_state=42
        )
        
        # Normalisation des features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entraînement et évaluation du classifieur de modulation
        self.classifier_modulation.fit(X_train_scaled, y_mod_train)
        y_mod_pred = self.classifier_modulation.predict(X_test_scaled)
        metrics_mod = classification_report(y_mod_test, y_mod_pred, output_dict=True)
        
        # Entraînement et évaluation du classifieur de dictionnaire
        self.classifier_dict.fit(X_train_scaled, y_dict_train)
        y_dict_pred = self.classifier_dict.predict(X_test_scaled)
        metrics_dict = classification_report(y_dict_test, y_dict_pred, output_dict=True)
        
        # Save the trained model
        model_path = 'radar_classifier.joblib'
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(model_path) if os.path.dirname(model_path) else '.', exist_ok=True)
        joblib.dump(self, model_path)
        
        return metrics_mod, metrics_dict

def load_classifier():
    """Load the trained classifier from disk"""
    model_path = 'radar_classifier.joblib'
    if not os.path.exists(model_path):
        # Train a new classifier if model file doesn't exist
        classifier = RadarClassifier()
        classifier.train("classification/data/output_features.csv")
    return joblib.load(model_path)

def evaluate_big():
    # Création et entraînement du classifieur
    classifier = RadarClassifier()
    metrics_mod, metrics_dict = classifier.train("classification/data/output_features.csv")
    
    # Évaluation sur un nouveau jeu de données
    eval_df = pd.read_csv("classification/data/eval.csv")
    
    # Extraction des features dans le même ordre que l'entraînement
    features = ['DI choisi', 'DTOA choisi','amplitude_max', 'energie_totale', 'freq_dominante', 'bande_passante',
               'moyenne', 'variance', 'asymetrie', 'kurtosis']
    X_eval = eval_df[features]
    y_mod_eval = eval_df['modulation']
    y_dict_eval = eval_df['dict_name']
    
    # Normalisation avec le même scaler que l'entraînement
    X_eval_scaled = classifier.scaler.transform(X_eval)
    
    # Prédiction des labels et des probabilités associées
    pred_mod = classifier.classifier_modulation.predict(X_eval_scaled)
    pred_dict = classifier.classifier_dict.predict(X_eval_scaled)
    
    proba_mod = classifier.classifier_modulation.predict_proba(X_eval_scaled)
    proba_dict = classifier.classifier_dict.predict_proba(X_eval_scaled)
    
    # Calcul de la précision sur l'ensemble d'évaluation
    mod_accuracy = (pred_mod == y_mod_eval).mean()
    dict_accuracy = (pred_dict == y_dict_eval).mean()
    
    # Création du fichier CSV avec les résultats
    with open("classification/data/result.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # En-tête avec les précisions globales
        writer.writerow(["Precision Modulation", "Precision Dictionnaire"])
        writer.writerow([f"{mod_accuracy:.2%}", f"{dict_accuracy:.2%}"])
        
        writer.writerow([]) # Ligne vide pour séparer
        
        # En-tête pour les prédictions détaillées
        writer.writerow(["Signal", 
                        "Modulation Reelle", "Modulation Predite",
                        *[f"Prob {mod}" for mod in classifier.classifier_modulation.classes_],
                        "Dictionnaire Reel", "Dictionnaire Predit",
                        *[f"Prob {dict_name}" for dict_name in classifier.classifier_dict.classes_]])
        
        # Écriture des résultats pour chaque signal
        for i in range(len(pred_mod)):
            row = [
                f"Signal {i+1}",
                y_mod_eval.iloc[i],
                pred_mod[i],
                *[f"{prob:.3f}" for prob in proba_mod[i]],
                y_dict_eval.iloc[i],
                pred_dict[i],
                *[f"{prob:.3f}" for prob in proba_dict[i]]
            ]
            writer.writerow(row)


if __name__ == "__main__":
    evaluate_big()
