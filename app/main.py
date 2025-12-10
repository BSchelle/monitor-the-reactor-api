from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI()

# --- Route Racine (Pour le message de bienvenue) ---
@app.get("/")
def read_root():
    # On récupère le nom du service pour voir où on est (Cloud Run ou Local)
    service = os.environ.get('K_SERVICE', 'Local API')
    return {"message": f"Bonjour depuis {service}"}

# --- Route Health (Pour vérifier que l'API tourne) ---
@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Route Data (Celle qui manque actuellement) ---
@app.get("/get-process-data")
def get_process_data():
    try:
        # Chemin relatif vers le fichier dans le conteneur Docker
        # Basé sur WORKDIR /code et COPY ./app /code/app
        #csv_path = "https://storage.googleapis.com/jubenkai-bucket/data.csv"

        # Stockage sur l'API
        csv_path = "app/data/data.csv"
        # 1. Vérification si le fichier existe en local
        if not os.path.exists(csv_path):
            # En cas d'erreur, on affiche le dossier courant pour aider au debug
            current_dir = os.getcwd()
            return {
                "error": f"Fichier introuvable au chemin : '{csv_path}'.",
                "debug_info": f"Dossier actuel du serveur : {current_dir}"
            }

        # 2. Lecture du CSV
        df = pd.read_csv(csv_path)

        # 3. FILTRAGE : On ne garde que les colonnes utiles
        colonnes_a_garder = ['faultNumber','sample', 'xmeas_7', 'xmeas_9', 'xmeas_10', 'detector','faults_pred','delta']

        # On vérifie que les colonnes existent bien pour éviter un crash silencieux
        missing_cols = [col for col in colonnes_a_garder if col not in df.columns]
        if missing_cols:
            return {"error": f"Colonnes manquantes dans le CSV : {missing_cols}"}

        # Sélection des colonnes
        df_filtered = df[colonnes_a_garder]

        # 4. Conversion en JSON (Liste de dictionnaires)
        return df_filtered.to_dict(orient='records')

    except Exception as e:
        # En cas de gros crash (ex: pandas pas installé, fichier corrompu...)
        return {"error": f"Erreur interne du serveur : {str(e)}"}
