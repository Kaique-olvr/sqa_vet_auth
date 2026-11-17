from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers import auth_router, prontuario_router  # Importa as rotas

'''Texto que aparece no topo do Swagger (/docs).
   Explica o passo a passo do login para quem abre a documentação pela primeira vez.
'''
DESCRICAO_API = """
Microsserviço de autenticação e controle de acesso por perfil (RBAC) da clínica veterinária.

**Como testar por aqui:**
1. Em **POST /auth/login**, clique em *Try it out* e depois em *Execute* (o exemplo já vem com a conta do veterinário).
2. Copie só o valor do `access_token`, sem as aspas.
3. Clique em **Authorize**, cole o token e confirme. Não precisa escrever *Bearer*.
4. O cadeado indica que a rota precisa de login. O perfil exigido está escrito no nome de cada rota.

Contas de demonstração (senha `senha123`): vet@clinica.com, recepcao@clinica.com, cliente@clinica.com e adm@clinica.com.
"""

app = FastAPI(title="SQA Vet Auth API", description=DESCRICAO_API)

# Conecta as rotas na aplicação principal
app.include_router(auth_router.router) # Rotas de autenticação (/auth/cadastro, /auth/login, /auth/meu-perfil)
app.include_router(prontuario_router.router) # Rotas de prontuários (/prontuarios), restritas por perfil


def traduzir_erro(erro: dict) -> str:
    '''Troca a mensagem padrão do Pydantic (em inglês e bem técnica) por uma frase em português.
       Recebe um item da lista de erros do Pydantic e retorna a mensagem em str'''

    tipo = erro.get("type", "")
    campo = erro.get("loc", [""])[-1] # Último item do "loc" é o nome do campo (ex: ["body", "senha"] -> "senha")
    contexto = erro.get("ctx", {})

    if tipo == "missing":
        return "Campo obrigatório."
    if tipo == "string_too_short":
        return f"Precisa ter no mínimo {contexto.get('min_length')} caracteres."
    if tipo == "string_too_long":
        return f"Pode ter no máximo {contexto.get('max_length')} caracteres."
    if tipo == "enum":
        return f"Valor inválido. Opções aceitas: {contexto.get('expected')}."
    if tipo == "extra_forbidden":
        return "Campo não permitido nesta rota."
    if tipo == "json_invalid":
        return "O JSON enviado está mal formatado. Confira vírgulas, aspas e chaves."
    if tipo == "value_error" and campo == "email":
        return "E-mail inválido. Use o formato nome@dominio.com."
    if tipo == "value_error":
        return str(erro.get("msg", "")).removeprefix("Value error, ") # Nossas mensagens dos validators já estão em português

    return erro.get("msg", "Valor inválido.") # Qualquer outro caso continua com a mensagem original


@app.exception_handler(RequestValidationError)
async def erro_de_validacao(request: Request, exc: RequestValidationError):
    '''Mantém o status 422 e o mesmo formato de resposta (detail com loc, msg e type),
       só que com o "msg" em português. Assim o que o Swagger documenta continua batendo com a resposta real.'''

    erros = []
    for erro in exc.errors():
        erros.append({
            "loc": erro.get("loc"),
            "msg": traduzir_erro(erro),
            "type": erro.get("type")
        }) # O campo "input" não é devolvido para não ecoar a senha digitada na resposta

    return JSONResponse(status_code=422, content={"detail": erros})


@app.get("/", tags=["Status"], summary="Verificar se a API está no ar")
def home():
    return {"status": "API da Clínica Veterinária rodando!"}
