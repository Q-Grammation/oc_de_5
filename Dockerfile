# Utilise une image Python légère
FROM python:3.9-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier des dépendances et les installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le script de migration
COPY main.py .

CMD ["python", "main.py"]