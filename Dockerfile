# 1. On passe en Python 3.10 pour matcher votre environnement local
FROM python:3.10-slim

WORKDIR /code

# 2. Copie et installation des dépendances (N'oubliez pas d'avoir ajouté pandas dans le txt !)
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 3. Copie du code source ET du dossier data
COPY ./app /code/app

# 4. Commande de lancement
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
