from pydantic import BaseModel, EmailStr, Field
from enum import Enum # enum permite criar um conjunto de valores predefinidos

# o BaseModel é uma classe base do pydantic que valida, converte e exporta os dados informados

class PerfilAcesso(str, Enum):
    """
    Enumeração de perfis de acesso.
    Define os diferentes níveis de acesso que um usuario pode ter.
    """
    VETERINARIO = "veterinario"
    RECEPCIONISTA = "recepcionista"
    ADM = "adm"
    CLIENTE = "cliente"

class UsuarioCreate(BaseModel):
    """
    Criação e registro de um novo usuario.
    Recebe os dados brutos no pedido de registro e aplica validação de formato e integridade antes de processar. 
    """
    email: EmailStr # metodo que valida email com dominios reais
    senha: str = Field(min_length=8, max_length=72) # metodo que faz a validação da senha
    perfil_acesso: PerfilAcesso # define o perfil de acesso do usuario


class LoginRequest(BaseModel):
    """
    Dados enviados pelo usuario no momento do login.
    Recebe o email e a senha em JSON e valida o formato do email antes de chegar na rota.
    """
    email: EmailStr # metodo que valida o formato do email (se vier invalido, a API responde 422 automaticamente)
    senha: str # senha digitada pelo usuario, sera comparada com o hash salvo


class TokenResponse(BaseModel):
    """
    Resposta devolvida pela API apos um login bem-sucedido.
    Segue o padrao do OAuth2: o token em si e o tipo dele ("bearer").
    """
    access_token: str # token JWT gerado no login
    token_type: str = "bearer" # tipo do token, o cliente deve envia-lo no header "Authorization: Bearer <token>"


class UsuarioResponse(BaseModel):
    """
    Resposta com os dados públicos do usuario.
    Define a estrutura devolvida pela API, escondendo qualquer dado sensível.
    """
    id: int
    email: EmailStr
    perfil_acesso: PerfilAcesso
