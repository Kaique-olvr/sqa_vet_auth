from fastapi import APIRouter, Depends, HTTPException, status
from app.security import criar_token_acesso, verificar_senha, gerar_hash_senha
from app.dependencies import get_usuario_atual, exigir_perfil
from app.schemas.user_schemas import (
    LoginRequest, TokenResponse, ClienteCreate, FuncionarioCreate,
    PerfilAcesso, CadastroResponse, PerfilResponse, ErroResponse
)
from app.repositories.user_repository import buscar_usuario_por_email, salvar_usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])

'''Respostas de erro documentadas no Swagger.
   Sem isso o Swagger marcava o 400, 401 e 403 como "Undocumented" e o usuário só descobria esses erros testando.
'''
ERRO_401 = {401: {"model": ErroResponse, "description": "Token não enviado, inválido ou expirado"}}
ERRO_403 = {403: {"model": ErroResponse, "description": "Usuário logado, mas o perfil não tem permissão para esta rota"}}
ERRO_400_EMAIL = {400: {"model": ErroResponse, "description": "E-mail já cadastrado"}}


def verificar_email_disponivel(email: str):
    '''Bloqueia o cadastro se o e-mail já existir (a busca já ignora maiúsculas/minúsculas).'''

    if buscar_usuario_por_email(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Este email já é utilizado!"
        )


# ROTA 1: Cadastro de clientes (público)
@router.post(
    "/cadastro",
    status_code= status.HTTP_201_CREATED,
    response_model=CadastroResponse,
    responses=ERRO_400_EMAIL,
    summary="Cadastrar cliente",
    description="Rota pública. Cria uma conta com perfil **cliente** (RN04). "
                "Funcionários (veterinário, recepcionista e adm) são cadastrados por um administrador em POST /auth/cadastro/funcionario."
)
def cadastrar_usuario(usuario: ClienteCreate):
    # Verifica se o email ja existe no banco de dados
    verificar_email_disponivel(usuario.email)

    # Faz o hash da senha digitada
    senha_hash = gerar_hash_senha(usuario.senha)

    # Adiciona o novo usuário no banco de dados. O perfil é sempre cliente, ele não vem mais da requisição
    salvo = salvar_usuario({
        "email": usuario.email,
        "senha_hash": senha_hash,
        "perfil": PerfilAcesso.CLIENTE
    })
    return {
        "mensagem": "Cadastro concluído!",
        "usuario" : {"email": salvo["email"], "perfil": salvo["perfil"]}
    }


# ROTA 2: Cadastro de funcionários (somente adm)
@router.post(
    "/cadastro/funcionario",
    status_code= status.HTTP_201_CREATED,
    response_model=CadastroResponse,
    responses={**ERRO_400_EMAIL, **ERRO_401, **ERRO_403},
    summary="Cadastrar funcionário (somente adm)",
    description="Exige token de um usuário com perfil **adm** (RN03). "
                "Perfis aceitos: veterinario, recepcionista e adm. Para **veterinario** o campo crmv é obrigatório (RF03)."
)
def cadastrar_funcionario(funcionario: FuncionarioCreate, usuario_logado: dict = Depends(exigir_perfil([PerfilAcesso.ADM]))):
    # Aqui só chega se quem está logado for adm (os outros perfis recebem 403 no exigir_perfil)
    verificar_email_disponivel(funcionario.email)

    novo_usuario = {
        "email": funcionario.email,
        "senha_hash": gerar_hash_senha(funcionario.senha),
        "perfil": funcionario.perfil_acesso
    }

    if funcionario.perfil_acesso == PerfilAcesso.VETERINARIO: # Só guarda o CRMV de quem é veterinário
        novo_usuario["crmv"] = funcionario.crmv.strip()

    salvo = salvar_usuario(novo_usuario)
    return {
        "mensagem": "Funcionário cadastrado!",
        "usuario" : {"email": salvo["email"], "perfil": salvo["perfil"]}
    }


# ROTA 3: LOGIN (Gera o Token)
@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErroResponse, "description": "E-mail ou senha incorretos"}},
    summary="Fazer login",
    description="Devolve o access_token. Copie só o valor do token (sem aspas) e cole no botão **Authorize** no topo da página."
)
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

# ROTA 4: PERFIL ABERTO (Qualquer um logado)
@router.get(
    "/meu-perfil",
    response_model=PerfilResponse,
    responses=ERRO_401,
    summary="Ver meu perfil",
    description="Qualquer usuário logado. Mostra o e-mail e o perfil que estão dentro do token."
)
def ver_perfil(usuario_logado: dict = Depends(get_usuario_atual)):
    # Aqui chega se o get_usuario_atual passou sem dar erro no token
    return {
        "mensagem": "Acesso Liberado!",
        "seus_dados": usuario_logado
    }
