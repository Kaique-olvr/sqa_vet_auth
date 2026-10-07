from fastapi import FastAPI
from app.routers import auth_router, prontuario_router  # Importa as rotas

app = FastAPI(title="SQA Vet Auth API")

# Conecta as rotas na aplicação principal
app.include_router(auth_router.router) # Rotas de autenticação (/auth/login, /auth/meu-perfil)
app.include_router(prontuario_router.router) # Rotas de prontuários (/prontuarios), restritas por perfil

@app.get("/")
def home():
    return {"status": "API da Clínica Veterinária rodando!"}
