import jwt
from datetime import datetime, timezone, timedelta

''' Testes das funções em security.py
    Aqui tem funções auxiliares que chamam as principais, que estão em app.security, e fazem as verificações com assert
'''

from app.security import (
    gerar_hash_senha, 
    verificar_senha, 
    criar_token_acesso, 
    SECRET_KEY, ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES)


def test_gerar_hash_senha_sucesso():
    '''
    Confirma que o hash está sendo gerado com sucesso e salts diferentes (em casos de senhas iguais)
    '''

    senha = "senhadeteste" # Senha qualquer para ser transformada em hash
    hash_gerado = gerar_hash_senha(senha)

    assert hash_gerado != senha # Confere se a senha original é diferente do hash

    hash_qualquer = gerar_hash_senha(senha) # Cria um novo hash qualquer, com a mesma senha, para comparar
    assert hash_gerado != hash_qualquer # Confere se os hashes são diferentes. Cada um tem um Salt diferente


def test_verificar_senha_correta():
    '''
    verifica se a senha digitada é igual ao hash cadastrado, retornando True
    '''
    senha = "senhasucesso" # Senha qualquer para ser transformada em hash 
    hash_gerado = gerar_hash_senha(senha) # Gera o hash da senha

    # Deve retornar True
    assert verificar_senha(senha, hash_gerado) is True # Verifica se senha e hash_gerado tem hashes iguais


def test_verificar_senha_incorreta():
    '''
    verifica se a senha digitada é diferente do hash cadastrado, retornando False
    '''
    senha = "senhaerro"
    hash_gerado = gerar_hash_senha(senha)

    # Deve retornar falso
    assert verificar_senha("senha_diferente_da_cadastrada", hash_gerado) is False # Verifica se senhas diferentes são rejeitadas


def test_criar_token_acesso():
    '''
    Valida a criação do token JWT, garantindo que o tipo de retorno seja uma string,
    que os dados do usuário (sub e perfil) estejam no payload 
    e que a data de expiração (exp) seja calculada corretamente com base no tempo configurado.
    '''
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

    # validação do tempo de expiração
    agora = datetime.now(timezone.utc) # timezone.utc padroniza os horarios e datas
    tempo_expiracao = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
    duracao_esperada = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # timedelta é a duração de tempo de um intervalo 

    # Pega abs((a hora que vai expirar - a hora agora) - o tempo que deveria durar)
    # Exemplo: | (12:30 - 12:00) - 00:30) |
    # Esse resultado tem que ser menor que 5 segundos, que é uma tolerencia para o processador conseguir rodar tranquilo
    assert abs((tempo_expiracao - agora) - duracao_esperada) < timedelta(seconds=5)