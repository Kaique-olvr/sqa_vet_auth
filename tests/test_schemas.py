from app.schemas.user_schemas import PerfilAcesso, UsuarioCreate, UsuarioResponse
import pytest
from pydantic import ValidationError


@pytest.mark.parametrize('email, perfil', [
    ('Testando@email.com', PerfilAcesso.CLIENTE),
    ('vet@clinica.com', PerfilAcesso.VETERINARIO),
    ('recepcao@clinica.com', PerfilAcesso.RECEPCIONISTA)
])
def test_usuario_create_sucesso(email, perfil):
    '''
    Garante que o schema de criação de usuário (UsuarioCreate) aceita e-mails em formato
    válido e atribui o perfil corretamente ao instanciar o modelo.
    '''
    senha = "senhaforte1234"
    # Intanciando um objeto:
    usuario = UsuarioCreate(email=email, senha=senha, perfil_acesso=perfil)
    # Checa se a condição é True ou False para a simulação do teste
    assert usuario.email == email
    assert usuario.senha == senha
    assert usuario.perfil_acesso == perfil # Verifica se salvou o perfil de acesso correto


@pytest.mark.parametrize('email_incorreto', [
    'email_sem_arroba.com',
    'usuario@',
    '@sla.com',
    'email com espacos@orkut.com',
    'virgula@email,com',
    ''
])
def test_usuario_create_email_incorreto(email_incorreto):
    '''
    Confirma que o schema UsuarioCreate dispara uma exceção de validação (ValidationError)
    ao receber e-mails malformados ou em formato inválido.
    '''
    # A ideia desse metodo é testar se a validação acontece ou não
    # Para esse teste PASSAR o pydantic precisa lançar esse ValidationError
    # Se a função não der ValidarionError o teste FALHA 
    with pytest.raises(ValidationError): # Essa linha está monitorando o codigo de baixo
        # O perfil_acesso é passado certinho para garantir que o erro venha SOMENTE do email
        UsuarioCreate(email = email_incorreto, senha = "senha_certinha_123", perfil_acesso=PerfilAcesso.CLIENTE)


@pytest.mark.parametrize('senha_invalida', [
     '1234',        # Senha curta (< 8: min definido)
     'A' * 73,      # Senha longa (> limite do bcrypt)
])
def test_usuario_create_senha_incorreta(senha_invalida):
    '''
    Valida se a regra de tamanho mínimo de senha do schema UsuarioCreate
    rejeita senhas inseguras ou fora do padrão esperado.
    '''
    # Mesma ideia da função de cima, mas agora o teste é na senha
    # Garante que senhas fora dos limites de tamanho disparam ValidationError.

    with pytest.raises(ValidationError):
        UsuarioCreate(email = "teste@email.com", senha = senha_invalida, perfil_acesso=PerfilAcesso.CLIENTE)


@pytest.mark.parametrize('user_id, email, perfil', [
    (1, 'exemplo@email.com', PerfilAcesso.VETERINARIO),
    (2, 'cliente@email.com', PerfilAcesso.CLIENTE),
    (3, 'recep@email.com', PerfilAcesso.RECEPCIONISTA)
])
def test_usuario_response(user_id, email, perfil):
    '''
    Garante que o schema de resposta (UsuarioResponse) serializa corretamente os dados
    públicos do usuário (id, email e perfil), omitindo campos sensíveis como a senha.
    '''

    usuario = UsuarioResponse(id = user_id, email = email, perfil_acesso = perfil)

    assert usuario.id == user_id
    assert usuario.email == email
    assert usuario.perfil_acesso == perfil