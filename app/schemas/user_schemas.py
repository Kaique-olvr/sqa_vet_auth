from pydantic import BaseModel, EmailStr, Field

# o BaseModel é uma classe base do pydantic que valida, converte e exporta os dados informados
class UsuarioCreate(BaseModel):
    """
    Criação e registro de um novo usuario.
    Recebe os dados brutos no pedido de registro e aplica validação de formato e integridade antes de processar. 
    """
    email: EmailStr # metodo que valida email com dominios reais
    senha: str = Field(min_length=8, max_length=72) # metodo que faz a validação da senha


class UsuarioResponse(BaseModel):
    """
    Resposta com os dados públicos do usuario.
    Define a estrutura devolvida pela API, escondendo qualquer dado sensível.
    """
    id: int
    email: EmailStr