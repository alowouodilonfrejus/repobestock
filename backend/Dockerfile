# Base locale reutilisable : contient deja Python 3.12 + FastAPI + SQLAlchemy
# async + asyncpg + PyJWT + bcrypt + pydantic-settings (aucun acces internet requis).
FROM scolarship-2026-main-api:latest

WORKDIR /app

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
