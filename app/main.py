from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI()


@app.get("/")
def read_root():
    # On récupère le nom du service pour voir où on est (optionnel)
    service = os.environ.get('K_SERVICE', 'Local API')
    return {"message": f"Bonjour depuis {service}"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/get-process-data")
def get_process_data():
    try:
        # Si votre structure est app/data/data.csv et WORKDIR est /code
        csv_path = "app/data/data.csv"

        # Vérification si le fichier existe
        if not os.path.exists(csv_path):
            return {"error": f"Fichier non trouvé au chemin : {csv_path}"}

        # Lecture du CSV
        df = pd.read_csv(csv_path)

        # FILTRAGE : On ne garde que les colonnes utiles
        colonnes_a_garder = ['sample', 'xmeas_7', 'xmeas_9', 'xmeas_10']

        # On sélectionne uniquement ces colonnes
        # Si une colonne manque, cela lèvera une erreur (ce qui est mieux que d'envoyer de mauvaises données)
        df_filtered = df[colonnes_a_garder]

        # 3. Conversion en JSON
        return df_filtered.to_dict(orient='records')

        # On convertit le DataFrame en dictionnaire (JSON compatible)
        # orient='records' crée une liste d'objets : [{"Pression": 10, ...}, ...]
        data_json = df.to_dict(orient='records')

        return data_json

    except Exception as e:
        return {"error": str(e)}
