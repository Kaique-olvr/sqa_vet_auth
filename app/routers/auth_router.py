from fastapi import APIRouter, Depends, HTTPException, status
from app.security import criar_token_acesso, verificar_senha
from app.dependencies import get_usuario_atual
from app.schemas.user_schemas import LoginRequest, TokenResponse
from app.repositories.user_repository import buscar_usuario_por_email

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# ROTA 1: LOGIN (Gera o Token)
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
