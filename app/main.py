from fastapi import FastAPI
import pandas as pd
import numpy as np
import os
import tensorflow as tf
import pickle

app = FastAPI()

# --- Variables globales ---
model = None
scaler = None

# --- Chargement Modèle ET Scaler au démarrage ---
@app.on_event("startup")
def load_resources():
    global model, scaler

    # 1. Chargement du modèle
    try:
        model_path = "app/models/models.keras"
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            print(f"✅ Modèle chargé : {model_path}")
        else:
            print(f"❌ Modèle introuvable : {model_path}")
    except Exception as e:
        print(f"❌ Erreur chargement modèle : {e}")

    # 2. Chargement du Scaler
    try:
        scaler_path = "app/models/scaler.pkl"
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
            print(f"✅ Scaler chargé : {scaler_path}")
        else:
            print(f"❌ Scaler introuvable : {scaler_path}")
    except Exception as e:
        print(f"❌ Erreur chargement scaler : {e}")

@app.get("/")
def read_root():
    return {"message": "API Monitor Reactor Ready"}

@app.get("/predict-faults")
def predict_faults():
    global model, scaler

    if model is None:
        return {"error": "Le modèle n'est pas chargé."}
    if scaler is None:
        return {"error": "Le scaler (normalisation) n'est pas chargé."}

    try:
        csv_path = "app/data/data.csv"
        if not os.path.exists(csv_path):
            return {"error": "Fichier data.csv introuvable."}

        # Lecture CSV
        df = pd.read_csv(csv_path)

        # Identification des 52 Features
        feature_cols = [f'xmeas_{i}' for i in range(1, 42)] + \
                       [f'xmv_{i}' for i in range(1, 12)]

        # Récupération des données brutes
        raw_data = df[feature_cols].values

        # --- NORMALISATION ---
        # C'est l'étape clé ajoutée : on transforme les données brutes
        normalized_data = scaler.transform(raw_data)

        samples_idx = df['sample'].values
        sequences = []
        timestamps = []

        # Paramètres sliding window
        start_index = 50
        step = 10
        limit = len(df)

        for i in range(start_index, limit, step):
            # On prend les données NORMALISÉES ici
            window = normalized_data[i-50 : i]
            sequences.append(window)
            timestamps.append(samples_idx[i])

        if not sequences:
            return {"message": "Pas assez de données."}

        # Array final (N, 50, 52)
        X_input = np.array(sequences)

        # Prédiction
        predictions = model.predict(X_input)
        predicted_classes = np.argmax(predictions, axis=1)

        # Formatage
        results = []
        for t, pred_class in zip(timestamps, predicted_classes):
            results.append({
                "sample": int(t),
                "prediction": int(pred_class)
            })

        return results

    except Exception as e:
        return {"error": f"Erreur de prédiction : {str(e)}"}
