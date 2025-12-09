from fastapi import FastAPI
import pandas as pd
import numpy as np
import os
import tensorflow as tf

app = FastAPI()

# --- Variable globale pour le modèle ---
model = None

# --- Chargement du modèle au démarrage ---
@app.on_event("startup")
def load_model():
    global model
    try:
        # Chemin selon votre structure Docker
        model_path = "app/models/models.keras"
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            print(f"Modèle chargé avec succès depuis : {model_path}")
        else:
            print(f"ATTENTION : Modèle introuvable à {model_path}")
    except Exception as e:
        print(f"Erreur lors du chargement du modèle : {e}")

@app.get("/")
def read_root():
    service = os.environ.get('K_SERVICE', 'Local API')
    return {"message": f"Bonjour depuis {service}"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/get-process-data")
def get_process_data():
    try:
        csv_path = "app/data/data.csv"
        if not os.path.exists(csv_path):
            return {"error": "Fichier data.csv introuvable."}

        df = pd.read_csv(csv_path)
        # Sélection des colonnes pour les graphes temps réel
        cols = ['sample', 'xmeas_7', 'xmeas_9', 'xmeas_10']
        return df[cols].to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}

# --- NOUVELLE ROUTE : Prédiction IA ---
@app.get("/predict-faults")
def predict_faults():
    global model
    if model is None:
        return {"error": "Le modèle n'est pas chargé."}

    try:
        csv_path = "app/data/data.csv"
        if not os.path.exists(csv_path):
            return {"error": "Fichier data.csv introuvable."}

        # 1. Lecture
        df = pd.read_csv(csv_path)

        # 2. Identification des 52 Features
        # xmeas_1 à xmeas_41 et xmv_1 à xmv_11
        feature_cols = [f'xmeas_{i}' for i in range(1, 42)] + \
                       [f'xmv_{i}' for i in range(1, 12)]

        # Vérification rapide
        if not all(col in df.columns for col in feature_cols):
            return {"error": "Colonnes de features manquantes dans le CSV"}

        data_matrix = df[feature_cols].values # Convertir en numpy array
        samples_idx = df['sample'].values

        # 3. Préparation des séquences (Sliding Window)
        # On a besoin de 50 pas de temps passés. On commence donc à l'index 50.
        # On avance de 10 en 10 (step=10).

        sequences = []
        timestamps = [] # Pour l'axe X du graphe

        start_index = 50
        step = 10
        limit = len(df)

        for i in range(start_index, limit, step):
            # Récupérer la fenêtre [i-50 : i] -> Forme (50, 52)
            window = data_matrix[i-50 : i]
            sequences.append(window)
            timestamps.append(samples_idx[i])

        if not sequences:
            return {"message": "Pas assez de données pour prédire (min 50 samples)."}

        # Conversion en np.array de forme (N_batch, 50, 52)
        X_input = np.array(sequences)

        # 4. Prédiction
        # Le modèle sort (N, 21). On prend l'argmax pour avoir la classe (0-20)
        predictions = model.predict(X_input)
        predicted_classes = np.argmax(predictions, axis=1)

        # 5. Formater la réponse pour Streamlit
        results = []
        for t, pred_class in zip(timestamps, predicted_classes):
            results.append({
                "sample": int(t),
                "prediction": int(pred_class)
            })

        return results

    except Exception as e:
        return {"error": f"Erreur de prédiction : {str(e)}"}
