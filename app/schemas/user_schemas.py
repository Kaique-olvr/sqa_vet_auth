from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from enum import Enum # enum permite criar um conjunto de valores predefinidos

# o BaseModel é uma classe base do pydantic que valida, converte e exporta os dados informados

LIMITE_BYTES_BCRYPT = 72 # O bcrypt só aceita senhas de até 72 BYTES (não caracteres). Letras com acento (ç, ã, é) ocupam 2 bytes cada

class PerfilAcesso(str, Enum):
    """
    Enumeração de perfis de acesso.
    Define os diferentes níveis de acesso que um usuario pode ter.
    """
    VETERINARIO = "veterinario"
    RECEPCIONISTA = "recepcionista"
    ADM = "adm"
    CLIENTE = "cliente"


def validar_senha(senha: str) -> str:
    '''Regras de senha que o Field(min_length, max_length) sozinho não cobre.
       - O max_length conta CARACTERES, mas o bcrypt limita em BYTES. Uma senha com 72 "ç" passava no schema
         e quebrava a API com erro 500 na hora do hash. Aqui a gente barra antes, com uma mensagem clara.
       - Senha formada só por espaços passava no min_length=8, então também é bloqueada.
       Retorna a senha sem alteração'''

    if not senha.strip(): # Se tirando os espaços não sobra nada, a senha está "em branco"
        raise ValueError("A senha não pode ser formada apenas por espaços.")

    if len(senha.encode('utf-8')) > LIMITE_BYTES_BCRYPT: # Conta o tamanho real em bytes, igual o bcrypt faz
        raise ValueError("A senha passou do limite de 72 bytes. Letras com acento contam como 2, tente uma senha menor.")

    return senha


class ClienteCreate(BaseModel):
    """
    Cadastro público de clientes (RF01).
    Não tem o campo de perfil: todo cadastro feito por aqui vira "cliente" automaticamente (RN04).
    Assim a interface nem oferece a opção de escolher um perfil com mais privilégio.
    """
    email: EmailStr # metodo que valida email com dominios reais
    senha: str = Field(min_length=8, max_length=72, description="Mínimo de 8 caracteres e máximo de 72 bytes (letras com acento contam como 2)")

    # Exemplo que aparece no Swagger. Sem isso ele gera "user@example.com" e "stringst", que parecem dados de verdade
    # extra="forbid" recusa campos a mais (ex: mandar "perfil_acesso": "adm" aqui dá erro em vez de ser ignorado sem aviso)
    model_config = {"extra": "forbid", "json_schema_extra": {"examples": [{"email": "novo.cliente@email.com", "senha": "minhasenha123"}]}}

    _validar_senha = field_validator("senha")(validar_senha) # Aplica as regras extras de senha


class UsuarioCreate(BaseModel):
    """
    Criação e registro de um novo usuario.
    Recebe os dados brutos no pedido de registro e aplica validação de formato e integridade antes de processar.
    """
    email: EmailStr # metodo que valida email com dominios reais
    senha: str = Field(min_length=8, max_length=72) # metodo que faz a validação da senha
    perfil_acesso: PerfilAcesso # define o perfil de acesso do usuario

    _validar_senha = field_validator("senha")(validar_senha) # Aplica as regras extras de senha


class FuncionarioCreate(UsuarioCreate):
    """
    Cadastro de funcionários (RF02), feito somente por um administrador (RN03).
    Herda email, senha e perfil do UsuarioCreate e adiciona o CRMV, que é obrigatório para veterinário (RF03).
    """
    crmv: str | None = Field(default=None, description="Registro no Conselho Regional de Medicina Veterinária. Obrigatório quando o perfil for veterinario")

    model_config = {"json_schema_extra": {"examples": [{"email": "nova.vet@clinica.com", "senha": "senhaforte123", "perfil_acesso": "veterinario", "crmv": "SP-12345"}]}}

    @model_validator(mode="after")
    def validar_regras_funcionario(self):
        '''Valida as regras que dependem de mais de um campo ao mesmo tempo (perfil + CRMV).
           Retorna o próprio objeto se estiver tudo certo'''

        if self.perfil_acesso == PerfilAcesso.CLIENTE: # Cliente tem a rota própria, aqui é só para funcionário
            raise ValueError("Clientes devem ser cadastrados pela rota /auth/cadastro.")

        if self.perfil_acesso == PerfilAcesso.VETERINARIO and not (self.crmv and self.crmv.strip()):
            raise ValueError("O CRMV é obrigatório para o perfil veterinario.")

        return self


class LoginRequest(BaseModel):
    """
    Dados enviados pelo usuario no momento do login.
    Recebe o email e a senha em JSON e valida o formato do email antes de chegar na rota.
    """
    email: EmailStr # metodo que valida o formato do email (se vier invalido, a API responde 422 automaticamente)
    senha: str # senha digitada pelo usuario, sera comparada com o hash salvo

    # Exemplo já com uma conta de demonstração, para o "Try it out" funcionar de primeira
    model_config = {"json_schema_extra": {"examples": [{"email": "vet@clinica.com", "senha": "senha123"}]}}


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


class UsuarioPublico(BaseModel):
    """
    Dados do usuário que podem aparecer numa resposta (nunca a senha nem o hash).
    """
    email: EmailStr
    perfil: PerfilAcesso


class CadastroResponse(BaseModel):
    """
    Resposta devolvida depois de um cadastro bem-sucedido.
    Antes a rota não tinha schema de resposta e o Swagger mostrava só "string" como exemplo.
    """
    mensagem: str
    usuario: UsuarioPublico


class PerfilResponse(BaseModel):
    """
    Resposta da rota /auth/meu-perfil, com os dados que estão dentro do token.
    """
    mensagem: str
    seus_dados: UsuarioPublico


class ErroResponse(BaseModel):
    """
    Formato padrão dos erros da API (401, 403, 400...).
    Usado só para documentar as respostas de erro no Swagger.
    """
    detail: str
