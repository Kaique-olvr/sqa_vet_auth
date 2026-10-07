import jwt

''' Testes das funções em security.py
    Aqui tem funções auxiliares que chamam as principais, que estão em app.security, e fazem as verificações com assert
'''

from app.security import gerar_hash_senha, verificar_senha, criar_token_acesso, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
def test_gerar_hash_senha_sucesso():
    senha = "senhadeteste" # Senha qualquer para ser transformada em hash
    hash_gerado = gerar_hash_senha(senha)

    assert hash_gerado != senha # Confere se a senha original é diferente do hash

    hash_qualquer = gerar_hash_senha(senha) # Cria um novo hash qualquer, com a mesma senha, para comparar
    assert hash_gerado != hash_qualquer # Confere se os hashes são diferentes. Cada um tem um Salt diferente


def test_verificar_senha_correta():
    senha = "senhasucesso" # Senha qualquer para ser transformada em hash 
    hash_gerado = gerar_hash_senha(senha) # Gera o hash da senha

    # Deve retornar True
    assert verificar_senha(senha, hash_gerado) is True # Verifica se senha e hash_gerado tem hashes iguais

def test_verificar_senha_incorreta():
    senha = "senhaerro"
    hash_gerado = gerar_hash_senha(senha)

    # Deve retornar falso
    assert verificar_senha("senha_diferente_da_cadastrada", hash_gerado) is False # Verifica se senhas diferentes são rejeitadas

def test_criar_token_acesso():
    # Simula os dados que iremos colocar no token na hora do login
    dados_usuario = {
        "sub": "usuario@teste.com",
        "perfil": "veterinario"
    }

    token = criar_token_acesso(dados_usuario) # Cria o token com os dados do usuario

    assert isinstance(token, str) # Verifica se o token é uma string

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # Decodifica o token para verificar se os dados estão corretos

    assert payload['sub'] == "usuario@teste.com" # Verifica se o email do payload é o mesmo do email do usuario
    assert payload['perfil'] == "veterinario" # Verifica se o perfil do payload é o mesmo do perfil do usuario
    assert "exp" in payload # Verifica se o payload tem a chave de expiração do token