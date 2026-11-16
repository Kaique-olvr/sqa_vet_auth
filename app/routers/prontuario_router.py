from fastapi import APIRouter, Depends
from app.dependencies import exigir_perfil
from app.schemas.user_schemas import PerfilAcesso, ErroResponse

'''Rotas de prontuários da clínica.
   Fica separado do auth_router porque não é autenticação: é um recurso do negócio que USA a autenticação.
   Por enquanto serve de exemplo do controle de acesso por perfil (RBAC).
'''

router = APIRouter(prefix="/prontuarios", tags=["Prontuários"])

# ROTA RESTRITA (Apenas Veterinários)
@router.post(
    "",
    summary="Criar prontuário (somente veterinário)",
    # O cadeado do Swagger só indica que a rota precisa de token, ele não mostra QUAL perfil é aceito.
    # Por isso o perfil exigido fica escrito no resumo e na descrição
    description="Exige token de um usuário com perfil **veterinario** (RN01). "
                "Os outros perfis recebem 403 mesmo estando logados. "
                "Por enquanto a rota não recebe dados do animal: ela só demonstra o controle de acesso.",
    responses={
        401: {"model": ErroResponse, "description": "Token não enviado, inválido ou expirado"},
        403: {"model": ErroResponse, "description": "Usuário logado, mas não é veterinário"}
    }
)
def criar_prontuario(usuario_logado: dict = Depends(exigir_perfil([PerfilAcesso.VETERINARIO]))):
    # Aqui só chega se for veterinário (qualquer outro perfil recebe 403 no exigir_perfil)
    return {
        "mensagem": "Prontuário criado com sucesso, Doutor(a)!",
        "medico_responsavel": usuario_logado["email"]
    }
