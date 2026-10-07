from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import SECRET_KEY, ALGORITHM
from app.schemas.user_schemas import PerfilAcesso

'''O HTTPBearer é uma classe do FastAPI que extrai o token de acesso do cabeçalho da requisição HTTP.

Ele espera receber o token no Header da requisição no formato: "Authorization: Bearer <token_jwt>"
Se o header não for enviado (ou não for do tipo Bearer), ele mesmo já responde 401 automaticamente.
'''

'''Por que HTTPBearer e não OAuth2PasswordBearer?
O OAuth2PasswordBearer espera que o login seja feito por FORMULÁRIO (campos "username" e "password"),
mas o nosso /auth/login recebe JSON (email e senha). Com o HTTPBearer, o botão "Authorize" do Swagger (/docs)
pede direto o token: basta fazer o login, copiar o "access_token" e colar lá.
'''
bearer_scheme = HTTPBearer()

def get_usuario_atual(credenciais: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Função principal que pega o token da requisição, decodifica e retorna os dados do usuário. Se o token for inválido ou não contiver as informações necessárias, uma exceção HTTP 401 é levantada.
    """
    credenciais_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Credenciais inválidas",
        headers = {"WWW-Authenticate": "Bearer"}
    )

    token = credenciais.credentials # Pega somente o token, sem a palavra "Bearer" na frente

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # Decodifica o token JWT usando a chave secreta e o algoritmo especificado

        email: str = payload.get("sub") # Pega o email do payload do token
        perfil: str = payload.get("perfil") # Pega o perfil do payload do token

        if email is None or perfil is None:
            raise credenciais_exception

        return {"email": email, "perfil": perfil} # Retorna um dicionário com o email e o perfil do usuário

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token expirado. Faça login novamente.",
            headers = {"WWW-Authenticate": "Bearer"}
        ) # Levanta uma exceção HTTP 401 se o token for expirado

    except jwt.PyJWTError:
        raise credenciais_exception # Levanta a exceção de credenciais inválidas (token adulterado, assinado com outra chave, malformado...)

def exigir_perfil(perfis_permitidos: list[PerfilAcesso]):
    """
    Função auxiliar que verifica se o perfil do usuário está entre os perfis permitidos. Se não estiver, uma exceção HTTP 403 é levantada.
    """
    def verificar_perfil(usuario_atual: dict = Depends(get_usuario_atual)):
        if usuario_atual["perfil"] not in perfis_permitidos:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Acesso negado. Perfil de usuário não autorizado."
            ) # Levanta uma exceção HTTP 403 se o perfil do usuário não estiver entre os perfis permitidos
        return usuario_atual # Retorna os dados do usuário atual se o perfil for permitido
    return verificar_perfil
