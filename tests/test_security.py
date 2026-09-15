''' Testes das funções em security.py
    Aqui tem funções auxiliares que chamam as principais, que estão em app.security, e fazem as verificações com assert
'''

from app.security import gerar_hash_senha, verificar_senha

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