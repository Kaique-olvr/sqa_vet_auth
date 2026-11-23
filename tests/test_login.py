import pytest


from fastapi.testclient import TestClient
from app.main import app




teste = TestClient(app)


# Login de Usuários (CT-LG)

@pytest.mark.parametrize('ct_id, email, senha, cod_esperado',     
                         
    
[ 
    # Cenário Válido
    ('CT-LG-01', 'jáexiste@email.com', 'senha123', 200),            # Usuário e senha corretos

    # Cenários inválidos
    ('CT-LG-02', 'nãoexiste@email.com', 'senha123', 401),           # Usuário inexistente
    ('CT-LG-03', '', 'senha123', 401),                              # Email em branco
    ('CT-LG-04', 'jáexiste@email.com', 'senhaerrada123', 401),      # Senha incorreta
    ('CT-LG-05', 'jáexiste@email.com', '', 401),                    # Senha em branco
    

])
def test_login_usuarios(ct_id,email,senha,cod_esperado):
    payload = {
        "email" : email,
        "senha" : senha
    }
    resposta = teste.post("/auth/login", json=payload)
    assert resposta.status_code == cod_esperado, f"falha no {ct_id}: O codigo esperado era {cod_esperado} e foi entregue {resposta.status_code}"


