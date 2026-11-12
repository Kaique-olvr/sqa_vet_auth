from fastapi import APIRouter, Depends, HTTPException, status
from app.security import criar_token_acesso, verificar_senha, gerar_hash_senha
from app.dependencies import get_usuario_atual
from app.schemas.user_schemas import LoginRequest, TokenResponse, UsuarioCreate
from app.repositories.user_repository import _USUARIOS_POR_EMAIL
from app.repositories.user_repository import buscar_usuario_por_email

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# ROTA 1: Cadastro (Cria o usuário)
@router.post("/cadastro",status_code= status.HTTP_201_CREATED)
def cadastrar_usuario(usuario: UsuarioCreate):
    # Verifica se o email ja existe no banco de dados
    if usuario.email in _USUARIOS_POR_EMAIL:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
        detail= "Este email já é utilizado!"
    )
      
    # Faz o hash da senha digitada
    senha_hash = gerar_hash_senha(usuario.senha)

    # Adiciona o novo usuário no banco de dados
    _USUARIOS_POR_EMAIL[usuario.email] = {
        "email": usuario.email,
        "senha_hash": senha_hash,
        "perfil": usuario.perfil_acesso

    }
    return {
        "mensagem": "Cadastro concluido!",
        "usuario" : {"email": usuario.email, "perfil": usuario.perfil_acesso}
    }


# ROTA 2: LOGIN (Gera o Token)
@router.post("/login", response_model=TokenResponse)
def login(credenciais: LoginRequest):
    # Mensagem ÚNICA para email ou senha errados.
    # Se a API dissesse "E-mail incorreto" separado de "Senha incorreta", um atacante conseguiria
    # descobrir quais emails estão cadastrados (enumeração de usuários).
    login_invalido_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "E-mail ou senha incorretos",
        headers = {"WWW-Authenticate": "Bearer"}
    )

    usuario_db = buscar_usuario_por_email(credenciais.email)

    # Verifica se o usuário existe
    if not usuario_db:
        raise login_invalido_exception

    # Verifica se a senha bate com o hash salvo (validação real do bcrypt)
    if not verificar_senha(credenciais.senha, usuario_db["senha_hash"]):
        raise login_invalido_exception

    # Se tudo deu certo, cria o payload e gera o token!
    dados_token = {
        "sub": usuario_db["email"], # "sub" (subject) é o campo padrão do JWT para identificar o dono do token
        "perfil": usuario_db["perfil"] # Perfil de acesso usado depois no controle de permissões (RBAC)
    }

    token = criar_token_acesso(dados_token)

    # Retorna no padrão do OAuth2 (access_token e token_type)
    return TokenResponse(access_token=token)

# ROTA 2: PERFIL ABERTO (Qualquer um logado)
@router.get("/meu-perfil")
def ver_perfil(usuario_logado: dict = Depends(get_usuario_atual)):
    # Aqui chega se o get_usuario_atual passou sem dar erro no token
    return {
        "mensagem": "Acesso Liberado!",
        "seus_dados": usuario_logado
    }
