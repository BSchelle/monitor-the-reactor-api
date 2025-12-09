from fastapi import FastAPI
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
