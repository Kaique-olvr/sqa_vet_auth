from app.schemas.user_schemas import UsuarioCreate, UsuarioResponse
import pytest
from pydantic import ValidationError

def test_usuario_create_sucesso():
    # Variaveis validas para o teste:
    email = "Testando@email.com"
    senha = "senhaforte1234"

    # Intanciando um objeto:
    usuario = UsuarioCreate(email = email, senha = senha)

    # Checa se a condição é True ou False para a simulação do teste
    assert usuario.email == email
    assert usuario.senha == senha


def test_usuario_create_email_incorreto():
    # A ideia desse metodo é testar se a validação acontece ou não
    # Para esse teste PASSAR o pydantic precisa lançar esse ValidationError
    # Se a função não der ValidarionError o teste FALHA 
    with pytest.raises(ValidationError): # Essa linha está monitorando o codigo de baixo
        UsuarioCreate(email = "email_sem_arroba.com", senha = "senha_certinha_123")


def test_usuario_create_senha_incorreta():
    # Mesma ideia da função de cima, mas agora o teste é na senha
    senha_curta = "1234"
    senha_longa = "a" * 73

    with pytest.raises(ValidationError):
        UsuarioCreate(email = "teste@email.com", senha = senha_curta)

    with pytest.raises(ValidationError):
            UsuarioCreate(email = "teste@email.com", senha = senha_longa)


def test_usuario_response():
    # Essa função testa se a classe UsuarioResponse está funcionando como deveria
    email = "exemplo@email.com"

    usuario = UsuarioResponse(id = 1, email = email)

    assert usuario.id == 1
    assert usuario.email == email