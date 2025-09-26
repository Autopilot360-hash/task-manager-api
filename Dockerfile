FROM python:3.10-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système pour PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Script de démarrage qui créera les tables
RUN echo '#!/bin/bash\n\
echo "🚀 Starting FastAPI Task Manager..."\n\
echo "📊 Creating database tables..."\n\
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine); print(\"✅ Tables created successfully!\")"\n\
echo "�� Starting server on port $PORT..."\n\
uvicorn main:app --host 0.0.0.0 --port $PORT' > start.sh

RUN chmod +x start.sh

# Railway utilise la variable $PORT dynamiquement
EXPOSE $PORT

# Commande de démarrage
CMD ["./start.sh"]
