# 1. Image de base (Python léger)
FROM python:3.9-slim

# 2. Dossier de travail dans le conteneur
WORKDIR /code

# 3. Installation des dépendances (en premier pour profiter du cache Docker)
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 4. Copie du code de l'application
COPY ./app /code/app

# 5. Commande de lancement
# Cloud Run injecte la variable PORT.
# On lance uvicorn en pointant vers "app.main:app" (dossier app -> fichier main -> objet app)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
