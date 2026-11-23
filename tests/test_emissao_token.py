import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timedelta, timezone
import jwt
from app.config import SECRET_KEY, ALGORITHM, carregar_secret_key, ENVIRONMENT, os
from app.security import criar_token_acesso


SECRET_KEY = carregar_secret_key(ENVIRONMENT, os.getenv("SECRET_KEY"))
teste = TestClient(app)

# Assinatura invalida para o teste CT-TK-03
Assinatura_inválida = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwicGVyZmlsIjoidmV0ZXJpbmFyaW8iLCJleHAiOjE3OTU0NzA4OTF9.token_assinado_com_outra_chave")  


# Função para gerar um token já expirado para o teste CT-TK-04
def gerar_token_expirado(email: str = "jáexiste@email.com", perfil: str = "cliente", expirado: int = 61) -> str:
    # Utiliza os mesmos UTC e SECRET_KEY da aplicação
    horario_atual = datetime.now(timezone.utc)
    payload = {
        "sub" : email,
        "perfil" : perfil,
        "exp" : int((horario_atual - timedelta(minutes=expirado)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)



    
Token_expirado = gerar_token_expirado()
Token_valido = criar_token_acesso({"sub": "jáexiste@email.com", "perfil": "cliente"})



@pytest.mark.parametrize('ct_id, metodo, rota, payload, headers, cod_esperado' , 
[ 
    # Cenário Válido
    ("CT-TK-01", "POST", "/auth/login", {"email": "jáexiste@email.com", "senha": "senha123"}, {}, 200),

    # Cenários Inválidos
    ("CT-TK-02", "GET", "/auth/meu-perfil", None, {"Authorization": "Bearer token_mal_formado"}, 401),         # Token com formato inválido
    ("CT-TK-03", "GET", "/auth/meu-perfil", None, {"Authorization": f"Bearer {Assinatura_inválida}"}, 401),    # Token com assinatura modificada
    ("CT-TK-04", "GET", "/auth/meu-perfil", None, {"Authorization": f"Bearer {Token_expirado}"}, 401),         # Acesso à áreas restritas com token expirado
    ("CT-TK-05", "POST", "/prontuarios", None,  {"Authorization": f"Bearer {Token_valido}"}, 403),              # Acesso à áreas restritas sem ter a permissão




])
def test_emissao_token(ct_id, metodo, rota, payload, headers, cod_esperado):
    if payload is not None:
        resposta = teste.request(metodo, rota, json=payload, headers=headers)
    else:
       resposta = teste.request(metodo, rota, headers=headers)
       print("Headers enviados:", resposta.request.headers.get("authorization"))
    assert resposta.status_code == cod_esperado, f"falha no {ct_id}: O codigo esperado era {cod_esperado} e foi entregue {resposta.status_code} \nDetalhe :{resposta.json()}"

    corpo = resposta.json()
    if ct_id == "CT-TK-01":
        assert "access_token" in corpo, f" falha no {ct_id}: 'access_token' ausente em {corpo} "
        assert isinstance(corpo["access_token"], str) and corpo["access_token"].strip() != ""
    else:
        assert "access_token" not in corpo, (
        f"Falha no {ct_id}: não deveria emitir token quando a validação falha")

    
    