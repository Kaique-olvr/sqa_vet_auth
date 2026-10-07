import pytest

''' Testes das regras de configuração em config.py
    Garante que a aplicação nunca rode fora do ambiente de desenvolvimento usando a chave secreta padrão.
'''

from app.config import carregar_secret_key, CHAVE_PADRAO_DESENVOLVIMENTO

def test_secret_key_definida_e_usada():
    # Se a chave existe no .env, ela deve ser usada em qualquer ambiente
    assert carregar_secret_key("production", "minha_chave_forte") == "minha_chave_forte"
    assert carregar_secret_key("development", "minha_chave_forte") == "minha_chave_forte"

def test_secret_key_padrao_em_desenvolvimento():
    # Rodando local sem chave definida, usa a chave padrão para facilitar o desenvolvimento
    assert carregar_secret_key("development", None) == CHAVE_PADRAO_DESENVOLVIMENTO

def test_secret_key_ausente_em_producao():
    # Fora do desenvolvimento, sem chave definida, a aplicação deve travar com erro
    with pytest.raises(RuntimeError):
        carregar_secret_key("production", None)

    with pytest.raises(RuntimeError):
        carregar_secret_key("production", "") # Chave vazia também conta como não definida
