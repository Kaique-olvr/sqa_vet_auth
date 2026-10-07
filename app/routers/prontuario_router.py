from fastapi import APIRouter, Depends
from app.dependencies import exigir_perfil
from app.schemas.user_schemas import PerfilAcesso

'''Rotas de prontuários da clínica.
   Fica separado do auth_router porque não é autenticação: é um recurso do negócio que USA a autenticação.
   Por enquanto serve de exemplo do controle de acesso por perfil (RBAC).
'''

router = APIRouter(prefix="/prontuarios", tags=["Prontuários"])

# ROTA RESTRITA (Apenas Veterinários)
@router.post("")
def criar_prontuario(usuario_logado: dict = Depends(exigir_perfil([PerfilAcesso.VETERINARIO]))):
    # Aqui só chega se for veterinário (qualquer outro perfil recebe 403 no exigir_perfil)
    return {
        "mensagem": "Prontuário criado com sucesso, Doutor(a)!",
        "medico_responsavel": usuario_logado["email"]
    }
