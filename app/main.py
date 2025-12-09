from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI()

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
        # Chemin relatif basé sur WORKDIR /code dans le Dockerfile
        csv_path = "app/data/data.csv"

        # Vérification si le fichier existe
        if not os.path.exists(csv_path):
            # Astuce de debug : On affiche le dossier actuel pour comprendre l'erreur
            cwd = os.getcwd()
            return {"error": f"Fichier introuvable. Chemin cherché : {csv_path}. Dossier actuel : {cwd}"}

        # Lecture du CSV
        df = pd.read_csv(csv_path)

        # FILTRAGE : On ne garde que les colonnes utiles
        colonnes_a_garder = ['sample', 'xmeas_7', 'xmeas_9', 'xmeas_10']

        # Sélection des colonnes (renvoie une erreur si une colonne manque)
        df_filtered = df[colonnes_a_garder]

        # Conversion et envoi de la réponse
        return df_filtered.to_dict(orient='records')

    except Exception as e:
        return {"error": str(e)}
