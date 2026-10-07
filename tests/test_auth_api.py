import jwt
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

''' Testes de integração da API (rotas HTTP)
    O TestClient simula requisições reais para a aplicação, sem precisar subir o servidor (uvicorn).
    Aqui testamos o fluxo completo: login -> token -> acesso às rotas protegidas -> controle por perfil.
'''

from app.main import app
from app.config import SECRET_KEY, ALGORITHM

client = TestClient(app) # Cliente que faz as requisições na nossa API

SENHA_CORRETA = "senha123" # Senha dos usuários do banco de dados falso


# FUNÇÕES AUXILIARES

def fazer_login(email: str, senha: str = SENHA_CORRETA):
    # Faz a requisição de login e retorna a resposta inteira (status + corpo)
    return client.post("/auth/login", json={"email": email, "senha": senha})

def gerar_header(token: str) -> dict:
    # Monta o header no formato que a API espera: "Authorization: Bearer <token>"
    return {"Authorization": f"Bearer {token}"}

def token_do_usuario(email: str) -> str:
    # Faz o login e já devolve somente o token
    return fazer_login(email).json()["access_token"]


# TESTE DA ROTA INICIAL

def test_home():
    resposta = client.get("/")

    assert resposta.status_code == 200 # Rota pública, não precisa de token


# TESTES DE LOGIN

def test_login_sucesso():
    resposta = fazer_login("vet@clinica.com")

    assert resposta.status_code == 200 # Login com dados corretos deve ser aceito
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer" # Confere se segue o padrão OAuth2

    payload = jwt.decode(corpo["access_token"], SECRET_KEY, algorithms=[ALGORITHM]) # Abre o token para conferir o conteúdo
    assert payload["sub"] == "vet@clinica.com" # O dono do token é o usuário que logou
    assert payload["perfil"] == "veterinario" # O perfil foi gravado corretamente no token

def test_login_senha_incorreta():
    resposta = fazer_login("vet@clinica.com", senha="senha_errada")

    assert resposta.status_code == 401 # Senha errada deve ser rejeitada
    assert resposta.json()["detail"] == "E-mail ou senha incorretos"

def test_login_email_inexistente():
    resposta = fazer_login("naoexiste@clinica.com")

    assert resposta.status_code == 401 # Email não cadastrado deve ser rejeitado
    assert resposta.json()["detail"] == "E-mail ou senha incorretos" # Mesma mensagem da senha errada (não revela se o email existe)

def test_login_email_formato_invalido():
    resposta = fazer_login("email_sem_arroba.com")

    assert resposta.status_code == 422 # O pydantic (EmailStr) barra o formato antes de chegar na rota


# TESTES DE AUTENTICAÇÃO (TOKEN)

def test_meu_perfil_com_token_valido():
    token = token_do_usuario("recepcao@clinica.com")
    resposta = client.get("/auth/meu-perfil", headers=gerar_header(token))

    assert resposta.status_code == 200 # Qualquer usuário logado pode acessar
    assert resposta.json()["seus_dados"] == {"email": "recepcao@clinica.com", "perfil": "recepcionista"}

def test_meu_perfil_sem_token():
    resposta = client.get("/auth/meu-perfil") # Requisição sem o header Authorization

    assert resposta.status_code == 401 # Sem token não entra

def test_meu_perfil_token_invalido():
    resposta = client.get("/auth/meu-perfil", headers=gerar_header("token.totalmente.invalido"))

    assert resposta.status_code == 401 # Token malformado deve ser rejeitado
    assert resposta.json()["detail"] == "Credenciais inválidas"

def test_meu_perfil_token_assinado_com_outra_chave():
    # Simula um atacante criando um token falso com perfil de veterinário, mas sem saber a SECRET_KEY
    token_falso = jwt.encode({"sub": "hacker@email.com", "perfil": "veterinario"}, "chave_do_atacante_com_mais_de_32_caracteres", algorithm=ALGORITHM)
    resposta = client.get("/auth/meu-perfil", headers=gerar_header(token_falso))

    assert resposta.status_code == 401 # A assinatura não bate, então o token é rejeitado

def test_meu_perfil_token_expirado():
    # Cria um token que expirou 1 minuto atrás
    expiracao_passada = datetime.now(timezone.utc) - timedelta(minutes=1)
    token_expirado = jwt.encode({"sub": "vet@clinica.com", "perfil": "veterinario", "exp": expiracao_passada}, SECRET_KEY, algorithm=ALGORITHM)
    resposta = client.get("/auth/meu-perfil", headers=gerar_header(token_expirado))

    assert resposta.status_code == 401 # Token vencido não entra
    assert resposta.json()["detail"] == "Token expirado. Faça login novamente." # Mensagem específica de expiração

def test_meu_perfil_token_sem_perfil():
    # Token assinado corretamente, mas sem o campo "perfil" no payload
    token_incompleto = jwt.encode({"sub": "vet@clinica.com"}, SECRET_KEY, algorithm=ALGORITHM)
    resposta = client.get("/auth/meu-perfil", headers=gerar_header(token_incompleto))

    assert resposta.status_code == 401 # Sem perfil não dá para controlar o acesso, então é rejeitado


# TESTES DE PERFIL DE ACESSO (RBAC)

def test_prontuario_veterinario_autorizado():
    token = token_do_usuario("vet@clinica.com")
    resposta = client.post("/prontuarios", headers=gerar_header(token))

    assert resposta.status_code == 200 # Veterinário tem permissão
    assert resposta.json()["medico_responsavel"] == "vet@clinica.com"

def test_prontuario_recepcionista_negado():
    token = token_do_usuario("recepcao@clinica.com")
    resposta = client.post("/prontuarios", headers=gerar_header(token))

    assert resposta.status_code == 403 # Está logado (token válido), mas o perfil não tem permissão
    assert resposta.json()["detail"] == "Acesso negado. Perfil de usuário não autorizado."

def test_prontuario_sem_token():
    resposta = client.post("/prontuarios")

    assert resposta.status_code == 401 # Sem token, nem chega a checar o perfil
