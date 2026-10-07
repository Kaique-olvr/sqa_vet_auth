from fastapi import APIRouter, Depends, HTTPException, status
from app.security import criar_token_acesso, verificar_senha
from app.dependencies import get_usuario_atual
from app.schemas.user_schemas import PerfilAcesso, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# SIMULAÇÃO DE BANCO DE DADOS (Provisório)

# Como ainda não ligamos o BD, vamos usar um dicionário na memória
# para simular dois usuários já cadastrados no sistema (com as senhas já em hash).

# Hash bcrypt REAL da senha "senha123" (gerado com gerar_hash_senha("senha123")).
# Assim o login usa a validação de verdade do bcrypt, igual vai ser quando o BD estiver ligado.
HASH_SENHA_123 = "$2b$12$KehcZRumtIPEg3iUtYi.9.lAehxi.qxbMdVjdCb/d7btwoc1.0Roy"

banco_de_dados_falso = {
    "vet@clinica.com": {
        "email": "vet@clinica.com",
        "senha_hash": HASH_SENHA_123,
        "perfil": PerfilAcesso.VETERINARIO
    },
    "recepcao@clinica.com": {
        "email": "recepcao@clinica.com",
        "senha_hash": HASH_SENHA_123,
        "perfil": PerfilAcesso.RECEPCIONISTA
    }
}

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

    # Busca o usuário no "banco de dados"
    usuario_db = banco_de_dados_falso.get(credenciais.email)

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
