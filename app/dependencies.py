from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import SECRET_KEY, ALGORITHM
from app.schemas.user_schemas import PerfilAcesso

'''O HTTPBearer é uma classe do FastAPI que extrai o token de acesso do cabeçalho da requisição HTTP.

Ele espera receber o token no Header da requisição no formato: "Authorization: Bearer <token_jwt>"
Com auto_error=False ele NÃO responde sozinho quando o header falta (a resposta padrão era "Not authenticated", em inglês).
Assim a gente mesmo devolve o 401 com uma mensagem em português explicando o que fazer.
'''

'''Por que HTTPBearer e não OAuth2PasswordBearer?
O OAuth2PasswordBearer espera que o login seja feito por FORMULÁRIO (campos "username" e "password"),
mas o nosso /auth/login recebe JSON (email e senha). Com o HTTPBearer, o botão "Authorize" do Swagger (/docs)
pede direto o token: basta fazer o login, copiar o "access_token" e colar lá.
'''
bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Cole aqui somente o access_token devolvido pelo POST /auth/login, sem a palavra Bearer e sem aspas."
)

def limpar_token(token: str) -> str:
    '''Corrige os erros mais comuns de quem cola o token no botão "Authorize" do Swagger:
       - colar "Bearer eyJ..." (o Swagger já coloca o Bearer, então ficava "Bearer Bearer eyJ...")
       - colar o token com as aspas que vêm na resposta JSON ("eyJ...")
       Retorna o token limpo em str'''

    token = token.strip().strip('"').strip("'").strip() # Tira espaços e aspas das pontas

    if token.lower().startswith("bearer "): # Remove o "Bearer " que foi colado junto
        token = token[7:].strip()

    return token

def get_usuario_atual(credenciais: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    """
    Função principal que pega o token da requisição, decodifica e retorna os dados do usuário. Se o token for inválido ou não contiver as informações necessárias, uma exceção HTTP 401 é levantada.
    """
    if credenciais is None: # Nenhum token foi enviado no header Authorization
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token não enviado. Faça login em POST /auth/login e cole o access_token no botão Authorize.",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    credenciais_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Credenciais inválidas",
        headers = {"WWW-Authenticate": "Bearer"}
    )

    token = limpar_token(credenciais.credentials) # Pega somente o token, sem a palavra "Bearer" na frente

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
