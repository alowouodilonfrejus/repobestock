# Railway / Prod : image publique (remplace scolarship-2026-main-api locale)
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dépendances système pour asyncpg/bcrypt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./app ./app

# Execution sans privileges : l'API n'a besoin d'ecrire nulle part
# (le magasin rate-limit vit dans /tmp, accessible en lecture-ecriture)
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin bestock
USER bestock

EXPOSE 8000

# Railway injecte $PORT — fallback 8000 en local
CMD ["sh", "-c", "python -m app.internal_data && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
