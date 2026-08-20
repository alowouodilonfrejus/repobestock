"""Point d'entree WSGI pour PythonAnywhere.

PythonAnywhere sert l'application via WSGI (synchrone). a2wsgi adapte
l'app ASGI FastAPI vers WSGI.

IMPORTANT : definir USE_NULLPOOL=true dans le .env (voir
.env.pythonanywhere.example) car chaque requete WSGI cree sa propre
boucle d'evenements : un pool de connexions partage serait reutilise
entre les boucles et provoquerait des erreurs "event loop is closed".
"""

from a2wsgi import WSGIMiddleware

from app.main import app

application = WSGIMiddleware(app)