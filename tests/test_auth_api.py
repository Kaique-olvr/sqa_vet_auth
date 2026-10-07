import jwt
import pytest
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

@pytest.mark.parametrize('email, perfil_esperado', [
    ('vet@clinica.com', 'veterinario'),
    ('recepcao@clinica.com', 'recepcionista'),
    ('cliente@clinica.com', 'cliente'),
    ('adm@clinica.com', 'adm')
])
def test_login_sucesso(email, perfil_esperado):
    '''
    Garante que usuários cadastrados consigam se autenticar com sucesso,
    retornando status 200, formato Bearer e payload JWT com e-mail e perfil corretos
    '''
    resposta = fazer_login(email)

    assert resposta.status_code == 200 # Login com dados corretos deve ser aceito
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer" # Confere se segue o padrão OAuth2

    payload = jwt.decode(corpo["access_token"], SECRET_KEY, algorithms=[ALGORITHM]) # Abre o token para conferir o conteúdo
    assert payload["sub"] == email # O dono do token é o usuário que logou
    assert payload["perfil"] == perfil_esperado # O perfil foi gravado corretamente no token


@pytest.mark.parametrize('email, senha', [
    ('vet@clinica.com', 'senha_errada'),        # Usuario existe, senha errada
    ('naoexiste@clinica.com', SENHA_CORRETA),   # Usuario não existe, senha correta
    ('naoexiste@clinica.com', 'senha_errada')   # Usuario não existe, senha errada
])
def test_login_credenciais_invalidas(email, senha):
    '''
    Confirma que tentativas de login com e-mail inexistente ou senha incorreta
    sejam rejeitadas com status 401 Unauthorized e mensagem genérica de erro.
    '''
    resposta = fazer_login(email, senha = senha)

    assert resposta.status_code == 401 # Credenciais erradas devem ser rejeitadas
    assert resposta.json()['detail'] == "E-mail ou senha incorretos"  # Mensagem padrão por segurança


@pytest.mark.parametrize('email_invalido', [
    'email_sem_arroba.com',
    'usuario@',
    '@email.com',
    'email com espacos@email.com',
    'virgula@email,com',
    ''
])
def test_login_email_formato_invalido(email_invalido):
    '''
    Valida se a camada de entrada (Pydantic/EmailStr) bloqueia requisições de login
    com e-mails malformados retornando status 422.
    '''
    resposta = fazer_login(email_invalido)

    assert resposta.status_code == 422 # O pydantic (EmailStr) barra o formato antes de chegar na rota


# TESTES DE AUTENTICAÇÃO (TOKEN)

@pytest.mark.parametrize('email, perfil', [
    ('vet@clinica.com', 'veterinario'),
    ('recepcao@clinica.com', 'recepcionista'),
    ('cliente@clinica.com', 'cliente'),
    ('adm@clinica.com', 'adm')
])
def test_meu_perfil_com_token_valido(email, perfil):
    '''
    Garante que qualquer usuário autenticado com um token JWT válido
    consiga acessar seus próprios dados no endpoint protegido (/auth/meu-perfil).
    '''
    token = token_do_usuario(email)
    resposta = client.get("/auth/meu-perfil", headers=gerar_header(token))

    assert resposta.status_code == 200 # Qualquer usuário logado pode acessar
    assert resposta.json()["seus_dados"] == {"email": email, "perfil": perfil}


def test_meu_perfil_sem_token():
    '''
    Garante que o acesso ao endpoint protegido (/auth/meu-perfil) sem o header
    de autorização seja bloqueado com status 401 Unauthorized.
    '''
    resposta = client.get("/auth/meu-perfil") # Requisição sem o header Authorization

    assert resposta.status_code == 401 # Sem token não entra


@pytest.mark.parametrize('token_invalido', [
    # Com token totalmente errado:
    'token.totalmente.invalido', 
    # Simula um atacante criando um token falso com perfil de veterinário, mas sem saber a SECRET_KEY
    # Assinado com outra chave:
    jwt.encode({'sub': 'hacker@email.com', 'perfil': 'veterinario'}, 'chave_do_atacante_com_mais_de_32_caracteres', algorithm=ALGORITHM), 
    # Token assinado corretamente, mas sem o campo "perfil" no payload:
    jwt.encode({'sub': 'vet@clinica.com'}, SECRET_KEY, algorithm=ALGORITHM),
])
def test_meu_perfil_tokens_invalidos(token_invalido):
    '''
    Garante que tokens malformados, com chave errada ou payload incompleto sejam rejeitados.
    '''
    resposta = client.get("/auth/meu-perfil", headers=gerar_header(token_invalido))

    assert resposta.status_code == 401 # Token malformado deve ser rejeitado
    assert resposta.json()["detail"] == "Credenciais inválidas"


def test_meu_perfil_token_expirado():
    '''
    Garante que um token JWT expirado seja recusado no acesso a rotas
    protegidas, retornando status 401 e instruindo o usuário a fazer login novamente.
    '''
    # Cria um token que expirou 1 minuto atrás
    expiracao_passada = datetime.now(timezone.utc) - timedelta(minutes=1)
    token_expirado = jwt.encode({"sub": "vet@clinica.com", "perfil": "veterinario", "exp": expiracao_passada}, SECRET_KEY, algorithm=ALGORITHM)
    resposta = client.get("/auth/meu-perfil", headers=gerar_header(token_expirado))

    assert resposta.status_code == 401 # Token vencido não entra
    assert resposta.json()["detail"] == "Token expirado. Faça login novamente." # Mensagem específica de expiração


# TESTES DE PERFIL DE ACESSO (RBAC)

def test_prontuario_veterinario_autorizado():
    '''
    Confirma que um usuário com perfil de veterinário possui permissão para criar
    prontuários no endpoint (/prontuarios), retornando status 200 OK.
    '''
    token = token_do_usuario("vet@clinica.com")
    resposta = client.post("/prontuarios", headers=gerar_header(token))

    assert resposta.status_code == 200 # Veterinário tem permissão
    assert resposta.json()["medico_responsavel"] == "vet@clinica.com"


@pytest.mark.parametrize('email_nao_autorizado', [
    'recepcao@clinica.com',
    'cliente@clinica.com',
    'adm@clinica.com'
])
def test_prontuario_perfil_nao_autorizado_negado(email_nao_autorizado):
    """
    Garante que qualquer perfil diferente de veterinário receba status 403 Forbidden ao tentar acessar prontuários.
    """
    token = token_do_usuario(email_nao_autorizado)
    resposta = client.post("/prontuarios", headers=gerar_header(token))

    assert resposta.status_code == 403 # Está logado (token válido), mas o perfil não tem permissão
    assert resposta.json()["detail"] == "Acesso negado. Perfil de usuário não autorizado."


def test_prontuario_sem_token():
    resposta = client.post("/prontuarios")

    assert resposta.status_code == 401 # Sem token, nem chega a checar o perfil
